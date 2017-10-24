"""Awx group helper module."""
from tower_cli.exceptions import Found, NotFound

from .inventory import AwxInventory
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxGroup(AwxBase):
    """Awx group class."""
    __resource_name__ = 'group'

    def __init__(self):
        """Constructor."""
        super(AwxGroup, self).__init__()
        self._inventory = AwxInventory()

    @property
    def inventory(self):
        """Return inventory instance."""
        return self._inventory

    @property
    def groups(self):
        """Return list of groups."""
        return self.resource.list()

    def create(self, name, inventory):
        """Create a group.

        :param name: Group name.
        :type name: str
        :param inventory: Inventory name.
        :type inventory: str
        """
        # get inventory
        inventory = self.inventory.get(inventory)

        try:
            self.resource.create(
                name=name,
                inventory=inventory['id'],
                fail_on_found=True
            )
        except Found as ex:
            self.logger.error('Group %s already exists!' % name)
            raise Exception(ex.message)

    def delete(self, name, inventory):
        """Delete a group.

        :param name: Group name.
        :type name: str
        :param inventory: Inventory name.
        :type inventory: str
        """
        # get inventory
        inventory = self.inventory.get(inventory)

        self.logger.info('Deleting group %s.' % name)
        self.resource.delete(name=name)
        self.logger.info('Group %s successfully deleted!' % name)

    def get(self, name, inventory):
        """Get group.

        :param name: Group name.
        :type name: str
        :param inventory: Inventory name.
        :type inventory: str
        """
        # get inventory
        inventory = self.inventory.get(inventory)
        try:
            return self.resource.get(name=name, inventory=inventory['id'])
        except NotFound as ex:
            raise Exception(ex.message)
