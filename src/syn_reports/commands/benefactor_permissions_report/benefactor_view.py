import uuid
import synapseclient as syn
from ...core import Utils, SynapseProxy


class BenefactorView(list):
    COL_BENEFACTORID = 'benefactorId'

    def __init__(self):
        self.scope = None
        self.view_project = None

    def set_scope(self, scope):
        """Clear the view data and load a new scope.

        Args:
            scope: The Project, Folder, or File to scope the view to.
        """
        self.clear()
        self.scope = scope
        self.load()

    def load(self):
        try:
            if isinstance(self.scope, syn.File):
                benefactor_id = SynapseProxy.client()._getBenefactor(self.scope).get('id')
                self._add_item(benefactor_id)
            elif type(self.scope) in [syn.Project, syn.Folder]:
                if self.view_project is None:
                    self._create_project()
                if SynapseProxy.is_project(self.scope):
                    # A separate view is required for Projects.
                    self._query_view(self._create_view([syn.EntityViewType.PROJECT]))

                self._query_view(self._create_view([syn.EntityViewType.FOLDER, syn.EntityViewType.FILE]))
            else:
                raise Exception('Scope entity must be a Project, Folder, or File.')
        except Exception as ex:
            Utils.eprint(ex)
            raise

    def _query_view(self, view):
        query = 'SELECT DISTINCT {0} FROM {1}'.format(self.COL_BENEFACTORID, view.id)
        query_result = SynapseProxy.client().tableQuery(query=query, resultsAs='csv')

        col_benefactorid = self._get_table_column_index(query_result.headers, self.COL_BENEFACTORID)

        for row in query_result:
            self._add_item(row[col_benefactorid])

    def _add_item(self, benefactorid):
        if benefactorid not in self:
            self.append(benefactorid)

    def _get_table_column_index(self, headers, column_name):
        """Gets the column index for a Synapse Table Column.
        """
        for index, item in enumerate(headers):
            if item.name == column_name:
                return index

    def _create_project(self):
        name = '_TEMP_{0}_VIEW_PROJECT_'.format(str(uuid.uuid4()))
        self.view_project = SynapseProxy.client().store(syn.Project(name=name))

    def _create_view(self, entity_types):
        name = '_TEMP_{0}_VIEW_'.format(str(uuid.uuid4()))
        cols = [
            syn.Column(name=self.COL_BENEFACTORID, columnType='ENTITYID')
        ]
        schema = syn.EntityViewSchema(name=name,
                                      columns=cols,
                                      properties=None,
                                      parent=self.view_project,
                                      scopes=[self.scope],
                                      includeEntityTypes=entity_types,
                                      addDefaultViewColumns=False,
                                      addAnnotationColumns=False)
        return SynapseProxy.client().store(schema)

    def delete(self):
        if self.view_project:
            SynapseProxy.client().delete(self.view_project)
