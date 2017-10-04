"""Awx helper module."""
from tower_cli.conf import settings

from . import __name__ as __awx_name__
from .base import LoggerMixin
from .commands.ad_hoc import AwxAdHoc
from .commands.config import AwxConfig
from .commands.credential import AwxCredential
from .commands.group import AwxGroup
from .commands.host import AwxHost
from .commands.inventory import AwxInventory
from .commands.inventory_script import AwxInventoryScript
from .commands.job import AwxJob
from .commands.job_template import AwxJobTemplate
from .commands.label import AwxLabel
from .commands.node import AwxNode
from .commands.notification_template import AwxNotificationTemplate
from .commands.organization import AwxOrganization
from .commands.permission import AwxPermission
from .commands.project import AwxProject
from .commands.role import AwxRole
from .commands.schedule import AwxSchedule
from .commands.setting import AwxSetting
from .commands.team import AwxTeam
from .commands.user import AwxUser
from .commands.version import AwxVersion
from .commands.workflow import AwxWorkflow
from .commands.workflow_job import AwxWorkflowJob


class Awx(LoggerMixin):
    """Awx class."""

    def __init__(self, host=None, username=None, password=None, verbose=1):
        """Constructor.

        :param host: Ansible AWX host URL.
        :type host: str
        :param username: AWX username.
        :type username: str
        :param password: AWX password.
        :type password: str
        :param verbose: Logging verbosity level.
        :type verbose: int
        """
        self.create_logger(__awx_name__, verbose=verbose)

        self._ad_hoc = AwxAdHoc()
        self._config = AwxConfig()
        self._credential = AwxCredential()
        self._group = AwxGroup()
        self._host = AwxHost()
        self._inventory = AwxInventory()
        self._inventory_script = AwxInventoryScript()
        self._job = AwxJob()
        self._job_template = AwxJobTemplate()
        self._label = AwxLabel()
        self._node = AwxNode()
        self._notification_template = AwxNotificationTemplate()
        self._organization = AwxOrganization()
        self._permission = AwxPermission()
        self._project = AwxProject()
        self._role = AwxRole()
        self._schedule = AwxSchedule()
        self._setting = AwxSetting()
        self._team = AwxTeam()
        self._user = AwxUser()
        self._version = AwxVersion()
        self._workflow = AwxWorkflow()
        self._workflow_job = AwxWorkflowJob()

        # set runtime parameters, this will override ones defined by file
        self.runtime_settings('host', host)
        self.runtime_settings('username', username)
        self.runtime_settings('password', password)
        self.runtime_settings('verify_ssl', 'False')

    @staticmethod
    def runtime_settings(key, value):
        """Set run time settings.

        :param key: Key name.
        :type key: str
        :param value: Key value.
        :type value: str
        """
        if value:
            settings.set_or_reset_runtime_param(key, value)

    @property
    def ad_hoc(self):
        """Return ad hoc instance."""
        return self._ad_hoc

    @property
    def config(self):
        """Return config instance."""
        return self._config

    @property
    def credential(self):
        """Return credential instance."""
        return self._credential

    @property
    def group(self):
        """Return group instance."""
        return self._group

    @property
    def host(self):
        """Return host instance."""
        return self._host

    @property
    def inventory(self):
        """Return inventory instance."""
        return self._inventory

    @property
    def inventory_script(self):
        """Return inventory script instance."""
        return self._inventory_script

    @property
    def job(self):
        """Return job instance."""
        return self._job

    @property
    def job_template(self):
        """Return job template instance."""
        return self._job_template

    @property
    def label(self):
        """Return label instance."""
        return self._label

    @property
    def node(self):
        """Return node instance."""
        return self._node

    @property
    def notification_template(self):
        """Return notification template instance."""
        return self._notification_template

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def permission(self):
        """Return permission instance."""
        return self._permission

    @property
    def project(self):
        """Return project instance."""
        return self._project

    @property
    def role(self):
        """Return role instance."""
        return self._role

    @property
    def schedule(self):
        """Return schedule instance."""
        return self._schedule

    @property
    def setting(self):
        """Return setting instance."""
        return self._setting

    @property
    def team(self):
        """Return team instance."""
        return self._team

    @property
    def user(self):
        """Return user instance."""
        return self._user

    @property
    def version(self):
        """Return version instance."""
        return self._version

    @property
    def workflow(self):
        """Return workflow instance."""
        return self._workflow

    @property
    def workflow_job(self):
        """Return workflow job instance."""
        return self._workflow_job
