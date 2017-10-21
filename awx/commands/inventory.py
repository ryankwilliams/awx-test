"""Awx inventory helper module."""
from tower_cli.exceptions import Found, NotFound

from .organization import AwxOrganization
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxInventory(AwxBase):
    """Awx inventory class."""
    __resource_name__ = 'inventory'

    def __init__(self):
        """Constructor."""
        super(AwxInventory, self).__init__()
        self._organization = AwxOrganization()

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def inventories(self):
        """Return list of inventories."""
        return self.resource.list()

    def create(self, name, organization, description=None, variables=None):
        """Create an inventory file.

        :param name: Filename.
        :type name: str
        :param organization: Organization name.
        :type organization: str
        :param description: Inventory description.
        :type description: str
        :param variables: Inventory variables.
        :type variables: dict
        """
        # check if organization exists
        _org = self.organization.get(organization)

        # quit if organization not found
        if not _org:
            raise Exception('Organization %s not found.' % organization)

        self.logger.info('Creating inventory %s.' % name)

        try:
            self.resource.create(
                name=name,
                organization=_org['id'],
                description=description,
                variables=variables,
                fail_on_found=True
            )
        except Found as ex:
            self.logger.error('Inventory %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('Inventory %s successfully created!' % name)

    def delete(self, name):
        """Delete an inventory.

        :param name: Filename.
        :type name: str
        """
        self.logger.info('Deleting inventory %s.' % name)
        self.resource.delete(name=name)
        self.logger.info('Inventory %s successfully deleted!' % name)

    def get(self, name):
        """Get inventory.

        :param name: Inventory name.
        :type name: str
        :return: Inventory object.
        :rtype: dict
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)
