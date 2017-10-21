"""Awx organization helper module."""
from tower_cli.exceptions import Found

from .user import AwxUser
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxOrganization(AwxBase):
    """Awx organization class."""
    __resource_name__ = 'organization'

    def __init__(self):
        """Constructor."""
        super(AwxOrganization, self).__init__()
        self._user = AwxUser()

    @property
    def user(self):
        """Return credential instance."""
        return self._user

    @property
    def organizations(self):
        """Return list of organizations."""
        return self.resource.list()

    def create(self, name, description=None):
        """Create an organization.

        :param name: Organization name.
        :type name: str
        :param description: Organization description.
        :type description: str
        """
        self.logger.info('Creating organization %s.' % name)

        try:
            self.resource.create(
                name=name,
                description=description,
                fail_on_found=True
            )
        except Found as ex:
            self.logger.error('Organization %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('Organization %s successfully created!' % name)

    def delete(self, name):
        """Delete an organization.

        :param name: Organization name.
        :type name: str
        """
        self.logger.info('Deleting organization %s.' % name)
        self.resource.delete(name=name)
        self.logger.info('Organization %s successfully deleted!' % name)

    def associate(self, organization, name):
        """Associate a user with the team

        :param organization: Organization name.
        :type organization: str
        :param name: User name
        :type name: str
        """
        try:
            user = self.user.get(name)
            organization_id = self.get(organization)["id"]
            self.resource.associate(organization=organization_id,
                                    user=user["id"])
        except Found as ex:
            raise Exception(ex.message)

    def disassociate(self, organization, name):
        """Disassociate a user with the team

        :param organization: Organization name.
        :type organization: str
        :param name: User name
        :type name: str
        """
        try:
            user = self.user.get(name)
            organization_id = self.get(organization)["id"]
            self.resource.disassociate(organization=organization_id,
                                       user=user["id"])
        except Found as ex:
            raise Exception(ex.message)

    def get(self, name):
        """Get organization.

        :param name: Organization name.
        :type name: str
        :return: Organization object.
        :rtype: dict
        """
        for item in self.organizations['results']:
            if item['name'] == name:
                return item
        return {}
