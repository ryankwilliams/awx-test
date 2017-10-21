"""Use case 07.

This use case will demonstrate using tower-cli client library combined
with the REST api to perform the following actions with Ansible AWX:

    1. get playbooks from a project
    2. get all playbooks in the Organization
"""
from logging import getLogger
from urlparse import urljoin

import requests

from awx import Awx
from awx.awx import __awx_name__

LOG = getLogger(__awx_name__)

PROJECT = "Demo Project"
TOWER_URL = "http://localhost"
TOWER_USER = "<user>"
TOWER_PASSWORD = "<password>"

# create awx objects
awx = Awx()

project = awx.project.get(PROJECT)
playbook_path = project["related"]["playbooks"]

full_url = urljoin(TOWER_URL, playbook_path)
r = requests.get(full_url, auth=(TOWER_USER, TOWER_PASSWORD))
# all playbook in the specific PROJECT
LOG.info(r.json())

# get all projects
all_projects = awx.project.projects
all_playbooks = []

# get a dictionary of projects and playbooks
project_playbooks = {}

for proj in all_projects["results"]:
    playbook_path = proj["related"]["playbooks"]
    full_url = urljoin(TOWER_URL, playbook_path)
    r = requests.get(full_url, auth=(TOWER_USER, TOWER_PASSWORD))
    all_playbooks.extend(r.json())
    project_playbooks[proj["name"]] = r.json()

# all playbooks from all the projects
LOG.info(all_playbooks)
LOG.info(project_playbooks)
