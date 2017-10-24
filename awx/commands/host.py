"""Awx host helper module."""
import json

from tower_cli.exceptions import NotFound

from .group import AwxGroup
from .inventory import AwxInventory
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxHost(AwxBase):
    """Awx host class."""
    __resource_name__ = 'host'

    def __init__(self):
        """Constructor."""
        super(AwxHost, self).__init__()
        self._group = AwxGroup()
        self._inventory = AwxInventory()

    @property
    def group(self):
        """Return group instance."""
        return self._group

    @property
    def inventory(self):
        """Return inventory instance."""
        return self._inventory

    @property
    def hosts(self):
        """Return list of hosts."""
        return self.resource.list()

    def associate(self, name, group, inventory):
        """Associate host with a group.

        :param name: Host name.
        :type name: str
        :param group: Group name.
        :type group: str
        """
        # get group
        group = self.group.get(group, inventory)

        # get host
        host = self.get(name, inventory)

        self.resource.associate(host=host['id'], group=group['id'])

    def disassociate(self, name, group):
        """"""

    def create(self, name, inventory, variables=None):
        """Create a host."""
        # check if inventory exists
        try:
            _inv = self.inventory.get(inventory)
        except Exception:
            raise Exception('Inventory %s not found.' % inventory)

        self.logger.info('Creating host %s.' % name)

        self.resource.create(
            name=name,
            inventory=_inv['id'],
            variables=json.dumps(variables),
            fail_on_found=True
        )

        self.logger.info('Host %s successfully created!' % name)

    def delete(self, name, inventory):
        """Delete a host."""
        # check if inventory exists
        try:
            _inv = self.inventory.get(inventory)
        except Exception:
            raise Exception('Inventory %s not found.' % inventory)

        self.logger.info('Deleting host %s.' % name)
        self.resource.delete(name=name, inventory=_inv['id'])
        self.logger.info('Host %s successfully deleted!' % name)

    def get(self, name, inventory):
        """Get host.

        :param name: Host name.
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
