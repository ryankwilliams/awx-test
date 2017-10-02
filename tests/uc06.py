"""Use case 06.

This use case will demonstrate using tower-cli client library to perform
a possible workflow using the following actions with Ansible AWX:

    1. Check if Organization exists, create if it does not
    2. Check if the Team exists, create if it does not
    3. Check if User exists, create if it does not
    4. As the Admin, check if the Project exists, create if it does not
    5. As the Admin, give permission to the user to the Project
    6. As the Admin, check if Credentials exist, create if it does not(ssh key)
    7. As the Admin, give permission to the user to the Credential
    8. As the Admin, check if the Inventory exists, create if it does not
    9. As the Admin, give permission to the user to the Inventory
    10. As the User, check if the template exists, create if it does not
    11. As the User, launch the template
"""
from awx import Awx
import time

# Got a request from user test2, to execute system-release.yml, which exists
# in the NewProj project, using the sshkey for creds

USER="uc06"
USER_PASSWORD="uc06"
USER_EMAIL="uc06@test.com"
PLAYBOOK="playbooks/system-release.yml"
PLAYBOOK_VARS=None
CREDENTIAL_NAME="uc06_creds"
SSH_KEY_LOCATION="<location to ssh_key>"
ORGANIZATION="Default"
TEAM="QA"

INVENTORY_NAME="uc06test"
INVENTORY_HOSTNAME="<add_machine_hostname>"

TEMPLATE_NAME="Get_System_Release"
TEMPLATE_TYPE="run"
TEMPLATE_RUN_DESCRIPTION="Getting System Release"

# there should be a query here to see if the playbook exists, which returned
# yes it exist with the following project settings
PROJECT="uc06_proj"
PROJECT_TYPE="git"
PROJECT_URL="http://github.com/rywillia/awx-test"

# create awx objects, one for admin and one for a test user
awx = Awx()

# create organization
try:
    awx.organization.create(
        name=ORGANIZATION,
        description='A demo organization for testing purposes.'
    )
except Exception as e:
    if "already exists" in e.message :
        print "Organization Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

# create the team
try:
    awx.team.create(
        TEAM, ORGANIZATION
    )
except Exception as e:
    if "already exists" in e.message:
        print "Team Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

# verify the user exists, create if user doesn't exist
# create user
# name, password, email, first_name, last_name,
try:
    awx.user.create(
        USER,
        USER_PASSWORD,
        USER_EMAIL,
        USER,
        ''
    )
except Exception as e:
    if "already exists" in e.message :
        print "User Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

# Add the user to the team
awx.team.associate(TEAM, USER)
# Add the user to the Organization -- Not sure why this doesn't happen
# automatically, when addin the team
awx.organization.associate(ORGANIZATION, USER)

# create awx object as user
awx_user = Awx(username=USER, password=USER_PASSWORD)


# do some query here to see what playbooks exists in what project
# should return New_Proj2 for this example

#Verify New_Proj2 exists and the user has access to it
try:
    awx.project.create_scm_project(
        PROJECT,
        "",
        ORGANIZATION,
        PROJECT_TYPE,
        PROJECT_URL,
        # update on launch set to true to make sure latest playbook is run
        update_on_launch=True
    )
except Exception as e:
    if "already exists" in e.message :
        print "Project Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

# give the user permissions to the project
try:
    awx.role.grant(user=USER, project=PROJECT)
except Exception as e:
    if "already a member" in e.message :
        print "User Already Has Correct Permissions, CONTINUING"
        pass
    else:
        print e.message
        exit(1)


# test credential creation ssh key
# name, organization, ssh_key_file
try:
    awx.credential.create_ssh_credential(CREDENTIAL_NAME,
                                         ORGANIZATION,
                                         SSH_KEY_LOCATION)
except Exception as e:
    if "already exists" in e.message :
        print "Credential Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

try:
    # give the user permissions to the credential
    awx.role.grant(user=USER, credential=CREDENTIAL_NAME)
except Exception as e:
    if "already a member" in e.message :
        print "User Already Has Correct Permissions, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

# create inventory
try:
    awx.inventory.create(INVENTORY_NAME, ORGANIZATION)
except Exception as e:
    if "already exists" in e.message :
        print "Inventory Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

# create host
try:
    awx.host.create(
        INVENTORY_HOSTNAME,
        INVENTORY_NAME
    )
except Exception as e:
    if "already exists" in e.message :
        print "Host Already Exists in Inventory, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

try:
    # give the user permissions to the inventory
    awx.role.grant(user=USER, inventory=INVENTORY_NAME)
except Exception as e:
    if "already a member" in e.message :
        print "User Already Has Correct Permissions, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

try:
    awx_user.job_template.create(name=TEMPLATE_NAME,
                                 description=TEMPLATE_RUN_DESCRIPTION,
                                 job_type=TEMPLATE_TYPE,
                                 inventory=INVENTORY_NAME,
                                 project=PROJECT,
                                 playbook=PLAYBOOK,
                                 credential=CREDENTIAL_NAME,
                                 extra_vars=PLAYBOOK_VARS)
except Exception as e:
    if "already exists" in e.message :
        print "Job Template Already Exists, Will Not Create, CONTINUING"
        pass
    else:
        print e.message
        exit(1)

awx_user.job.launch(TEMPLATE_NAME, TEMPLATE_RUN_DESCRIPTION)

# Cleanup (Remove template, inventory)
# User, Credentials, Project will not be removed

# wait for the job to be complete before deleting
time.sleep(60)
awx.inventory.delete(INVENTORY_NAME)
awx.job_template.delete(TEMPLATE_NAME, PROJECT)
print "Use Case is complete"