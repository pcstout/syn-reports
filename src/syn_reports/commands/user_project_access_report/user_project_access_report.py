import functools
import os
import csv
import synapseclient as syn
from ...core import Utils
from synapsis import Synapsis


class UserProjectAccessReport:
    """
    This report will show all the Projects a user has access to.
    NOTE: Only public projects or projects the user executing this script has access to will be reported.
          This is a Synapse limitation.
    """

    def __init__(self, user_ids_or_usernames, only_created_by=False, out_path=None):
        self._user_ids_or_usernames = user_ids_or_usernames
        if self._user_ids_or_usernames and not isinstance(self._user_ids_or_usernames, list):
            self._user_ids_or_usernames = [self._user_ids_or_usernames]
        self.only_created_by = only_created_by
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self.errors = []

    CSV_HEADERS = ['user_id',
                   'username',
                   'first_name',
                   'last_name',
                   'project_id',
                   'project_name',
                   'permission_level',
                   'project_created_by',
                   'project_created_by_id'
                   ]

    def execute(self):
        if self._out_path:
            if self._out_path.lower().endswith('.csv'):
                self._csv_full_path = self._out_path
            else:
                self._csv_full_path = os.path.join(self._out_path,
                                                   'user-access-{0}.csv'.format(Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w', newline='', encoding='utf-8')
            self._csv_writer = csv.DictWriter(self._csv_file,
                                              delimiter=',',
                                              quotechar='"',
                                              fieldnames=self.CSV_HEADERS,
                                              quoting=csv.QUOTE_ALL)
            self._csv_writer.writeheader()
        try:
            for id_or_name in self._user_ids_or_usernames:
                print('=' * 80)
                print('Looking up user: "{0}"...'.format(id_or_name))

                try:
                    user = Utils.WithCache.get_user(id_or_name)
                except ValueError:
                    # User does not exist
                    user = None

                if user:
                    user_id = user.ownerId
                    username = user.userName
                    first_name = user.get('firstName', None)
                    last_name = user.get('lastName', None)
                    print('  Username: {0} ({1})'.format(username, user_id))
                    if first_name:
                        print('  First Name: {0}'.format(first_name))
                    if last_name:
                        print('  Last Name: {0}'.format(last_name))

                    for activity in Utils.users_project_access(user_id):
                        project_id = activity['id']
                        project = Synapsis.get(project_id)
                        created_by_id = project.createdBy
                        created_by = Utils.WithCache.get_user(created_by_id)
                        created_by_username = created_by.userName

                        if not self.only_created_by or (self.only_created_by and user_id == created_by_id):
                            project_name = activity['name']
                            user_permission = self._get_permission(project_id, principal_id=user_id)

                            print('    Project: {0} (ID: {1}, Permission: {2}, Created By: {3})'.format(
                                project_name,
                                project_id,
                                user_permission.name,
                                created_by_username))

                            if self._csv_writer:
                                self._csv_writer.writerow({
                                    'user_id': user_id,
                                    'username': username,
                                    'first_name': first_name,
                                    'last_name': last_name,
                                    'project_id': project_id,
                                    'project_name': project_name,
                                    'permission_level': user_permission.name,
                                    'project_created_by': created_by_username,
                                    'project_created_by_id': created_by_id
                                })
                else:
                    self._show_error('Could not find user matching: {0}'.format(id_or_name))
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                print('')
                print('Report saved to: {0}'.format(self._csv_full_path))
        return self

    def _get_permission(self, entity, principal_id):
        """Get the permission that a user or group has on an Entity.

        :param entity:      An Entity or Synapse ID to lookup
        :param principal_id: Identifier of a user or group

        :returns: Synapsis.Permission or Synapsis.Permissions.NO_PERMISSION
        """
        # TODO: make this method return the highest permission the user has.
        principal_id = Synapsis._getUserbyPrincipalIdOrName(principal_id)
        acl = Synapsis._getACL(entity)
        resource_access = acl['resourceAccess']

        # Look for the principal's individual permission on the entity.
        for resource in resource_access:
            if 'principalId' in resource and resource['principalId'] == int(principal_id):
                return Synapsis.Permissions.get(resource['accessType'])

        # Look for the principal's permission via a team on the entity.
        teams = self._get_users_teams(principal_id)
        team_ids = Synapsis.utils.map(teams, lambda id: int(id), key='id')
        for resource in resource_access:
            if resource['principalId'] in team_ids:
                return Synapsis.Permissions.get(resource['accessType'])

        return Synapsis.Permissions.NO_PERMISSION

    @functools.lru_cache(maxsize=Utils.WithCache.LRU_MAXSIZE, typed=True)
    def _get_users_teams(self, user_id):
        """Get all the teams a user is part of.

        Args:
            user_id: The user ID to get teams for.

        Returns:
            List
        """
        try:
            return list(Utils.users_teams(user_id))
        except syn.core.exceptions.SynapseHTTPError:
            return []

    def _show_error(self, msg):
        self.errors.append(msg)
        Utils.eprint(msg)
