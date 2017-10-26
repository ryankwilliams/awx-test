"""Awx job template helper module."""
import json

from tower_cli.exceptions import Found, NotFound

from .credential import AwxCredential
from .inventory import AwxInventory
from .project import AwxProject
from .notification_template import AwxNotificationTemplate
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxJobTemplate(AwxBase):
    """Awx job template class."""
    __resource_name__ = 'job_template'

    def __init__(self):
        """Constructor."""
        super(AwxJobTemplate, self).__init__()
        self._inventory = AwxInventory()
        self._credential = AwxCredential()
        self._project = AwxProject()
        self._notification_template = AwxNotificationTemplate()

    @property
    def project(self):
        """Return project instance."""
        return self._project

    @property
    def credential(self):
        """Return credential instance."""
        return self._credential

    @property
    def inventory(self):
        """Return inventory instance."""
        return self._inventory

    @property
    def notification_template(self):
        """Return notification instance."""
        return self._notification_template

    @property
    def job_templates(self):
        """Return a list of job templates."""
        return self.resource.list()

    def create(self, name, description, job_type, inventory, project, playbook,
               credential, extra_vars=None, ask_variables_on_launch=False,
               limit=None):
        """Create a job template.

        :param name: Template name.
        :type name: str
        :param description: Template description.
        :type description: str
        :param job_type: Job type.
        :type job_type: str
        :param inventory: Inventory name.
        :type inventory: str
        :param project: Project name.
        :type project: str
        :param playbook: Playbook name.
        :type playbook: str
        :param credential: Credential name.
        :type credential: str
        :param extra_vars: Extra variables.
        :type extra_vars: list
        :param ask_variables_on_launch: Prompt for playbook vars at run.
        :type ask_variables_on_launch: bool
        :param limit: Limit which hosts to run on based on inventory groups.
        :type limit: list
        """
        # get credential object
        _credential = self.credential.get(credential)

        # get inventory object
        _inventory = self.inventory.get(inventory)

        # get project object
        _project = self.project.get(project)

        # set extra vars
        _extra_vars = list()
        if extra_vars:
            for elem in extra_vars:
                _extra_vars.append(json.dumps(elem))
        else:
            _extra_vars = None

        self.logger.info('Creating job template %s.' % name)

        try:
            self.resource.create(
                name=name,
                description=description,
                job_type=job_type,
                inventory=_inventory['id'],
                project=_project['id'],
                playbook=playbook,
                credential=_credential['id'],
                extra_vars=_extra_vars,
                ask_variables_on_launch=ask_variables_on_launch,
                fail_on_found=True,
                limit=limit
            )
        except Found as ex:
            self.logger.error('Job template %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('Job template %s successfully created!' % name)

    def delete(self, name, project):
        """Delete a job template.

        :param name: Template name.
        :type name: str
        :param project: Project name.
        :type project: str
        """
        # get project object
        _project = self.project.get(project)

        # delete job template
        self.logger.info('Deleting job template %s.' % name)
        self.resource.delete(name=name, project=_project['id'])
        self.logger.info('Job template %s successfully deleted!' % name)

    def get(self, name):
        """Get job template.

        :param name: Template name.
        :type name: str
        :return: Template object.
        :rtype: dict
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)

    def associate_notification_template(self, job_template,
                                        notification_template, status="any"):
        """ Associate Notification template with job.

        :param job_template: Job template name.
        :type job_template: str
        :param notification_template: Notification Template name.
        :type notificatin_template: str
        :param status: Status to trigger Notificatin. Success, Failure or All
        :type status: str any|error|success

        """
        # get Job object
        _job = self.get(job_template)

        # get Notification object
        _notification_template =\
            self.notification_template.get(notification_template)

        try:
            self.resource.associate_notification_template(
                job_template=_job['id'],
                notification_template=_notification_template['id'],
                status=status)
        except NotFound as ex:
            raise Exception(ex.message)
