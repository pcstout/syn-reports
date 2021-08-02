import functools
import os
import csv
import synapseclient as syn
from ...core import SynapseProxy, Utils


class UserProjectAccessReport:
    """
    This report will show all the Projects a user has access to.
    NOTE: Only public projects or projects the user executing this script has access to will be reported.
          This is a Synapse limitation.
    """

    def __init__(self, user_ids_or_usernames, out_path=None):
        self._user_ids_or_usernames = user_ids_or_usernames
        if self._user_ids_or_usernames and not isinstance(self._user_ids_or_usernames, list):
            self._user_ids_or_usernames = [self._user_ids_or_usernames]
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
                   'permission_level']

    def execute(self):
        SynapseProxy.login()

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
                    user = SynapseProxy.client().getUserProfile(id_or_name, refresh=True)
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

                    for activity in SynapseProxy.users_project_access(user_id):
                        project_id = activity['id']
                        project_name = activity['name']
                        users_permission = self._get_permissions(project_id, principal_id=user_id)
                        permission_level = SynapseProxy.Permissions.name(users_permission)

                        print('    Project: {0} ({1}) [{2}]'.format(project_name, project_id, permission_level))
                        if self._csv_writer:
                            self._csv_writer.writerow({
                                'user_id': user_id,
                                'username': username,
                                'first_name': first_name,
                                'last_name': last_name,
                                'project_id': project_id,
                                'project_name': project_name,
                                'permission_level': permission_level
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

    def _get_permissions(self, entity, principal_id):
        """Get the permissions that a user or group has on an Entity.

        :param entity:      An Entity or Synapse ID to lookup
        :param principal_id: Identifier of a user or group

        :returns: An array containing some combination of
                  ['READ', 'CREATE', 'UPDATE', 'DELETE', 'CHANGE_PERMISSIONS', 'DOWNLOAD']
                  or an empty array
        """
        # TODO: make this method return the highest permission the user has.
        principal_id = SynapseProxy.client()._getUserbyPrincipalIdOrName(principal_id)
        acl = SynapseProxy.client()._getACL(entity)

        # Look for the principal's individual permission on the entity.
        for resource in acl['resourceAccess']:
            if 'principalId' in resource and resource['principalId'] == int(principal_id):
                return resource['accessType']

        # Look for the principal's permission via a team on the entity.
        teams = self._get_users_teams(principal_id)
        team_ids = [int(t['id']) for t in teams]
        for resource in acl['resourceAccess']:
            if resource['principalId'] in team_ids:
                return resource['accessType']

        return []

    @functools.lru_cache(maxsize=SynapseProxy.WithCache.LRU_MAXSIZE, typed=True)
    def _get_users_teams(self, user_id):
        """Get all the teams a user is part of.

        Args:
            user_id: The user ID to get teams for.

        Returns:
            List
        """
        try:
            return list(SynapseProxy.users_teams(user_id))
        except syn.core.exceptions.SynapseHTTPError:
            return []

    def _show_error(self, msg):
        self.errors.append(msg)
        Utils.eprint(msg)
