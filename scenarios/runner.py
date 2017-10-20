"""Runner."""
import time
import uuid

import yaml

from awx import Awx


class Runner(object):

    __organization__ = 'minion'

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

        # create awx object for admin user
        admin_awx = Awx()

        # create minion organization
        try:
            admin_awx.organization.create(name=self.__organization__)
        except Exception:
            admin_awx.logger.warn('Organization already exists, skipping..')

        # create kingbob user
        try:
            admin_awx.user.create(
                'kingbob',
                'password',
                'kingbob@kingbob.com',
                'Kingbob',
                'Kingbob',
                superuser=True
            )
        except Exception:
            admin_awx.logger.warn('User already exists, skipping..')

        # create awx object for kingbob user
        self._awx = Awx(
            host='http://localhost',
            username='kingbob',
            password='password'
        )

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
        # load scenario
        with open(self.scenario, 'r') as fh:
            self.scenario_data = yaml.load(fh)

        self.hosts = self.scenario_data['provision']
        self.orchestrate = self.scenario_data['orchestrate']

        # create inventory
        self.awx.inventory.create(
            name=self.inventory,
            organization=self.organization
        )

        # create host and add to inventory
        for item in self.hosts:
            self.awx.host.create(
                name=item['host'],
                inventory=self.inventory,
                variables=item['ansible_vars']
            )

        # create project and job templates
        for item in self.orchestrate:
            # only support scm (git)
            if 'scm' not in item and 'git' not in item['scm']['type']:
                continue

            project = item['scm']['url'].split('/')[-1].split('.')[0]
            job_template = 'job_%s' % uuid.uuid4().hex[:4]

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

            # delete project
            self.awx.project.delete(name=project)


if __name__ == '__main__':
    runner = Runner('scenario_01.yml')
    runner.run()
