import uuid
import synapseclient as syn
from ...core import Utils, SynapseProxy
from synapseclient.core.exceptions import SynapseHTTPError


class BenefactorView(list):
    COL_BENEFACTORID = 'benefactorId'
    COL_PROJECTID = 'projectId'

    def __init__(self):
        self.scope = None
        self.view_project = None

    def set_scope(self, scope, clear=True):
        """Load a new scope object and optionally clear the benefactor list data.

        Args:
            scope: The Project, Folder, or File to scope the view to.
            clear: Whether to clear the loaded benefactor list data or not.
        """
        if clear:
            self.clear()
        self.scope = scope
        self.load()

    def load(self):
        try:
            if type(self.scope) in [syn.Project, syn.Folder, syn.File]:
                self._add_single_scope_item(self.scope)

                if type(self.scope) in [syn.Project, syn.Folder]:
                    if self.view_project is None:
                        self._create_project()

                    # Create a view and load the uniq benefactors for each folder and file in the scoped container.
                    self._create_folder_and_file_view()
            else:
                raise Exception('Scope entity must be a Project, Folder, or File.')
        except Exception as ex:
            Utils.eprint(ex)
            raise

    def _create_folder_and_file_view(self):
        """Creates a view for all the folders and files within the current scope object.
        If a view cannot be created this method will fallback to adding each folder/file individually.
        """
        try:
            self._query_view(self._create_view([syn.EntityViewType.FOLDER, syn.EntityViewType.FILE]))
        except SynapseHTTPError as ex:
            if 'scope exceeds the maximum number' in str(ex):
                print('Cannot create Folder/File view for: {0}. Falling back to individual loading and views.'.format(
                    self.scope.name))
                self._fallback_add_folders_and_files()

    def _fallback_add_folders_and_files(self):
        """This will add the benefactor data into self for each folder and file in the current scope,
        then it will try to view load each folder. If a folder cannot be view loaded it will recurse through
        this method until a folder that can be view loaded is found or each folder/file has been added individually.

        Synapse has a limit of 20,000 objects in a container. If one of the projects or folders exceeds this number
        then we need to fallback to loading the benefactor data this way.
        """
        child_items = list(SynapseProxy.client().getChildren(self.scope, includeTypes=["folder", "file"]))
        folder_ids = []

        # Manually add each folder and file in the scope that couldn't be loaded via a view.
        child_added_count = 0
        for child_item in child_items:
            child_type_name = SynapseProxy.entity_type_display_name(child_item)
            child_item_id = child_item['id']
            child_added_count += 1
            print(' - Adding {0}: {1} [{2}/{3}]'.format(child_type_name,
                                                        child_item_id,
                                                        child_added_count,
                                                        len(child_items)))
            self._add_single_scope_item(child_item_id)
            if SynapseProxy.is_folder(child_item):
                folder_ids.append(child_item_id)

        # Try to load the folders with views.
        folder_added_count = 0
        for folder_id in folder_ids:
            folder_added_count += 1
            syn_folder = SynapseProxy.client().get(folder_id)
            print(' - Creating View for Folder: {0} ({1}) [{2}/{3}]'.format(syn_folder.id,
                                                                            syn_folder.name,
                                                                            folder_added_count,
                                                                            len(folder_ids)))
            self.set_scope(syn_folder, clear=False)

    def _add_single_scope_item(self, entity_or_id):
        """Gets the benefactor data for a single entity and adds it to self.

        Args:
            entity_or_id: The entity (or entity ID) to add benefactor data for.

        Returns:
            None
        """
        entity_id = entity_or_id['id'] if isinstance(entity_or_id, syn.Entity) else entity_or_id

        paths = SynapseProxy.client().restGET('/entity/{0}/path'.format(entity_id)).get('path')
        project_id = next((p for p in paths if p['type'] == 'org.sagebionetworks.repo.model.Project'))['id']

        benefactor_id = SynapseProxy.client()._getBenefactor(entity_id).get('id')
        self._add_item(benefactor_id, project_id)

    def _query_view(self, view):
        query = 'SELECT DISTINCT {0},{1} FROM {2}'.format(self.COL_BENEFACTORID, self.COL_PROJECTID, view.id)
        query_result = SynapseProxy.client().tableQuery(query=query, resultsAs='csv')

        col_benefactorid = self._get_table_column_index(query_result.headers, self.COL_BENEFACTORID)
        col_projectid = self._get_table_column_index(query_result.headers, self.COL_PROJECTID)

        for row in query_result:
            self._add_item(row[col_benefactorid], row[col_projectid])

    def _add_item(self, benefactor_id, project_id):
        item = {
            'benefactor_id': benefactor_id,
            'project_id': project_id
        }
        if item not in self:
            self.append(item)

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
            syn.Column(name=self.COL_BENEFACTORID, columnType='ENTITYID'),
            syn.Column(name=self.COL_PROJECTID, columnType='ENTITYID')
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
            SynapseProxy.delete_skip_trash(self.view_project)
