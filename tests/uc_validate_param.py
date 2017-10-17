"""Use case: playbook parameter validation

Flow:
1. search for the project that contains the playbook
2. create an inventory w/host
3. create a template to execute the playbook w/the options
4. launch the playbook
5. delete the template
6. delete the inventory

Prerequisites to using this script:

1. Must have a Carbon organization.
2. Must have a carbon-user defined in AWX to be a Admin user in the Carbon
   organization.
3. Must have the following projects created (as Admin and give user permission
   to carbon-user):

   1. SCM: https://github.com/rywillia/awx-test
      Description:
      {"git_url":"https://raw.githubusercontent.com/rywillia/awx-test/master/"}

   2. SCM: https://github.com/vi-patel/test-playbooks
      Description:
      {"git_url":"https://raw.githubusercontent.com/vi-patel/test-playbooks/master/"}


This use case will demonstrate using tower-cli client library combined
with the REST api to perform the following actions with Ansible AWX:

Scenario 1: successful validation of mandatory params, so the playbook
            can be executed.
Scenario 2: successful validation, w/no params to be validated,
            so the playbook execution will occur.
Scenario 3: unsuccessful validation, so there is an error returned and the
            playbook is never executed.
Scenario 4: no validation is done, because there is no description file, so the
            playbook is executed as is.

"""
import sys
from logging import getLogger
from time import sleep
import requests
import yaml
import uuid
from urlparse import urljoin
import ast
from awx import Awx
from awx.awx import __awx_name__

LOG = getLogger(__awx_name__)

# commonly used variables
# should already be created
ORGANIZATION = 'Carbon'
CREDENTIAL_PREFIX = 'cred_'
SSH_KEY_LOCATION='<location to ssh_key>'
INVENTORY_PREFIX = 'inv_'
PROJECT_PREFIX = 'proj_'
JOB_TEMPLATE_PREFIX = 'job_'
HOST = '<machine_to_test>'
TOWER_USER = 'carbon-user'
TOWER_PASSWORD = 'carbon-user'
TOWER_URL = 'http://localhost'

# playbook and variables passed by the user
# Scenario 1
PLAYBOOK = 'var_test.yml'
vars = {'hello':'just_a_test',
        'hello2':'same_test'}

# # Scenario 2
# PLAYBOOK = 'system-release.yml'
# vars = {}

# # Scenario 3, failed validation
# PLAYBOOK = 'var_test.yml'
# vars = {'hello':'just_a_test'}
#
# # Scenario 4
# # no description, skipping validation
# PLAYBOOK = 'playbooks/system-release.yml'
# vars = {}


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

inventory = INVENTORY_PREFIX + scenario_guid
job_template = JOB_TEMPLATE_PREFIX + scenario_guid
credential = CREDENTIAL_PREFIX + scenario_guid

# create awx object as carbon-user
awx_user = Awx(username="carbon-user", password="carbon-user")

# query to see if project exists
found_project = get_playbook_project(awx_user, TOWER_URL,
                                     TOWER_USER, TOWER_PASSWORD,
                                     PLAYBOOK)
if found_project:
    project = awx_user.project.get(found_project)
else:
    LOG.error("The playbook was not found")
    sys.exit(1)


proj_desc = project['description']
project_dict = ast.literal_eval(proj_desc)
playbook_url = urljoin(project_dict["git_url"], PLAYBOOK)
split_playbook = PLAYBOOK.rsplit(".", 1)
playbook_desc = split_playbook[0] + "_desc." + split_playbook[1]
playbook_desc_url =urljoin(project_dict["git_url"], playbook_desc)


r = requests.get(playbook_desc_url)

if "404" in r.content:
    LOG.info("skipping validation")
else:
    desc_dict = yaml.load(r.content)

    LOG.debug("Mandatory playbook vars: {}".format(desc_dict["required"]))

    for required_var in desc_dict["required"]:
        # make sure the required var is not None
        if required_var:
            if not(required_var in vars and vars[required_var]):
                LOG.error("validation failed: Required variable {} is not set," 
                " can't continue".format(required_var))
                sys.exit(1)
        else:
            LOG.debug("no required vars")

    LOG.info("successful parameter validation")


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
    project=project["name"],
    playbook=PLAYBOOK,
    credential=credential,
    extra_vars=[vars]
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
    sleep(10) # wait for 10 seconds for the job to be successfully cancelled

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
    project=project['name']
)

# delete inventory
awx_user.inventory.delete(name=inventory)

# delete credential
awx_user.credential.delete(name=credential, kind="ssh")
