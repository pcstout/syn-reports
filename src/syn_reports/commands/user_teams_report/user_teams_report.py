import os
import csv
from ...core import SynapseProxy, Utils


class UserTeamsReport:
    """
    This report shows all the teams a user is a member of.
    """

    def __init__(self, user_ids_or_usernames, out_path=None):
        self._user_ids_or_usernames = user_ids_or_usernames
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
                    print('Username: {0} ({1})'.format(username, user_id))
                    if first_name:
                        print('First Name: {0}'.format(first_name))
                    if last_name:
                        print('Last Name: {0}'.format(last_name))

                    teams = SynapseProxy.users_teams(user_id)

                    for team in teams:
                        print('  ---')
                        team_id = team['id']
                        team_name = team['name']

                        team_member = SynapseProxy.client().restGET('/team/{0}/member/{1}'.format(team_id, user_id))
                        is_admin = team_member.get('isAdmin', False)

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
                    print('Could not find user matching: {0}'.format(id_or_name))
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                print('Report saved to: {0}'.format(self._csv_full_path))
