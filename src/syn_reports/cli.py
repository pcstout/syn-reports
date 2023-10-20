import argparse
import sys
from datetime import datetime
from .commands.team_members_report import cli as team_members_report_cli
from .commands.benefactor_permissions_report import cli as benefactor_permissions_report_cli
from .commands.entity_permissions_report import cli as entity_permissions_report_cli
from .commands.user_project_access_report import cli as user_project_access_report_cli
from .commands.user_teams_report import cli as user_teams_report_cli
# from .commands.team_access_report import cli as team_access_report_cli  # TODO: Uncomment when fully implemented.
from ._version import __version__
from synapsis import cli as synapsis_cli

ALL_ACTIONS = [
    benefactor_permissions_report_cli,
    entity_permissions_report_cli,
    user_project_access_report_cli,
    user_teams_report_cli,
    team_members_report_cli
]


def main(args=None):
    shared_parser = argparse.ArgumentParser(add_help=False)
    synapsis_cli.inject(shared_parser)

    main_parser = argparse.ArgumentParser(description='Synapse Reports')
    main_parser.add_argument('--version', action='version', version='%(prog)s {0}'.format(__version__))
    subparsers = main_parser.add_subparsers(title='Commands', dest='command')
    for action in ALL_ACTIONS:
        action.create(subparsers, [shared_parser])

    cmd_args = main_parser.parse_args(args)

    if '_execute' in cmd_args:
        exit_code = 1
        try:
            start_time = datetime.now()
            synapsis_cli.configure(cmd_args, synapse_args={'multi_threaded': False}, login=True)
            cmd = cmd_args._execute(cmd_args)
            end_time = datetime.now()
            if cmd.errors:
                print('Finished with errors.')
                for error in cmd.errors:
                    print(error)
                exit_code = 1
            else:
                print('Finished successfully.')
                exit_code = 0
        except Exception as ex:
            print(ex)
            exit_code = 1
        finally:
            print('Run time: {0}'.format(end_time - start_time))
            sys.exit(exit_code)
    else:
        main_parser.print_help()
        sys.exit(1)
