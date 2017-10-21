"""Awx user helper module."""
from tower_cli.exceptions import Found, NotFound

from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxUser(AwxBase):
    """Awx user class."""
    __resource_name__ = 'user'

    def __init__(self):
        """Constructor."""
        super(AwxUser, self).__init__()

    @property
    def users(self):
        """Return list of users."""
        return self.resource.list()

    def create(self, name, password, email, first_name, last_name,
               superuser=False, system_auditor=False):
        """Create a user.

        :param name: Username.
        :type name: str
        :param password: Password.
        :type password: str
        :param email: Email address.
        :type email: str
        :param first_name: First name.
        :type first_name: str
        :param last_name: Last name.
        :type last_name: str
        :param superuser: Superuser field.
        :type superuser: bool
        :param system_auditor: System auditor field.
        :type system_auditor: bool
        """
        self.logger.info('Creating user %s.' % name)
        try:
            self.resource.create(
                username=name,
                password=password,
                email=email,
                first_name=first_name,
                last_name=last_name,
                is_superuser=superuser,
                is_system_auditor=system_auditor,
                fail_on_found=True
            )
        except Found as ex:
            self.logger.error('User %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('User %s successfully created!' % name)

    def delete(self, name):
        """Delete a user.

        :param name: Username.
        :type name: str
        """
        self.logger.info('Deleting user %s.' % name)
        self.resource.delete(username=name)
        self.logger.info('User %s successfully deleted.' % name)

    def get(self, name):
        """Get a user.

        :param name: Username.
        :type name: str
        """
        try:
            return self.resource.get(username=name)
        except NotFound as ex:
            raise Exception(ex.message)
