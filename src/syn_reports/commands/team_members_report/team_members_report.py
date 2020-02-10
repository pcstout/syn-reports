import os
import csv
from ...core import SynapseProxy, Utils


class TeamMembersReport:

    def __init__(self, team_ids_or_names, out_path=None):
        self._team_ids_or_names = team_ids_or_names
        self._out_path = Utils.expand_path(out_path) if out_path else None
        self._csv_full_path = None
        self._csv_file = None
        self._csv_writer = None

    CSV_HEADERS = ['team_id',
                   'team_name',
                   'user_name',
                   'first_name',
                   'last_name',
                   'emails',
                   'is_individual',
                   'is_admin']

    def execute(self):
        if self._out_path:
            if self._out_path.lower().endswith('.csv'):
                self._csv_full_path = self._out_path
            else:
                self._csv_full_path = os.path.join(self._out_path, 'team-members-{0}.csv'.format(Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w')
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

    def _report_on_team(self, id_or_name):
        print('Looking up team: "{0}"...'.format(id_or_name))
        try:
            team = SynapseProxy.client().getTeam(id_or_name)
        except ValueError:
            # Team does not exist.
            pass
        except Exception as ex:
            print('Error loading team: {0}'.format(ex))

        if team:
            try:
                members = list(SynapseProxy.client().getTeamMembers(team))
                print('Found team: {0} ({1}) with {2} members.'.format(team.name, team.id, len(members)))
                for record in members:
                    print('---')
                    member = record.get('member')
                    profile = SynapseProxy.client().getUserProfile(member.get('ownerId'), refresh=True)

                    user_name = member.get('userName', None)
                    first_name = member.get('firstName', None)
                    last_name = member.get('lastName', None)
                    emails = ', '.join(profile.get('emails', []))
                    is_individual = member.get('isIndividual', False)
                    is_admin = record.get('isAdmin', False)

                    if user_name:
                        print('User Name: {0}'.format(user_name))
                    if first_name:
                        print('First Name: {0}'.format(first_name))
                    if last_name:
                        print('Last Name: {0}'.format(last_name))
                    if emails:
                        print('Emails: {0}'.format(emails))
                    print('Is Individual: {0}'.format('Yes' if is_individual else 'No'))
                    print('Is Admin: {0}'.format('Yes' if is_admin else 'No'))

                    if self._csv_writer:
                        self._csv_writer.writerow({'team_id': team.id,
                                                   'team_name': team.name,
                                                   'user_name': user_name,
                                                   'first_name': first_name,
                                                   'last_name': last_name,
                                                   'emails': emails,
                                                   'is_individual': is_individual,
                                                   'is_admin': is_admin})
            except Exception as ex:
                print('Error loading team data: {0}'.format(ex))
        else:
            print('Team does not exist or you do not have access to the team.')
