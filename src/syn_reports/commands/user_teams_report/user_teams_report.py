import os
import csv
import synapseclient as syn
from ...core import SynapseProxy, Utils


class UserTeamsReport:
    """
    This report shows all the teams a user is a member of.
    """

    def __init__(self, user_ids_or_usernames, required_member_ids_or_usernames=None, out_path=None):
        self._user_ids_or_usernames = user_ids_or_usernames
        if self._user_ids_or_usernames and not isinstance(self._user_ids_or_usernames, list):
            self._user_ids_or_usernames = [self._user_ids_or_usernames]

        self._required_member_ids_or_usernames = required_member_ids_or_usernames
        if self._required_member_ids_or_usernames and not isinstance(self._required_member_ids_or_usernames, list):
            self._required_member_ids_or_usernames = [self._required_member_ids_or_usernames]

        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None

    CSV_HEADERS = ['user_id',
                   'username',
                   'first_name',
                   'last_name',
                   'team_id',
                   'team_name',
                   'is_admin']

    def execute(self):
        SynapseProxy.login()

        if self._out_path:
            if self._out_path.lower().endswith('.csv'):
                self._csv_full_path = self._out_path
            else:
                self._csv_full_path = os.path.join(self._out_path, 'user-teams-{0}.csv'.format(Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w')
            self._csv_writer = csv.DictWriter(self._csv_file,
                                              delimiter=',',
                                              quotechar='"',
                                              fieldnames=self.CSV_HEADERS,
                                              quoting=csv.QUOTE_ALL)
            self._csv_writer.writeheader()
        try:
            required_members = []
            required_members_usernames = []
            if self._required_member_ids_or_usernames:
                for required_user_id_or_name in self._required_member_ids_or_usernames:
                    required_user = self._find_user(required_user_id_or_name)
                    if required_user is None:
                        Utils.eprint('Could not find user matching: {0}. Aborting.'.format(required_user_id_or_name))
                        return False
                    else:
                        required_members.append(required_user)
                        required_members_usernames.append(required_user.userName)

            if required_members:
                print('Only including teams that have members: {0}'.format(
                    ' or '.join(['{0} ({1})'.format(m.userName, m.ownerId) for m in required_members])))

            for id_or_name in self._user_ids_or_usernames:
                print('=' * 80)
                print('Looking up user: "{0}"...'.format(id_or_name))

                user = self._find_user(id_or_name)

                if user:
                    user_id = user.ownerId
                    username = user.userName
                    first_name = user.get('firstName', None)
                    last_name = user.get('lastName', None)
                    print('Username: {0} ({1})'.format(username, user_id))
                    if first_name:
                        print('First Name: {0}'.format(first_name))
                    if last_name:
                        print('Last Name: {0}'.format(last_name))

                    teams = SynapseProxy.users_teams(user_id)

                    for team in teams:
                        team_id = team['id']
                        team_name = team['name']

                        # Check if the team has at least on of the required members.
                        if required_members:
                            found_match = False
                            members = self._get_team_members(team_id)
                            for result in members:
                                member = result.get('member')
                                if member.get('userName') in required_members_usernames:
                                    found_match = True
                                    break

                            if not found_match:
                                continue

                        team_member = SynapseProxy.client().restGET('/team/{0}/member/{1}'.format(team_id, user_id))
                        is_admin = team_member.get('isAdmin', False)

                        print('  ---')
                        print('  Team: {0} ({1})'.format(team_name, team_id))
                        print('  Is Admin: {0}'.format('Yes' if is_admin else 'No'))
                        if self._csv_writer:
                            self._csv_writer.writerow({
                                'user_id': user_id,
                                'username': username,
                                'first_name': first_name,
                                'last_name': last_name,
                                'team_id': team_id,
                                'team_name': team_name,
                                'is_admin': is_admin
                            })
                else:
                    Utils.eprint('Could not find user matching: {0}'.format(id_or_name))
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                print('Report saved to: {0}'.format(self._csv_full_path))

    def _find_user(self, id_or_name):
        try:
            return SynapseProxy.client().getUserProfile(id_or_name, refresh=True)
        except ValueError:
            # User does not exist
            return None

    def _get_team_members(self, team_id):
        try:
            return list(SynapseProxy.client()._GET_paginated('/teamMembers/{0}'.format(team_id)))
        except syn.exceptions.SynapseHTTPError as ex:
            if ex.response.status_code != 403:
                Utils.eprint('Error getting team members: {0}'.format(ex))
            return []
