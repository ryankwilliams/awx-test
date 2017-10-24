"""Awx credential helper module."""
import os
from tower_cli.exceptions import Found, NotFound

from .organization import AwxOrganization
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxCredential(AwxBase):
    """Awx credential class."""
    __resource_name__ = 'credential'

    def __init__(self):
        """Constructor."""
        super(AwxCredential, self).__init__()
        self._organization = AwxOrganization()

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def credentials(self):
        """Return list of credentials."""
        return self.resource.list()

    def create_ssh_credential(self, name, organization, ssh_key_file):
        """Create a SSH credential entry.

        :param name: Credential name.
        :type name: str
        :param organization: Organization name.
        :type organization: str
        :param ssh_key_file: SSH private key file path.
        :type ssh_key_file: str
        """
        # quit if ssh private key file path does not exist
        if not os.path.exists(ssh_key_file):
            raise Exception('SSH private key %s not found.' % ssh_key_file)

        # check if organization exists
        _org = self.organization.get(organization)

        # quit if organization not found
        if not _org:
            raise Exception('Organization %s not found.' % organization)

        # load ssh private key
        with open(ssh_key_file, 'r') as fh:
            key_content = fh.read()

        # create credential entry
        try:
            self.resource.create(
                name=name,
                kind='ssh',
                organization=_org['id'],
                ssh_key_data=key_content,
                fail_on_found=True
            )
        except Found:
            self.logger.warn('Credential %s already exists!' % name)

    def delete(self, name, kind):
        """Delete a credential entry."""
        self.resource.delete(name=name, kind=kind)

    def get(self, name):
        """Get credential.

        :param name: Credential name.
        :type name: str
        :return: Credential object.
        :type dict
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)
