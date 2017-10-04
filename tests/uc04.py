"""Use case 04.

This use case will demonstrate using tower-cli client library to perform the
following actions with Ansible AWX:

    1. Create an organization.
    2. Create an inventory.
    3. Create a credential
    3. Create a host.
    4. Create a project from scm - git.
    5. Create a template based on project just created.
    6. Run template.
    7. Delete template.
    8. Delete project.
    9. Delete organization (which deletes inventories and hosts associated).
"""
from time import sleep

from awx import Awx

# commonly used variables
ORGANIZATION = 'demo_organization01'
CREDENTIAL = 'Demo Credential'
INVENTORY = 'demo_inventory01'
HOST = 'localhost'
PROJECT = 'demo_project01'
JOB_TEMPLATE = 'demo_template01'

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

# create template
awx.job_template.create(
    name=JOB_TEMPLATE,
    description='A demo job template for testing purposes.',
    job_type='run',
    inventory=INVENTORY,
    project=PROJECT,
    playbook='playbooks/system-release.yml',
    credential=CREDENTIAL
)

# run template
results = awx.job.launch(
    name=JOB_TEMPLATE,
    reason='A demo job launch for testing purposes.'
)

job_id = results["id"]

# wait for the job is done and gather the output
try:
    job_output = awx.job.monitor(job_id, interval=1, timeout=60)
    print job_output
except Exception as e:
    if "aborted due to timeout" in e.message:
        print "reached the timeout period, cancel the job"
    else:
        print "Error occurred during job monitoring: {}".format(e.message)
    cancelled_job = awx.job.cancel(job_id)
    print cancelled_job
    print "Waiting 10 seconds for the job to be cancelled"
    sleep(10) # wait for 10 seconds for the job to be successfully cancelled

status = awx.job.status(job_id)
if status['status'] == 'successful':
    print 'Playbook execution was successful'
elif status['status'] == 'failed':
    print 'Playbook execution failed'

print "Results: {}".format(status)
print 'Output: {}'.format(awx.job.stdout(job_id))

# delete template
awx.job_template.delete(
    name=JOB_TEMPLATE,
    project=PROJECT
)

# delete project
awx.project.delete(name=PROJECT)

# delete organization
awx.organization.delete(name=ORGANIZATION)
