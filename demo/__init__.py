import time
import uuid

from awx import Awx


class Run(object):

    __organization__ = 'Carbon'

    def __init__(self, input_config, tower_config):
        self.tower_config = tower_config
        self.hosts = input_config['provision']
        self.orchestrate = input_config['orchestrate']
        self.rid = uuid.uuid4().hex[:4]

        self.inventory = 'inventory_%s' % self.rid
        self.project = 'project_%s' % self.rid

        self.awx = Awx(
            self.tower_config['host'],
            self.tower_config['username'],
            self.tower_config['password']
        )

    @property
    def organization(self):
        return self.__organization__

    def go(self):
        # create inventory
        self.awx.inventory.create(self.inventory, self.organization)

        credential = 'credential_%s' % self.rid

        # add hosts
        for host in self.hosts:
            try:
                ssh_key = host['ansible_vars'].\
                    pop('ansible_ssh_private_key_file')
            except KeyError:
                raise Exception('ansible_ssh_private_key_file key not found!')

            # create host
            self.awx.host.create(
                name=host['host'],
                inventory=self.inventory,
                variables=host['ansible_vars']
            )

            # create credential
            self.awx.credential.create_ssh_credential(
                name=credential,
                organization=self.organization,
                ssh_key_file=ssh_key
            )

            # create group
            self.awx.group.create(
                name=host['name'],
                inventory=self.inventory
            )

            # associate host with group
            self.awx.host.associate(
                name=host['host'],
                group=host['name'],
                inventory=self.inventory
            )

        for item in self.orchestrate:
            # get branch
            try:
                branch = item['scm']['branch']
            except KeyError:
                branch = 'master'

            # create project
            try:
                project = item['scm']['url'].split('/')[-1].split('.')[0]

                self.awx.project.create_scm_project(
                    name=project,
                    description=item['scm']['url'],
                    organization=self.organization,
                    scm_type='git',
                    url=item['scm']['url'],
                    branch=branch
                )
            except Exception:
                self.awx.logger.warn('Project %s already exists.' % project)

            # lets delay for SCM update to finish
            # TODO: add a better check here
            self.awx.logger.warn('Delay 15 seconds for SCM update to finish.')
            time.sleep(15)

            # create job template
            job_template = 'job_%s' % self.rid

            # set extra vars for playbook
            try:
                extra_vars = item['extra_vars']
            except KeyError:
                extra_vars = None

            self.awx.job_template.create(
                name=job_template,
                description=item['description'],
                job_type='run',
                inventory=self.inventory,
                project=project,
                playbook='%s.yml' % item['name'],  # TODO: which file ext?
                credential=credential,
                extra_vars=extra_vars,
                limit=item['hosts'].replace(' ', ',').strip()
            )

            # run job template
            results = self.awx.job.launch(
                job_template,
                item['description']
            )

            # wait for job to complete
            try:
                output = self.awx.job.monitor(
                    results['id'],
                    interval=1,
                    timeout=300
                )
                self.awx.logger.debug(output)

                # delay
                self.awx.logger.info('Delaying..')
                time.sleep(2)

            except Exception as ex:
                self.awx.logger.warn(ex)

            # delete job template
            self.awx.job_template.delete(job_template, project)

            # delete project
            self.awx.project.delete(project)

        # delete inventory
        self.awx.inventory.delete(self.inventory)

        # delete credential
        self.awx.credential.delete(credential, 'ssh')
