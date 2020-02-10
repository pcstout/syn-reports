import os
import csv
from ...core import SynapseProxy, Utils


class TeamMembersReport:
    def __init__(self, team_id_or_name, out_path=None):
        self._team_id_or_name = team_id_or_name
        self._out_path = Utils.expand_path(out_path) if out_path else None

    def execute(self):
        print('Looking up team: "{0}"...'.format(self._team_id_or_name))
        try:
            team = SynapseProxy.client().getTeam(self._team_id_or_name)
        except ValueError:
            # Team does not exist.
            pass
        except Exception as ex:
            print('Error loading team: {0}'.format(ex))

        if team:
            csv_full_path = None
            csv_file = None
            csv_writer = None
            try:
                if self._out_path:
                    if self._out_path.lower().endswith('.csv'):
                        csv_full_path = self._out_path
                    else:
                        csv_full_path = os.path.join(self._out_path,
                                                     '{0}-team-members-{1}.csv'.format(team.name,
                                                                                       Utils.timestamp_str()))
                    Utils.ensure_dirs(os.path.dirname(csv_full_path))
                    csv_file = open(csv_full_path, mode='w')
                    csv_writer = csv.DictWriter(csv_file,
                                                delimiter=',',
                                                quotechar='"',
                                                fieldnames=['user_name',
                                                            'first_name',
                                                            'last_name',
                                                            'emails',
                                                            'is_individual',
                                                            'is_admin'],
                                                quoting=csv.QUOTE_ALL)
                    csv_writer.writeheader()

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

                    if csv_writer:
                        csv_writer.writerow({'user_name': user_name,
                                             'first_name': first_name,
                                             'last_name': last_name,
                                             'emails': emails,
                                             'is_individual': is_individual,
                                             'is_admin': is_admin})
            finally:
                if csv_file:
                    csv_file.close()
                    print('Report saved to: {0}'.format(csv_full_path))
        else:
            print('Team does not exist or you do not have access to the team.')
