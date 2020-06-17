import os
import csv
from ...core import SynapseProxy, Utils


class TeamAccessReport:
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

    CSV_HEADERS = ['team_id',
                   'team_name',
                   'entity_type',
                   'entity_id',
                   'entity_name',
                   'permission_level']

    def execute(self):
        raise NotImplementedError('This command has not been completed.')
        SynapseProxy.login()

        if self._out_path:
            if self._out_path.lower().endswith('.csv'):
                self._csv_full_path = self._out_path
            else:
                self._csv_full_path = os.path.join(self._out_path, 'team-access-{0}.csv'.format(Utils.timestamp_str()))
            Utils.ensure_dirs(os.path.dirname(self._csv_full_path))
            self._csv_file = open(self._csv_full_path, mode='w', newline='')
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
        print('=' * 80)
        print('Looking up team: "{0}"...'.format(id_or_name))
        try:
            team = SynapseProxy.client().getTeam(id_or_name)
        except ValueError:
            # Team does not exist.
            pass
        except Exception as ex:
            Utils.eprint('Error loading team: {0}'.format(ex))

        if team:
            try:
                team_id = team['id']
                team_name = team['name']
                print('Team: {0} ({1})'.format(team_name, team_id))
                # TODO: How do we get the entities this team has access to?
                raise NotImplementedError()
            except Exception as ex:
                Utils.eprint('Error loading team data: {0}'.format(ex))
        else:
            Utils.eprint('Team does not exist or you do not have access to the team.')
