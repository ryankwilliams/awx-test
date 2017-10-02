"""Use case 01.

This use case will demonstrate using tower-cli client library to perform
the following actions with Ansible AWX:

    1. Create a new organization
    2. Create a new inventory
    3. Create a new host (adding to previously created inventory)
    4. Run a ad hoc ping command on host
    5. Delete host
    6. Delete inventory
    7. Delete organization
"""
from time import sleep

from awx import Awx

# global variables
CREDENTIAL = 'Demo Credential'
HOST = 'localhost'
INVENTORY = 'uc01'
ORGANIZATION = 'uc01'

# create awx objects
awx = Awx()

# create organization
awx.organization.create(ORGANIZATION)

# create inventory
awx.inventory.create(INVENTORY, ORGANIZATION)

# create host
awx.host.create(
    HOST,
    INVENTORY,
    dict(ansible_connection='local')
)

# run ad hoc command (ping host)
results = awx.ad_hoc.launch(
    'run',
    'ping',
    INVENTORY,
    CREDENTIAL
)

job_id = results['id']

while True:
    results = awx.ad_hoc.get(job_id)
    if results['status'] == 'successful':
        print(awx.ad_hoc.stdout(job_id))
        break
    sleep(2)

sleep(10)

# delete host
awx.host.delete(HOST, INVENTORY)

# delete inventory
awx.inventory.delete(INVENTORY)

# delete organization
awx.organization.delete(ORGANIZATION)
