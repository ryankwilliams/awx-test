"""Sample script to fetch playbooks and their projects.

* Fetch all projects and their available playbooks
* Fetch a project for a given playbook
"""
import pprint

from awx import Awx

awx = Awx()

# get all playbooks
pprint.pprint(awx.project.playbooks, indent=4)

# get playbook's associated project
print(awx.project.get_playbook_project('system-release.yml'))
