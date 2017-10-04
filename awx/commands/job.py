"""Awx job helper module."""
import json
from tower_cli.exceptions import NotFound

from .job_template import AwxJobTemplate
from ..base import AwxBase


# TODO: Add in additional parameters that are optional for all methods.


class AwxJob(AwxBase):
    """Awx job class."""
    __resource_name__ = 'job'

    def __init__(self):
        """Constructor."""
        super(AwxJob, self).__init__()
        self._job_template = AwxJobTemplate()

    @property
    def job_template(self):
        """Return job template instance."""
        return self._job_template

    @property
    def jobs(self):
        """Return a list of jobs."""
        return self.resource.list()

    def launch(self, name, reason, extra_vars=None):
        """Launch a new job from a job template.

        :param name: Template name.
        :type name: str
        :param reason: Reason for template launch.
        :type reason: str
        :param extra_vars: Extra variables.
        :type extra_vars: list
        :return: Launch data
        :rtype: dict
        """
        # get job template object
        _job_template = self.job_template.get(name)

        # set extra vars
        _extra_vars = list()
        if extra_vars:
            for elem in extra_vars:
                _extra_vars.append(json.dumps(elem))
        else:
            _extra_vars = None

        return self.resource.launch(
            job_template=_job_template['id'],
            job_explanation=reason,
            extra_vars=_extra_vars
        )

    def status(self, job_id):
        """Get the job status

        :param job_id: job id.
        :type job_id: int
        :return: status
        :rtype: dict
        """
        try:
            return self.resource.status(job_id)
        except NotFound as ex:
            raise Exception(ex.message)

    def stdout(self, job_id):
        """Get the job's standard out

        :param job_id: job id.
        :type job_id: int
        :return: stdout from the playbook execution
        :rtype: dict
        """
        try:
            return self.resource.stdout(job_id)
        except NotFound as ex:
            raise Exception(ex.message)

    def monitor(self, job_id, interval=0.5, timeout=600):
        """Monitor the job

        :param job_id: job id.
        :type job_id: int
        :return: job information
        :rtype: dict
        """
        try:
            return self.resource.monitor(job_id, interval=interval, timeout=timeout)
        except NotFound as ex:
            raise Exception(ex.message)

    def cancel(self, job_id):
        """Get the job

        :param job_id: job id.
        :type job_id: int
        :return: job
        :rtype: dict
        """
        try:
            return self.resource.cancel(job_id)
        except NotFound as ex:
            raise Exception(ex.message)

    def get(self, job_id):
        """Get the job

        :param job_id: job id.
        :type job_id: int
        :return: job
        :rtype: dict
        """
        try:
            return self.resource.get(job_id)
        except NotFound as ex:
            raise Exception(ex.message)