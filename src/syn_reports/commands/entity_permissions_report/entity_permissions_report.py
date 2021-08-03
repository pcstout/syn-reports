import os
import csv
import synapseclient as syn
from ...core import SynapseProxy, Utils


class EntityPermissionsReport:
    """
    This report will show the permissions of each user and team on an entity.
    """

    def __init__(self, entity_ids_or_names, out_path=None, recursive=False, report_on_all=False):
        self._entity_ids_or_names = entity_ids_or_names
        if self._entity_ids_or_names and not isinstance(self._entity_ids_or_names, list):
            self._entity_ids_or_names = [self._entity_ids_or_names]
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._recursive = recursive
        self._report_on_all = report_on_all
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self.errors = []

    CSV_HEADERS = ['entity_type',
                   'entity_id',
                   'entity_name',
                   'principal_type',
                   'team_id',
                   'team_name',
                   'is_team_manager',
                   'user_id',
                   'username',
                   'first_name',
                   'last_name',
                   'emails',
                   'permission_level']

    def execute(self):
        if self._out_path:
            if self._out_path.lower().endswith('.csv'):
                self._csv_full_path = self._out_path
            else:
                self._csv_full_path = os.path.join(self._out_path,
                                                   'entity-permissions-{0}.csv'.format(Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w', newline='', encoding='utf-8')
            self._csv_writer = csv.DictWriter(self._csv_file,
                                              delimiter=',',
                                              quotechar='"',
                                              fieldnames=self.CSV_HEADERS,
                                              quoting=csv.QUOTE_ALL)
            self._csv_writer.writeheader()
        try:
            for id_or_name in self._entity_ids_or_names:
                self._report_on_entity(id_or_name)
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                print('')
                print('Report saved to: {0}'.format(self._csv_full_path))
        return self

    def _report_on_entity(self, id_or_name, root_benefactor_id=None):
        print('=' * 80)
        print('Looking up entity: "{0}"...'.format(id_or_name))
        entity = None
        try:
            if SynapseProxy.is_synapse_id(id_or_name):
                syn_id_to_load = id_or_name
            else:
                syn_id_to_load = SynapseProxy.client().findEntityId(id_or_name)

            if syn_id_to_load:
                entity = SynapseProxy.client().restGET('/entity/{0}/type'.format(syn_id_to_load))
        except syn.core.exceptions.SynapseHTTPError:
            # Entity does not exist.
            pass
        except Exception as ex:
            self._show_error('Error loading entity: {0}'.format(ex))

        if entity:
            try:
                entity_type = SynapseProxy.entity_type_display_name(entity)
                print('{0}: {1} ({2}) found.'.format(entity_type, entity['name'], entity['id']))
                benefactor_id = entity['benefactorId']

                # Only report on permissions that are different from the root entity's permissions.
                if not self._report_on_all and (root_benefactor_id is not None and root_benefactor_id == benefactor_id):
                    print('  Permissions inherited from root entity.')
                else:
                    # NOTE: Do not use syn._getACL() as it will raise an error if the entity inherits its ACL.
                    entity_acl = SynapseProxy.client().restGET('/entity/{0}/acl'.format(benefactor_id))
                    # Get the resource access items and sort them so they can be compared.
                    resource_accesses = sorted(entity_acl.get('resourceAccess', []), key=lambda r: r.get('principalId'))
                    for resource in resource_accesses:
                        resource.get('accessType').sort()

                    for resource in resource_accesses:
                        user_or_team = SynapseProxy.WithCache.get_user_or_team(resource.get('principalId'))
                        permission_level = SynapseProxy.Permissions.name(resource.get('accessType'))
                        self._display_principal(entity, entity_type, permission_level, user_or_team)

                        if isinstance(user_or_team, syn.Team):
                            team_members = SynapseProxy.WithCache.get_team_members(user_or_team.id)
                            for team_member in team_members:
                                is_team_manager = team_member.get('isAdmin')
                                member = team_member.get('member')
                                user_id = member.get('ownerId')
                                user = SynapseProxy.WithCache.get_user(user_id)
                                self._display_principal(entity,
                                                        entity_type,
                                                        permission_level,
                                                        user,
                                                        from_team_id=user_or_team.id,
                                                        from_team_name=user_or_team.name,
                                                        from_team_user_is_manager=is_team_manager)

                if self._recursive:
                    if root_benefactor_id is None:
                        root_benefactor_id = benefactor_id

                    if SynapseProxy.is_project(entity) or SynapseProxy.is_folder(entity):
                        for child in SynapseProxy.client().getChildren(entity['id'],
                                                                       includeTypes=['folder', 'file', 'table']):
                            self._report_on_entity(child['id'], root_benefactor_id=root_benefactor_id)

            except Exception as ex:
                self._show_error('Error loading entity data: {0}'.format(ex))
        else:
            self._show_error('Entity does not exist or you do not have access to the entity.')

    def _display_principal(self, entity, entity_type, permission_level, user_or_team,
                           from_team_id=None, from_team_name=None, from_team_user_is_manager=None):
        indent = '  ' if from_team_id is None else '    '
        print('{0}---'.format(indent))
        principal_type = None
        team_name = None
        team_id = None
        is_team_manager = from_team_user_is_manager
        user_id = None
        username = None
        first_name = None
        last_name = None
        emails = None

        if isinstance(user_or_team, syn.Team):
            principal_type = 'Team'
            team_name = user_or_team.name
            team_id = user_or_team.id
            print('{0}Team: {1} ({2})'.format(indent, team_name, team_id))
        elif user_or_team is None:
            principal_type = 'Unknown'
            print('{0}Username/Team: Unknown - Script user ({1}) may not have access to this user/team data.)'.format(
                indent, SynapseProxy._synapse_username))
            if from_team_name:
                print('{0}From Team: {1} ({2})'.format(indent, from_team_name, from_team_id))
        else:
            principal_type = 'User'
            user_id = user_or_team.ownerId
            username = user_or_team.userName
            first_name = user_or_team.get('firstName', None)
            last_name = user_or_team.get('lastName', None)
            emails = ','.join(user_or_team.get('emails', []))
            print('{0}Username: {1} ({2})'.format(indent, username, user_id))
            if from_team_name:
                print('{0}From Team: {1} ({2})'.format(indent, from_team_name, from_team_id))
            if first_name:
                print('{0}First Name: {1}'.format(indent, first_name))
            if last_name:
                print('{0}Last Name: {1}'.format(indent, last_name))
            if emails:
                print('{0}Emails: {1}'.format(indent, emails))
            if is_team_manager is not None:
                print('{0}Team Manager: {1}'.format(indent, is_team_manager))

        print('{0}Permission: {1}'.format(indent, permission_level))

        if self._csv_writer:
            self._csv_writer.writerow({
                'entity_type': entity_type,
                'entity_id': entity['id'],
                'entity_name': entity['name'],
                'principal_type': principal_type,
                'team_id': team_id or from_team_id,
                'team_name': team_name or from_team_name,
                'is_team_manager': is_team_manager,
                'user_id': user_id,
                'username': username,
                'first_name': first_name,
                'last_name': last_name,
                'emails': emails,
                'permission_level': permission_level
            })

    def _show_error(self, msg):
        self.errors.append(msg)
        Utils.eprint(msg)
