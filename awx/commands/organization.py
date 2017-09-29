"""Awx organization helper module."""
from tower_cli.exceptions import Found

from ..base import AwxBase

# TODO: Add in additional parameters that are optional for all methods.


class AwxOrganization(AwxBase):
    """Awx organization class."""
    __resource_name__ = 'organization'

    def __init__(self):
        """Constructor."""
        super(AwxOrganization, self).__init__()

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
        try:
            self.resource.create(
                name=name,
                description=description,
                fail_on_found=True
            )
        except Found as ex:
            raise Exception(ex.message)

    def delete(self, name):
        """Delete an organization.

        :param name: Organization name.
        :type name: str
        """
        self.resource.delete(name=name)

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

