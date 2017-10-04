"""Use case 02.

This use case will demonstrate using tower-cli client library to perform
the following actions with Ansible AWX:

    1. Create a user
    2. Delete a user
"""
from logging import getLogger
from pprint import pformat

from awx import Awx
from awx.awx import __awx_name__

LOG = getLogger(__awx_name__)

# create awx objects
awx = Awx()

# create user
awx.user.create(
    'user01',
    'password',
    'user01@test.com',
    'User01',
    'User01'
)

# list users
for user in awx.user.users['results']:
    LOG.info(pformat(dict(user), indent=4))

# delete user
awx.user.delete('user01')
