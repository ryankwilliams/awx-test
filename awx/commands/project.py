"""Awx project module."""
import urlparse

import requests
from tower_cli.exceptions import Found, NotFound

from .organization import AwxOrganization
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxProject(AwxBase):
    """Awx project class."""
    __resource_name__ = 'project'

    def __init__(self, **kwargs):
        """Constructor."""
        super(AwxProject, self).__init__()
        self._scm_types = ['manual', 'git', 'hg', 'svn']
        self.kwargs = kwargs

        self._organization = AwxOrganization()

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def scm_types(self):
        """Return a list of scm types."""
        return self._scm_types

    @property
    def projects(self):
        """Return a list of projects."""
        return self.resource.list()

    @property
    def playbooks(self):
        """Return a dictionary of project and its available playbooks."""
        playbooks = {}

        for project in self.projects['results']:
            play_path = project['related']['playbooks']
            url = urlparse.urljoin(self.kwargs['host'], play_path)
            response = requests.get(
                url,
                auth=(self.kwargs['username'], self.kwargs['password']),
                verify=False
            )
            playbooks[project['name']] = response.json()
        return playbooks

    def get_playbook_project(self, playbook):
        """Return the project for the associated playbook.

        :param playbook: Playbook name.
        :type playbook: str
        """
        for project, playbooks in self.playbooks.items():
            for pb in playbooks:
                if playbook in pb:
                    return project

    def get(self, name):
        """Get project.

        :param name: Project name.
        :type name: str
        :return: Project object.
        :rtype: dict
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)

    def create_scm_project(self, name, description, organization, scm_type,
                           url, branch='master', credential=None, clean=False,
                           delete_on_update=False, update_on_launch=False,
                           update_cache_timeout=0):
        """Create project based on scm source details.

        :param name: Project name.
        :type name: str
        :param description: Project description.
        :type description: str
        :param organization: Organization name.
        :type organization: str
        :param scm_type: SCM type.
        :type scm_type: str
        :param url: SCM url.
        :type url: str
        :param branch: SCM branch name.
        :type branch: str
        :param credential: SCM credential.
        :type credential: str
        :param clean: Remove local modifications before updating.
        :type clean: bool
        :param delete_on_update: Delete local repo before updating.
        :type delete_on_update: bool
        :param update_on_launch: Update local repo on each run.
        :type update_on_launch: bool
        :param update_cache_timeout: Update local repo timeout.
        :type update_cache_timeout: int
        """
        # check if organization exists
        _org = self.organization.get(organization)

        # quit if organization not found
        if not _org:
            raise Exception('Organization %s not found.' % organization)

        self.logger.info('Creating SCM project %s.' % name)

        try:
            self.resource.create(
                name=name,
                description=description,
                organization=_org['id'],
                scm_type=scm_type,
                scm_url=url,
                scm_branch=branch,
                scm_credential=credential,
                scm_clean=clean,
                scm_delete_on_update=delete_on_update,
                scm_update_on_launch=update_on_launch,
                scm_update_cache_timeout=update_cache_timeout,
                fail_on_found=True
            )
        except Found as ex:
            self.logger.error('SCM project %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('SCM project %s successfully created!' % name)

    def create_manual_project(self, name, description, organization):
        """Create project based on manual source.

        :param name: Project name.
        :type name: str
        :param description: Project description.
        :type description: str
        :param organization: Organization name.
        :type organization: str
        """
        # check if organization exists
        _org = self.organization.get(organization)

        # quit if organization not found
        if not _org:
            raise Exception('Organization %s not found.' % organization)

        self.logger.info('Creating manual project %s.' % name)

        try:
            self.resource.create(
                name=name,
                description=description,
                organization=_org['id'],
                scm_type='',
                fail_on_found=True
            )
        except Found as ex:
            self.logger.error('Manual project %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('Manual project %s successfully created!' % name)

    def delete(self, name):
        """Delete a project.

        :param name: Project name.
        :type name: str
        """
        self.logger.info('Deleting project %s.' % name)
        self.resource.delete(name=name)
        self.logger.info('Project %s successfully deleted.' % name)
