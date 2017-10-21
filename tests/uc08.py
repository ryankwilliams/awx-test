"""Use case 08.

This use case will demonstrate using tower-cli client library to perform the
following actions with Ansible AWX, developing a workflow for using AWX
for orchestration as the backend:

Prerequisites:
  Organization created that has access to common projects
  created organization: Carbon
  created project w/common playbooks: Common_playbooks ->
          created by admin, and carbon-user has permissions to use.
  Note: All common projects should have Update on Launch selected.

  created user: carbon-user, normal user, and add
                admin permissions for Carbon organization and
                has user permission for the Common_playbooks project.

    1. As carbon-user, create an inventory.
    2. As carbon-user, create a credential
    3. As carbon-user, create a host.
    4. As carbon-user, create a project from scm - git, if necessary
    5. As carbon-user, create a template based on project just created.
    6. As carbon-user, run template.
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
from urlparse import urljoin

import requests

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
JOB_TEMPLATE_PREFIX = 'job'
HOST = '<machine_to_test>'
PLAYBOOK = 'playbooks/system-release.yml'
TOWER_USER = 'carbon-user'
TOWER_PASSWORD = 'carbon-user'
TOWER_URL = 'http://localhost'


def get_playbook_project(awx, url, user, password, playbook_name):
    # function that searches all playbooks and returns the project
    # that contains the playbook if exists.

    # get all projects
    all_projects = awx.project.projects
    all_playbooks = []

    # get a dictionary of projects and playbooks
    project_playbooks = {}

    for proj in all_projects["results"]:
        playbook_path = proj["related"]["playbooks"]
        full_url = urljoin(url, playbook_path)
        r = requests.get(full_url, auth=(user, password))
        all_playbooks.extend(r.json())
        project_playbooks[proj["name"]] = r.json()

    if playbook_name not in all_playbooks:
        return None
    else:
        for project in project_playbooks:
            if playbook_name in project_playbooks[project]:
                return project


# variable to track if the project needs to be deleted
del_project = False

# get a guid for the scenario
scenario_guid = uuid.uuid4().hex
scenario_guid = scenario_guid[:8]

# create awx object as carbon-user
awx_user = Awx(username="carbon-user", password="carbon-user")

inventory = INVENTORY_PREFIX + scenario_guid
project = PROJECT_PREFIX + scenario_guid
job_template = JOB_TEMPLATE_PREFIX + scenario_guid
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

# query to see if project exists
found_project = get_playbook_project(awx_user, TOWER_URL,
                                     TOWER_USER, TOWER_PASSWORD,
                                     PLAYBOOK)

if found_project:
    project = found_project
else:
    # create a project with the local git
    # create a project
    awx_user.project.create_scm_project(
        name=project,
        description='A demo project for testing purposes.',
        organization=ORGANIZATION,
        scm_type='git',
        url='https://github.com/rywillia/awx-test'
    )
    del_project = True

sleep(15)

# create credentials
awx_user.credential.create_ssh_credential(credential,
                                          ORGANIZATION,
                                          SSH_KEY_LOCATION)

# create template
awx_user.job_template.create(
    name=job_template,
    description='A demo job template for testing purposes.',
    job_type='run',
    inventory=inventory,
    project=project,
    playbook=PLAYBOOK,
    credential=credential
)

# run template
results = awx_user.job.launch(
    name=job_template,
    reason='A demo job launch for testing purposes.'
)

job_id = results["id"]

# wait for the job is done and gather the output
try:
    job_output = awx_user.job.monitor(job_id, interval=1, timeout=60)
    LOG.debug(job_output)
except Exception as e:
    if "aborted due to timeout" in e.message:
        LOG.error("reached the timeout period, cancel the job")
    else:
        LOG.error("Error occurred during job monitoring: {}".format(e.message))
    cancelled_job = awx_user.job.cancel(job_id)
    LOG.error(cancelled_job)
    LOG.debug("Waiting 10 seconds for the job to be cancelled")
    sleep(10)  # wait for 10 seconds for the job to be successfully cancelled

status = awx_user.job.status(job_id)
if status['status'] == 'successful':
    LOG.info('Playbook execution was successful')
elif status['status'] == 'failed':
    LOG.error('Playbook execution failed')

LOG.info("Results: {}".format(status))
LOG.info('Output: {}'.format(awx_user.job.stdout(job_id)))

# delete template
awx_user.job_template.delete(
    name=job_template,
    project=project
)

# delete project, if user created
if del_project:
    awx_user.project.delete(name=project)

# delete inventory
awx_user.inventory.delete(name=inventory)

# delete credential
awx_user.credential.delete(name=credential, kind="ssh")
