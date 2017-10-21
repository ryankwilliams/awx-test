"""Awx role helper module."""
from tower_cli.exceptions import Found

from .credential import AwxCredential
from .inventory import AwxInventory
from .project import AwxProject
from .user import AwxUser
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxRole(AwxBase):
    """Awx role class."""
    __resource_name__ = 'role'

    def __init__(self):
        """Constructor."""
        self._credential = AwxCredential()
        self._project = AwxProject()
        self._inventory = AwxInventory()
        self._user = AwxUser()
        super(AwxRole, self).__init__()

    @property
    def roles(self, user=None):
        # """Return list of users."""
        return self.resource.list()

    @property
    def credential(self):
        """Return credential instance."""
        return self._credential

    @property
    def inventory(self):
        """Return credential instance."""
        return self._inventory

    @property
    def project(self):
        """Return credential instance."""
        return self._project

    @property
    def user(self):
        """Return credential instance."""
        return self._user

    def grant(self, team=None, user=None, type="use", inventory=None,
              project=None, credential=None):

        user = self.user.get(user)
        # TODO: add support for TEAM

        if credential:
            # get credential object
            credential = self.credential.get(credential)
        elif inventory:
            inventory = self.inventory.get(inventory)
        elif project:
            project = self.project.get(project)
        else:
            raise Exception("Set a resource type to associate the role")

        try:
            self.resource.grant(
                                type=type,
                                user=user['id'],
                                team=team,
                                credential=credential['id'],
                                inventory=inventory['id'],
                                project=project['id'],
                                fail_on_found=True)
        except Found as ex:
            raise Exception(ex.message)

    def revoke(self, team=None, user=None, type="use", inventory=None,
               project=None, credential=None):

        user = self.user.get(user)
        # TODO: add support for TEAM

        if credential:
            # get credential object
            credential = self.credential.get(credential)
        elif inventory:
            inventory = self.inventory.get(inventory)
        elif project:
            project = self.project.get(project)
        else:
            raise Exception("Set a resource type to associate the role")

        try:
            self.resource.revoke(
                                type=type,
                                user=user['id'],
                                team=team,
                                credential=credential['id'],
                                inventory=inventory['id'],
                                project=project['id'],
                                fail_on_found=True)
        except Found as ex:
            raise Exception(ex.message)
