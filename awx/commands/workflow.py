"""Awx workflow helper module."""
from ..base import AwxBase
from .organization import AwxOrganization
from tower_cli.exceptions import Found, NotFound

# TODO: Add in additional parameters that are optional for all methods.


class AwxWorkflow(AwxBase):
    """Awx workflow class."""
    __resource_name__ = 'workflow'

    def __init__(self):
        """Constructor."""
        super(AwxWorkflow, self).__init__()
        self._organization = AwxOrganization()

    @property
    def organization(self):
        """Return organization instance."""
        return self._organization

    @property
    def workflow_templates(self):
        """Return a list of workflow templates."""
        return self.resource.list()

    def create(self, name, description, organization, fail_on_found=True):
        """Create a workflow template.

        :param name: Workflow template name.
        :type name: str
        :param description: Workflow template description.
        :type description: str
        :param organization: Orgnaization of the workflow template.
        :type organization: str
        :param fail_on_found: option to fail if found.
        :type fail_on_found: boolean
        """

        self.logger.info('Creating workflow template %s.' % name)
        _org = self.organization.get(organization)

        # quit if organization not found
        if not _org:
            raise Exception('Organization %s not found.' % organization)

        try:
            self.resource.create(
                name=name,
                description=description,
                organization=_org['id'],
                fail_on_found=fail_on_found
            )
        except Found as ex:
            self.logger.error('Workflow template %s already exists!' % name)
            raise Exception(ex.message)

        self.logger.info('Workflow template %s successfully created!' % name)

    def upload_schema(self, name, schema_loc):
        """Upload a workflow schema (json or yaml)

        :param name: Workflow template name.
        :type name: str
        :param schema_loc: File location of the schema.
        :type schema_loc: str
        :return: workflow template object.
        :rtype: dict
        """
        workflow_obj = self.get(name)
        # quit if organization not found
        if not workflow_obj:
            raise Exception('Workflow Template {} not found.'.format(name))
        return self.resource.schema(wfjt=workflow_obj["id"],
                                    node_network=schema_loc)

    def get_schema(self, name):
        """Get the schema of an existing workflow schema

        :param name: Workflow template name.
        :type name: str
        :return: workflow template object.
        :param format: format of the output
        :type: enum (yaml, json, human)
        :rtype: dict
        """
        workflow_obj = self.get(name)
        # quit if organization not found
        if not workflow_obj:
            raise Exception('Workflow Template {} not found.'.format(name))
        return self.resource.schema(wfjt=workflow_obj["id"])

    def delete(self, name):
        """Delete a workflow template.

        :param name: Workflow template name.
        :type name: str
        """

        # delete workflow template
        self.logger.info('Deleting workflow template %s.' % name)
        self.resource.delete(name=name)
        self.logger.info('Workflow template %s successfully deleted!' % name)

    def get(self, name):
        """Get the workflow

        :param name: Workflow template name.
        :type name: str
        :return: Workflow object.
        :type dict
        """
        try:
            return self.resource.get(name=name)
        except NotFound as ex:
            raise Exception(ex.message)
