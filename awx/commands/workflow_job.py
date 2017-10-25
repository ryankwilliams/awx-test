"""Awx workflow job helper module."""
import json
from tower_cli.exceptions import NotFound
from ..base import AwxBase
from .workflow import AwxWorkflow

# TODO: Add in additional parameters that are optional for all methods.


class AwxWorkflowJob(AwxBase):
    """Awx workflow job class."""
    __resource_name__ = 'workflow_job'

    def __init__(self):
        """Constructor."""
        super(AwxWorkflowJob, self).__init__()
        self._workflow = AwxWorkflow()

    @property
    def workflow(self):
        """Return job template instance."""
        return self._workflow

    @property
    def workflow_jobs(self):
        """Return a list of jobs."""
        return self.resource.list()

    def launch(self, name, extra_vars=None):
        """Launch a new job from a job template.

        :param name: Template name.
        :type name: str
        :param extra_vars: Extra variables.
        :type extra_vars: list
        :return: Launch data
        :rtype: dict
        """
        # get job template object
        _workflow_template = self.workflow.get(name)

        # set extra vars
        _extra_vars = list()
        if extra_vars:
            for elem in extra_vars:
                _extra_vars.append(json.dumps(elem))
        else:
            _extra_vars = None

        return self.resource.launch(
            workflow_job_template=_workflow_template['id'],
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

    def summary(self, job_id):
        """Get the unified standard out

        :param job_id: job id.
        :type job_id: int
        :return: stdout from the playbook execution
        :rtype: dict
        """
        try:
            return self.resource.summary(job_id)
        except NotFound as ex:
            raise Exception(ex.message)

    def monitor(self, job_id, interval=1.0, timeout=3600):
        """Monitor the job
        by default check every second for 60 mins/hr

        :param job_id: job id.
        :type job_id: int
        :return: job information
        :rtype: dict
        """
        try:
            return self.resource.monitor(
                job_id,
                interval=interval,
                timeout=timeout
            )
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

    def delete(self, job_id):
        """Get the unified standard out

        :param job_id: job id.
        :type job_id: int
        :return: stdout from the playbook execution
        :rtype: dict
        """
        try:
            return self.resource.delete(job_id)
        except NotFound as ex:
            raise Exception(ex.message)
