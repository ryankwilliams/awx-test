"""Runner."""
import time
import uuid
from urlparse import urljoin

import requests
import yaml

from awx import Awx

TOWER_USER = '<user>'
TOWER_PASSWORD = '<password>'
TOWER_URL = '<awx_url>'


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
        r = requests.get(full_url, auth=(user, password), verify=False)
        all_playbooks.extend(r.json())
        project_playbooks[proj["name"]] = r.json()

    # TODO: need a better way to do this
    playbook_name = playbook_name + ".yml"

    if playbook_name not in all_playbooks:
        return None
    else:
        for project in project_playbooks:
            if playbook_name in project_playbooks[project]:
                return project


class Runner(object):

    __organization__ = 'Carbon'

    def __init__(self, scenario):
        self.scenario = scenario

        # random id for run
        self.run_id = uuid.uuid4().hex[:4]

        # awx values
        self.inventory = 'inv_%s' % self.run_id
        self.project = 'proj_%s' % self.run_id
        self.credential = 'Demo Credential'

        # define attributes to be fulfilled
        self.scenario_data = dict()
        self.hosts = dict()
        self.orchestrate = dict()
        self._awx = Awx()

    @property
    def organization(self):
        return self.__organization__

    @property
    def awx(self):
        return self._awx

    @awx.setter
    def awx(self, value):
        self._awx = value

    def run(self):
        created_proj = True

        # load scenario
        with open(self.scenario, 'r') as fh:
            self.scenario_data = yaml.load(fh)

        self.hosts = self.scenario_data['provision']
        self.orchestrate = self.scenario_data['orchestrate']

        # create project and job templates
        for item in self.orchestrate:
            # create inventory
            self.awx.inventory.create(
                name=self.inventory,
                organization=self.organization
            )

            # create host and add to inventory
            for host in self.hosts:
                self.awx.host.create(
                    name=host['host'],
                    inventory=self.inventory,
                    variables=host['ansible_vars']
                )

            # only support scm (git)

            if 'scm' not in item:
                # must be using a common playbook, need to find project
                # query to see if project exists
                awx_user = self.awx
                playbook = item["name"]

                project = get_playbook_project(
                    awx_user,
                    TOWER_URL,
                    TOWER_USER,
                    TOWER_PASSWORD,
                    playbook
                )

                self.project = project
                if not self.project:
                    raise Exception("playbook not found")
                else:
                    created_proj = False
            elif 'scm' not in item and 'git' not in item['scm']['type']:
                continue

            job_template = 'job_%s' % uuid.uuid4().hex[:4]

            if created_proj:
                project = item['scm']['url'].split('/')[-1].split('.')[0]

                # create project
                try:
                    self.awx.project.create_scm_project(
                        name=project,
                        description=item['scm']['url'],
                        organization=self.organization,
                        scm_type=item['scm']['type'],
                        url=item['scm']['url']
                    )
                except Exception:
                    self.awx.logger.warn('SCM project already exists..')

                time.sleep(15)

            # create job template
            self.awx.job_template.create(
                name=job_template,
                description='Job template %s' % job_template,
                job_type='run',
                inventory=self.inventory,
                project=project,
                playbook="%s.yml" % item['name'],
                credential=self.credential
            )

            # run template
            results = self.awx.job.launch(
                name=job_template,
                reason='Job template %s' % job_template
            )

            # wait for job to finish
            try:
                output = self.awx.job.monitor(
                    results['id'],
                    interval=1,
                    timeout=300
                )
                self.awx.logger.debug(output)
            except Exception as ex:
                self.awx.logger.warn(ex)

            # delete job template
            self.awx.job_template.delete(
                name=job_template,
                project=project
            )

            # delete project if created
            if created_proj:
                self.awx.project.delete(name=project)

            # delete the inventory
            self.awx.inventory.delete(name=self.inventory)
            created_proj = True


if __name__ == '__main__':
    runner = Runner('scenario_03.yml')
    runner.run()
