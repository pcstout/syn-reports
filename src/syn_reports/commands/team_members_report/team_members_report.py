import os
import csv
from ...core import SynapseProxy, Utils


class TeamMembersReport:
    """
    This report shows all the users on a team.
    """

    def __init__(self, team_ids_or_names, out_path=None):
        self._team_ids_or_names = team_ids_or_names
        if self._team_ids_or_names and not isinstance(self._team_ids_or_names, list):
            self._team_ids_or_names = [self._team_ids_or_names]
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None
        self.errors = []

    CSV_HEADERS = ['team_id',
                   'team_name',
                   'user_id',
                   'username',
                   'first_name',
                   'last_name',
                   'company',
                   'is_admin']

    def execute(self):
        if self._out_path:
            if self._out_path.lower().endswith('.csv'):
                self._csv_full_path = self._out_path
            else:
                self._csv_full_path = os.path.join(self._out_path, 'team-members-{0}.csv'.format(Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w', newline='', encoding='utf-8')
            self._csv_writer = csv.DictWriter(self._csv_file,
                                              delimiter=',',
                                              quotechar='"',
                                              fieldnames=self.CSV_HEADERS,
                                              quoting=csv.QUOTE_ALL)
            self._csv_writer.writeheader()
        try:
            for id_or_name in self._team_ids_or_names:
                self._report_on_team(id_or_name)
        finally:
            if self._csv_file:
                self._csv_file.close()
            if self._csv_full_path:
                print('Report saved to: {0}'.format(self._csv_full_path))
        return self

    def _report_on_team(self, id_or_name):
        print('=' * 80)
        print('Looking up team: "{0}"...'.format(id_or_name))
        team = None
        try:
            team = SynapseProxy.client().getTeam(id_or_name)
        except ValueError:
            # Team does not exist.
            pass
        except Exception as ex:
            self._show_error('Error loading team: {0}'.format(ex))

        if team:
            try:
                members = list(SynapseProxy.client().getTeamMembers(team))
                print('Found team: {0} ({1}) with {2} members.'.format(team.name, team.id, len(members)))
                for record in members:
                    print('  ---')
                    member = record.get('member')
                    user = SynapseProxy.WithCache.get_user(member.get('ownerId'))

                    user_id = user.get('ownerId')
                    username = user.get('userName', None)
                    first_name = user.get('firstName', None)
                    last_name = user.get('lastName', None)
                    company = user.get('company', None)
                    is_admin = record.get('isAdmin', False)

                    if username:
                        print('  Username: {0} ({1})'.format(username, user_id))
                    if first_name:
                        print('  First Name: {0}'.format(first_name))
                    if last_name:
                        print('  Last Name: {0}'.format(last_name))
                    if company:
                        print('  Company: {0}'.format(company))
                    print('  Is Admin: {0}'.format('Yes' if is_admin else 'No'))

                    if self._csv_writer:
                        self._csv_writer.writerow({'team_id': team.id,
                                                   'team_name': team.name,
                                                   'user_id': user_id,
                                                   'username': username,
                                                   'first_name': first_name,
                                                   'last_name': last_name,
                                                   'company': company,
                                                   'is_admin': is_admin})
            except Exception as ex:
                self._show_error('Error loading team data: {0}'.format(ex))
        else:
            self._show_error('Team does not exist or you do not have access to the team.')

    def _show_error(self, msg):
        self.errors.append(msg)
        Utils.eprint(msg)
