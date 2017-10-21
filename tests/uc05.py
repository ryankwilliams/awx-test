"""Use case 05.

This use case will demonstrate using tower-cli client library to perform the
following actions with Ansible AWX:

    1. Create an organization.
    2. Create an inventory.
    3. Create a host.
    4. Create a project from scm - git.
    5. Create a template to install package on system.
    6. Create a template to remove package on system.
    7. Run template(s).
    8. Delete template(s).
    9. Delete project.
    10. Delete organization (which deletes inventories and hosts associated).
"""
from logging import getLogger
from time import sleep

from awx import Awx
from awx.awx import __awx_name__

LOG = getLogger(__awx_name__)

# commonly used variables
ORGANIZATION = 'demo_organization01'
CREDENTIAL = 'Demo Credential'
INVENTORY = 'demo_inventory01'
HOST = 'localhost'
PROJECT = 'demo_project01'
JOB_TEMPLATE_01 = 'package_install'
JOB_TEMPLATE_02 = 'package_remove'

# create awx object
awx = Awx()

# create organization
awx.organization.create(
    name=ORGANIZATION,
    description='A demo organization for testing purposes.'
)

# create inventory
awx.inventory.create(
    name=INVENTORY,
    organization=ORGANIZATION,
    description='A demo inventory for testing purposes.'
)

# create a host
awx.host.create(
    name=HOST,
    inventory=INVENTORY,
    variables=dict(ansible_connection='local')
)

# create a project
awx.project.create_scm_project(
    name=PROJECT,
    description='A demo project for testing purposes.',
    organization=ORGANIZATION,
    scm_type='git',
    url='https://github.com/rywillia/awx-test'
)

sleep(15)

# create template 01, prompt for variables at run time
awx.job_template.create(
    name=JOB_TEMPLATE_01,
    description='Template to install package.',
    job_type='run',
    inventory=INVENTORY,
    project=PROJECT,
    playbook='playbooks/package_install.yml',
    credential=CREDENTIAL,
    ask_variables_on_launch=True
)

# create template 02, variables static to template
awx.job_template.create(
    name=JOB_TEMPLATE_02,
    description='Template to remove package.',
    job_type='run',
    inventory=INVENTORY,
    project=PROJECT,
    playbook='playbooks/package_remove.yml',
    credential=CREDENTIAL,
    extra_vars=[{'package': 'tree'}]
)

# run template 01
results = awx.job.launch(
    name=JOB_TEMPLATE_01,
    reason='Install a package.',
    extra_vars=[{'package': 'tree'}]
)

job_id = results["id"]

try:
    job_output = awx.job.monitor(job_id, interval=1, timeout=60)
    LOG.info(job_output)
except Exception as e:
    if "aborted due to timeout" in e.message:
        LOG.error("reached the timeout period, cancel the job")
    else:
        LOG.error("Error occurred during job monitoring: {}".format(e.message))
    cancelled_job = awx.job.cancel(job_id)
    LOG.error(cancelled_job)
    LOG.debug("Waiting 10 seconds for the job to be cancelled")
    sleep(10)  # wait for 10 seconds for the job to be successfully cancelled

status = awx.job.status(job_id)
if status['status'] == 'successful':
    LOG.info('Playbook execution was successful')
elif status['status'] == 'failed':
    LOG.error('Playbook execution failed')

LOG.info("Results: {}".format(status))
LOG.info('Output: {}'.format(awx.job.stdout(job_id)))

# run template 02
results = awx.job.launch(
    name=JOB_TEMPLATE_02,
    reason='Remove a installed pacakage.'
)

job_id = results["id"]

try:
    job_output = awx.job.monitor(job_id, interval=1, timeout=60)
    LOG.info(job_output)
except Exception as e:
    if "aborted due to timeout" in e.message:
        LOG.error("reached the timeout period, cancel the job")
    else:
        LOG.error("Error occurred during job monitoring: {}".format(e.message))
    cancelled_job = awx.job.cancel(job_id)
    LOG.error(cancelled_job)
    LOG.debug("Waiting 10 seconds for the job to be cancelled")
    sleep(10)  # wait for 10 seconds for the job to be successfully cancelled

status = awx.job.status(job_id)
if status['status'] == 'successful':
    LOG.info('Playbook execution was successful')
elif status['status'] == 'failed':
    LOG.error('Playbook execution failed')

LOG.info("Results: {}".format(status))
LOG.info('Output: {}'.format(awx.job.stdout(job_id)))

# delete templates
for template in [JOB_TEMPLATE_01, JOB_TEMPLATE_02]:
    awx.job_template.delete(
        name=template,
        project=PROJECT
    )

# delete project
awx.project.delete(name=PROJECT)

# delete organization
awx.organization.delete(name=ORGANIZATION)
