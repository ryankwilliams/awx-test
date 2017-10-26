"""Awx notification template helper module."""

from tower_cli.exceptions import Found, NotFound
from .organization import AwxOrganization
from ..base import AwxBase

# TODO: Add in additional parameters that are optional for all methods.


class AwxNotificationTemplate(AwxBase):
    """Awx notification template class."""
    __resource_name__ = 'notification_template'

    def __init__(self):
        """Constructor."""
        super(AwxNotificationTemplate, self).__init__()
        self._organization = AwxOrganization()

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def notification_templates(self):
        """Return a list of job templates."""
        return self.resource.list()

    def create(self, name, notification_type, description="",
               organization="default", notification_configuration=None):
        """Create a notification template.

        :param name: Template name.
        :type name: str
        :param notification_type: Notification type.
        :type notification_type: str
        :param description: Template description.
        :type description: str
        :param organization: Organization name.
        :type organization: str
        :param notification_configuration: File or Notification Configuration.
        :type notification_configuration: filname str
        """
        # get organization object
        _organization = self.organization.get(organization)

        self.logger.info('Creating notification template %s.' % name)

        try:
            self.resource.create(
                name=name,
                description=description,
                notification_type=notification_type,
                organization=_organization['id'],
                notification_configuration=notification_configuration
            )
        except Found as ex:
            self.logger.error('Notification template %s already exists!' %
                              name)
            raise Exception(ex.message)

        self.logger.info('Notification template %s successfully created!' %
                         name)

    def delete(self, name, notification_type, description="",
               organization="default", notification_configuration=None):
        """Delete a notification template.

        :param name: Template name.
        :type name: str
        :param notification_type: Notification type.
        :type notification_type: str
        :param description: Template description.
        :type description: str
        :param organization: Organization name.
        :type organization: str
        :param notification_configuration: File or Notification Configuration.
        :type notification_configuration: filname str
        """

        # delete notification template
        self.logger.info('Deleting notification template %s.' % name)
        self.resource.delete(
            name=name,
            description=description,
            notification_type=notification_type,
            organization=organization,
            notification_configuration=notification_configuration
            )
        self.logger.info('Notification template %s successfully deleted!' %
                         name)

    def get(self, name):
        """Get Notification template.
        :param name: Template name.
        :type name: str
        :return: Template object.
        :rtype: dict
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)
