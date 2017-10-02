"""Awx team helper module."""
from tower_cli.exceptions import Found, NotFound

from .organization import AwxOrganization
from .user import AwxUser
from ..base import AwxBase

# TODO: Add in additional parameters that are optional for all methods.


class AwxTeam(AwxBase):
    """Awx team class."""
    __resource_name__ = 'team'

    def __init__(self):
        """Constructor."""
        super(AwxTeam, self).__init__()
        self._organization = AwxOrganization()
        self._user = AwxUser()

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def user(self):
        """Return credential instance."""
        return self._user

    @property
    def teams(self):
        """Return list of users."""
        return self.resource.list()

    def create(self, name, organization, description=""):
        """Create a team

        :param name: Team Name.
        :type name: str
        :param organization: Org the team belongs in
        :type password: str
        :param description: Team description.
        :type email: str
        """
        # check if organization exists
        _org = self.organization.get(organization)

        # quit if organization not found
        if not _org:
            raise Exception('Organization %s not found.' % organization)

        try:
            self.resource.create(
                name=name,
                organization=_org['id'],
                description=description,
                fail_on_found=True
            )
        except Found as ex:
            raise Exception(ex.message)

    def delete(self, name):
        """Delete a user.

        :param name: Username.
        :type name: str
        """
        self.resource.delete(name=name)

    def associate(self, team, name):
        """Associate a user with the team

        :param team: Team name.
        :type team: str
        :param name: User name
        :type name: str
        """
        try:
            user = self.user.get(name)
            team_id = self.get(team)["id"]
            self.resource.associate(team=team_id, user=user["id"])
        except Found as ex:
            raise Exception(ex.message)

    def disassociate(self, team, name):
        """Disassociate a user with the team

        :param team: Team name.
        :type team: str
        :param name: User name
        :type name: str
        """
        try:
            user = self.user.get(name)
            team_id = self.get(team)["id"]
            self.resource.disassociate(team=team_id, user=user["id"])
        except Found as ex:
            raise Exception(ex.message)

    def get(self, name):
        """Get a user.

        :param name: Team Name.
        :type name: str
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)
