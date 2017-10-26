"""Use case 09.

This use case will demonstrate using tower-cli client library to perform the
following actions with Ansible AWX:

    1. Create an organization.
    2. Create an inventory.
    3. Create a host.
    4. Create a project from scm - git.
    5. Create a template to install package on system.
    6. Create a template to remove package on system.
    7. Create a notification template 1 Email
    8. Create a notification template 2 IRC
    9. Associate notification template 1 to job template 1
    10. Associate notification template 1 and 2 to job templage 2
    11. Run template(s).
    12. Delete template(s).
    13. Delete notificatin template(s).
    14. Delete project.
    15. Delete organization (which deletes inventories and hosts associated).
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

NOTIFICATION_TEMPLATE_01 = 'Email-Notification'
NOTIFICATION_DESCRIPTION_01 = 'Email Notification'
NOTIFICATION_TEMPLATE_02 = 'IRC-Notificatoin'
NOTIFICATION_DESCRIPTION_02 = 'IRC Notification'
NOTIFICATION_TYPE_01 = 'email'
NOTIFICATION_TYPE_02 = 'irc'
NOTIFICATION_CONFIGURATION_FILE = 'email.json'
NOTIFICATION_CONFIGURATION = '{"server":"<irc_host_url>",' \
                             '"password":"",' \
                             '"targets":["<list_users_channels>"],' \
                             '"nickname":"<nick name>",' \
                             '"port":<port>,' \
                             '"use_ssl":false}'

NOTIFICATION_STATUS_ERROR = 'error'
NOTIFICATION_STATUS_SUCCESS = 'success'
NOTIFICATION_STATUS_ANY = 'any'

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

# create notification template 01 by file
with open(NOTIFICATION_CONFIGURATION_FILE) as data_file:
    awx.notification_template.create(
        name=NOTIFICATION_TEMPLATE_01,
        notification_type=NOTIFICATION_TYPE_01,
        description=NOTIFICATION_DESCRIPTION_01,
        organization=ORGANIZATION,
        notification_configuration=(data_file)
    )

# create notification template 02 by configuration var
awx.notification_template.create(
    name=NOTIFICATION_TEMPLATE_02,
    notification_type=NOTIFICATION_TYPE_02,
    description=NOTIFICATION_DESCRIPTION_02,
    organization=ORGANIZATION,
    notification_configuration=NOTIFICATION_CONFIGURATION
)

# Associate Notification 1 template to job 1
awx.job_template.associate_notification_template(
    job_template=JOB_TEMPLATE_01,
    notification_template=NOTIFICATION_TEMPLATE_01,
    status=NOTIFICATION_STATUS_ANY)

# Associate Notification 1 and 2 templates to job 2
awx.job_template.associate_notification_template(
    job_template=JOB_TEMPLATE_02,
    notification_template=NOTIFICATION_TEMPLATE_01,
    status=NOTIFICATION_STATUS_SUCCESS)

awx.job_template.associate_notification_template(
    job_template=JOB_TEMPLATE_02,
    notification_template=NOTIFICATION_TEMPLATE_02,
    status=NOTIFICATION_STATUS_SUCCESS)

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

# delete notification template 1
awx.notification_template.delete(
    name=NOTIFICATION_TEMPLATE_01,
    notification_type="email",
    organization=ORGANIZATION
)

# delete notification template 2
awx.notification_template.delete(
    name=NOTIFICATION_TEMPLATE_02,
    notification_type="irc",
    organization=ORGANIZATION
)

# delete project
awx.project.delete(name=PROJECT)

# delete organization
awx.organization.delete(name=ORGANIZATION)
