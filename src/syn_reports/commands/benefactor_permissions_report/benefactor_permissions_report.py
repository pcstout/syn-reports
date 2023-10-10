import os
import csv
import synapseclient as syn
from .benefactor_view import BenefactorView
from ...core import Utils
from synapsis import Synapsis


class BenefactorPermissionsReport:
    """
    This report will show the permissions of each user and team on an entity by using a File View to
    get the unique benefactors. This is much faster than walking the entire Project hierarchy.
    """

    def __init__(self, entity_ids_or_names, out_path=None,
                 out_file_prefix=None, out_file_per_entity=False,
                 out_file_without_timestamp=False, out_file_name_max_length=None):
        self._entity_ids_or_names = entity_ids_or_names if entity_ids_or_names is not None else []
        if self._entity_ids_or_names and not isinstance(self._entity_ids_or_names, list):
            self._entity_ids_or_names = [self._entity_ids_or_names]
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._out_file_prefix = out_file_prefix
        self._out_file_without_timestamp = out_file_without_timestamp
        self._out_file_per_entity = out_file_per_entity
        self._out_file_name_max_length = out_file_name_max_length
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self.csv_files_created = []
        self._view = None
        self.errors = []

    CSV_HEADERS = ['entity_type',
                   'entity_id',
                   'entity_name',
                   'entity_parent_id',
                   'entity_project_id',
                   'principal_type',
                   'team_id',
                   'team_name',
                   'is_team_manager',
                   'user_id',
                   'username',
                   'first_name',
                   'last_name',
                   'user_data',
                   'permission_level']

    def execute(self):
        if self._out_path and not self._out_file_per_entity:
            if not self._start_csv():
                return self

        try:
            self._view = BenefactorView()

            if not self._entity_ids_or_names:
                user = Synapsis.getUserProfile()
                print('Loading all Projects accessible to user: {0}'.format(user.userName))
                for activity in Utils.users_project_access(user.ownerId):
                    project_id = activity['id']
                    project_name = activity['name']
                    self._entity_ids_or_names.append(project_id)
                    print('  - Adding Project: {0} ({1})'.format(project_name, project_id))

            for id_or_name in self._entity_ids_or_names:
                try:
                    print('=' * 80)
                    print('Looking up entity: "{0}"...'.format(id_or_name))
                    entity = Utils.get_entity(id_or_name, self._show_error)
                    if entity:
                        entity_type = Synapsis.ConcreteTypes.get(entity)
                        entity_name = entity['name']
                        if self._out_path and self._out_file_per_entity:
                            if not self._start_csv(project_name=entity_name):
                                return self

                        print('{0}: {1} ({2}) found.'.format(entity_type.name, entity_name, entity['id']))
                        print('Creating Temporary Project and Views...')
                        self._view.set_scope(entity)
                        self._report_on_view()
                        if self._out_path and self._out_file_per_entity:
                            self._end_csv()
                    else:
                        self._show_error(
                            'Entity does not exist or you do not have access to the entity: {0}'.format(id_or_name))
                except Exception as ex:
                    self._show_error('ERROR: {0}'.format(ex))
        finally:
            self._end_csv()
            if len(self.csv_files_created) > 0:
                print('')
                print('Report(s) saved to:')
                for csv_file in self.csv_files_created:
                    print(csv_file)
            if self._view:
                self._view.delete()
        return self

    def _start_csv(self, project_name=None):
        self._end_csv()

        if self._out_path.lower().endswith('.csv'):
            if self._out_file_per_entity:
                self._show_error('Out path must be a directory when creating one output file per entity.')
                return False
            if self._out_file_prefix:
                self._show_error('Out path prefix not allowed when creating one output file per entity.')
                return False
            self._csv_full_path = self._out_path
        else:
            prefix = self._out_file_prefix if self._out_file_prefix else 'benefactor-permissions'
            timestamp = '' if self._out_file_without_timestamp else Utils.timestamp_str()
            project_name = project_name if project_name else ''

            csv_filename = '-'.join([s for s in [prefix, timestamp, project_name] if s])

            if self._out_file_name_max_length:
                csv_filename = csv_filename[:self._out_file_name_max_length]

            csv_filename = csv_filename + '.csv'
            self._csv_full_path = os.path.join(self._out_path, csv_filename)

        Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
        self._csv_file = open(self._csv_full_path, mode='w', newline='', encoding='utf-8')
        self._csv_writer = csv.DictWriter(self._csv_file,
                                          delimiter=',',
                                          quotechar='"',
                                          fieldnames=self.CSV_HEADERS,
                                          quoting=csv.QUOTE_ALL)
        self._csv_writer.writeheader()
        self.csv_files_created.append(self._csv_full_path)
        return True

    def _end_csv(self):
        if self._csv_file:
            self._csv_file.close()
            self._csv_file = None
            self._csv_writer = None

    def _show_error(self, msg):
        self.errors.append(msg)
        Utils.eprint(msg)

    def _report_on_view(self):
        for item in self._view:
            try:
                benefactor_id = item['benefactor_id']
                entity_project_id = item['project_id']

                entity = Synapsis.get(benefactor_id)
                entity_type = Synapsis.ConcreteTypes.get(entity)
                print('{0}: {1} ({2})'.format(entity_type.name, entity['name'], entity['id']))

                # NOTE: Do not use syn._getACL() as it will raise an error if the entity inherits its ACL and
                # it is slower as it will make an API call to get the benefactorId.
                entity_acl = Synapsis.restGET('/entity/{0}/acl'.format(entity.id))
                # Get the resource access items and sort them so they can be compared.
                resource_accesses = sorted(entity_acl.get('resourceAccess', []), key=lambda r: r.get('principalId'))

                for resource in resource_accesses:
                    user_or_team = Utils.WithCache.get_user_or_team(resource.get('principalId'))
                    permission = Synapsis.Permissions.get(resource.get('accessType'))

                    self._display_principal(entity, entity_type, entity_project_id, permission, user_or_team)

                    if isinstance(user_or_team, syn.Team):
                        team_members = Utils.WithCache.get_team_members(user_or_team.id)
                        for team_member in team_members:
                            is_team_manager = team_member.get('isAdmin')
                            member = team_member.get('member')
                            user_id = member.get('ownerId')
                            user = Utils.WithCache.get_user(user_id)
                            self._display_principal(entity,
                                                    entity_type,
                                                    entity_project_id,
                                                    permission,
                                                    user,
                                                    from_team_id=user_or_team.id,
                                                    from_team_name=user_or_team.name,
                                                    from_team_user_is_manager=is_team_manager)
                            team_invites = Utils.WithCache.get_team_open_invitations(user_or_team.id)
                            for team_invite in team_invites:
                                user_id = team_invite.get('inviteeId', None)
                                email = team_invite.get('inviteeEmail', None)
                                if user_id is not None:
                                    user = Utils.WithCache.get_user(user_id)
                                else:
                                    user = email
                                self._display_principal(entity,
                                                        entity_type,
                                                        entity_project_id,
                                                        permission,
                                                        user,
                                                        from_team_id=user_or_team.id,
                                                        from_team_name=user_or_team.name,
                                                        from_team_user_is_manager=is_team_manager,
                                                        is_invite=True)


            except Exception as ex:
                self._show_error('Error loading ACL data: {0}'.format(ex))

    def _display_principal(self, entity, entity_type, entity_project_id, permission, user_or_team_or_email,
                           from_team_id=None, from_team_name=None, from_team_user_is_manager=None,
                           is_invite=False):
        indent = '  ' if from_team_id is None else '    '
        print('{0}---'.format(indent))
        principal_type = None
        team_name = None
        is_team_manager = from_team_user_is_manager
        team_id = None
        user_id = None
        username = None
        first_name = None
        last_name = None
        user_data = None

        if isinstance(user_or_team_or_email, syn.Team):
            principal_type = 'Team'
            team_name = user_or_team_or_email.name
            team_id = user_or_team_or_email.id
            print('{0}Team: {1} ({2})'.format(indent, team_name, team_id))
        elif user_or_team_or_email is None:
            principal_type = 'Unknown'
            print(
                '{0}Username/Team: Unknown - Synapse user may not have access to this user/team data.)'.format(indent))
            if from_team_name:
                print('{0}From Team: {1} ({2})'.format(indent, from_team_name, from_team_id))
        elif is_invite and isinstance(user_or_team_or_email, str):
            principal_type = 'Invite'
            username = user_or_team_or_email
        else:
            if is_invite:
                principal_type = 'Invite'
            else:
                principal_type = 'User'
            user_id = user_or_team_or_email.ownerId
            username = user_or_team_or_email.userName
            first_name = user_or_team_or_email.get('firstName', None)
            last_name = user_or_team_or_email.get('lastName', None)

            user_field_data = []
            for field in ['company', 'location', 'position']:
                if user_or_team_or_email.get(field, None):
                    user_field_data.append(user_or_team_or_email.get(field))

            user_data = ' - '.join(user_field_data)

        if is_invite and user_id is None:
            print('{0}Invited Email: {1}'.format(indent, username))
        elif is_invite:
            print('{0}Invited Username: {1} ({2})'.format(indent, username, user_id))
        else:
            print('{0}Username: {1} ({2})'.format(indent, username, user_id))
        if from_team_name:
            print('{0}From Team: {1} ({2})'.format(indent, from_team_name, from_team_id))
        if first_name:
            print('{0}First Name: {1}'.format(indent, first_name))
        if last_name:
            print('{0}Last Name: {1}'.format(indent, last_name))
        if user_data:
            print('{0}User Data: {1}'.format(indent, user_data))
        if is_team_manager is not None:
            print('{0}Team Manager: {1}'.format(indent, is_team_manager))

        print('{0}Permission: {1}'.format(indent, permission.name))

        entity_parent_id = entity['parentId']
        # Do not include the parent ID for projects since no one has access to that container, and
        # it's not needed or useful.
        if Synapsis.ConcreteTypes.get(entity).is_project:
            entity_parent_id = None

        if self._csv_writer:
            self._csv_writer.writerow({
                'entity_type': entity_type.name,
                'entity_id': entity['id'],
                'entity_name': entity['name'],
                'entity_parent_id': entity_parent_id,
                'entity_project_id': entity_project_id,
                'principal_type': principal_type,
                'team_id': team_id or from_team_id,
                'team_name': team_name or from_team_name,
                'is_team_manager': is_team_manager,
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'user_data': user_data,
                'permission_level': permission.name
            })
