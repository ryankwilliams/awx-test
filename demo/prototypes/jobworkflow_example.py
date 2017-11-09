"""

This use case will demonstrate using tower-cli client library to perform the
following actions with Ansible AWX, developing a workflow for executing a
workflow:

Prerequisites:
  Organization created that has access to common projects
  created organization: Carbon
  created project w/common playbooks: Common_playbooks ->
          created by admin, and carbon-user has permissions to use.
  2 Projects are required:
    * scm: https://github.com/vi-patel/test-playbooks.git
    * scm: https://github.com/rywillia/awx-test.git

  Note: All common projects should have Update on Launch selected.

  created user: carbon-user, normal user, and add
                admin permissions for Carbon organization and
                has user permission for both projects mentioned above.

    1. As user carbon, create an inventory.
    2. As user carbon, create a credential
    3. As user carbon, create a host.
    4. As user carbon, create a project from scm - git, if necessary
    5. As user carbon, create all templates required for the run.
    6. As user carbon, run workflow template.
    7. Delete the template.
    8. Delete the inventory
    9. Delete the project if it is not a common project
    10. Delete the credential

  Note: issue found in this workflow: after the workflow is complete,
  carbon-user cannot see the job (even though the user created the template
  and launched the job).
"""
import uuid
from logging import getLogger
from time import sleep

from awx import Awx
from awx.awx import __awx_name__

LOG = getLogger(__awx_name__)

# commonly used variables
# should already be created
ORGANIZATION = 'Carbon'
CREDENTIAL_PREFIX = 'cred_'
SSH_KEY_LOCATION = '<location to ssh_key>'
INVENTORY_PREFIX = 'inv_'
PROJECT_PREFIX = 'proj_'
HOST = '<machine_to_test>'
playbookdict = {'SYS_RELEASE_common': {
    'playbook_name': 'playbooks/system-release.yml',
    'scm': 'https://github.com/rywillia/awx-test.git'},
               'SYS_RELEASE_vipatel': {
    'playbook_name': 'system-release.yml',
    'scm': 'https://github.com/vi-patel/test-playbooks.git'},
               'force_failure': {
    'playbook_name': 'var_test.yml',
    'scm': 'https://github.com/vi-patel/test-playbooks.git'}}
SCHEMA_LOC = "workflow_schema.yml"
WORKFLOW_JOB = "workflow_test"
WORKFLOW_DESC = "testing a workflow"


# variable to track if the project needs to be deleted
del_project = False

# get a guid for the scenario
scenario_guid = uuid.uuid4().hex
scenario_guid = scenario_guid[:8]

# create awx object as carbon-user
awx_user = Awx(username="carbon-user", password="carbon-user")

inventory = INVENTORY_PREFIX + scenario_guid
project = PROJECT_PREFIX + scenario_guid
credential = CREDENTIAL_PREFIX + scenario_guid

# create inventory
awx_user.inventory.create(
    name=inventory,
    organization=ORGANIZATION,
    description='A demo inventory for testing purposes.'
)

# create a host and add to inventory
awx_user.host.create(
    name=HOST,
    inventory=inventory,
    variables=dict(ansible_connection='local')
)

for index, job_template in enumerate(playbookdict):
    # query to see if project exists
    found_project = awx_user.project.get_playbook_project(
        playbookdict[job_template]['playbook_name'])

    if found_project:
        project = found_project
    else:
        # create a project with the local git
        # create a project
        awx_user.project.create_scm_project(
            name=project + (str(index)),
            description='A demo project for testing purposes.',
            organization=ORGANIZATION,
            scm_type='git',
            url=playbookdict[job_template]['scm']
        )
        del_project = True

    sleep(15)

    # create credentials
    awx_user.credential.create_ssh_credential(credential,
                                              ORGANIZATION,
                                              SSH_KEY_LOCATION)

    try:
        # create template
        awx_user.job_template.create(
            name=job_template,
            description='A demo job template for testing purposes.',
            job_type='run',
            inventory=inventory,
            project=project,
            playbook=playbookdict[job_template]['playbook_name'],
            credential=credential
        )
    except Exception as e:
        if "already exists" in e.message:
            LOG.warn("Template already exists, will not create, CONTINUING")
        else:
            LOG.error(e.message)
            exit(1)


try:
    # create a workflow
    awx_user.workflow.create(WORKFLOW_JOB, WORKFLOW_DESC, ORGANIZATION)
except Exception as e:
    if "already exists" in e.message:
        LOG.warn("Template already exists, will not create, CONTINUING")
    else:
        LOG.error(e.message)
        exit(1)

# upload the schema to the workflow
# TODO: we will have to determine how to create this schema
awx_user.workflow.upload_schema(WORKFLOW_JOB, SCHEMA_LOC)

results = awx_user.workflow_job.launch(WORKFLOW_JOB)

workflow_job_id = results["id"]

# wait for the job is done and gather the output
try:
    job_output = awx_user.workflow_job.monitor(workflow_job_id)
except Exception as e:
    if "aborted due to timeout" in e.message:
        LOG.error("reached the timeout period, cancel the job")
    else:
        LOG.error("Error during job monitoring: {}".format(e.message))
    cancelled_job = awx_user.workflow_job.cancel(workflow_job_id)
    LOG.error(cancelled_job)
    LOG.debug("Waiting 10 seconds for the job to be cancelled")
    sleep(10)  # wait for 10 seconds for the job to be successfully cancelled
    exit(1)

# get the list of jobs from the executed workflow
joblist = awx_user.workflow_job.get_jobs(workflow_job_id)

job_result_list = []

# Get the status of the individual jobs executed
for job_id in joblist:
    status = awx_user.job.status(job_id)
    job_result_list.append(status["status"])
    if status['status'] == 'successful':
        LOG.info('Playbook execution was successful')
    elif status['status'] == 'failed':
        LOG.error('Playbook execution failed')

    LOG.info("Results: {}".format(status))
    LOG.info('Output: {}'.format(awx_user.job.stdout(job_id)))

# Correlate the final results
if "failed" in job_result_list:
    LOG.error("Overall workflow execution is a failure.")
else:
    LOG.info("Overall workflow execution is a success.")

# delete inventory
awx_user.inventory.delete(name=inventory)

# delete credential
awx_user.credential.delete(name=credential, kind="ssh")
