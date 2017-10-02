"""Awx host helper module."""
import json

from .inventory import AwxInventory
from ..base import AwxBase

# TODO: Add in additional parameters that are optional for all methods.


class AwxHost(AwxBase):
    """Awx host class."""
    __resource_name__ = 'host'

    def __init__(self):
        """Constructor."""
        super(AwxHost, self).__init__()
        self._inventory = AwxInventory()

    @property
    def inventory(self):
        """Return inventory instance."""
        return self._inventory

    @property
    def hosts(self):
        """Return list of hosts."""
        return self.resource.list()

    def create(self, name, inventory, variables=None):
        """Create a host."""
        # check if inventory exists
        try:
            _inv = self.inventory.get(inventory)
        except Exception:
            raise Exception('Inventory %s not found.' % inventory)

        self.resource.create(
            name=name,
            inventory=_inv['id'],
            variables=json.dumps(variables),
            fail_on_found = True
        )

    def delete(self, name, inventory):
        """Delete a host."""
        # check if inventory exists
        try:
            _inv = self.inventory.get(inventory)
        except Exception:
            raise Exception('Inventory %s not found.' % inventory)

        self.resource.delete(
            name=name,
            inventory=_inv['id']
        )
