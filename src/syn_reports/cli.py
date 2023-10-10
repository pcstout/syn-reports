import argparse
import sys
import os
import logging
from .commands.team_members_report import cli as team_members_report_cli
from .commands.benefactor_permissions_report import cli as benefactor_permissions_report_cli
from .commands.entity_permissions_report import cli as entity_permissions_report_cli
from .commands.user_project_access_report import cli as user_project_access_report_cli
from .commands.user_teams_report import cli as user_teams_report_cli
from .commands.team_access_report import cli as team_access_report_cli  # TODO: Uncomment when fully implemented.
from ._version import __version__
from synapsis import cli as synapsis_cli, Synapsis

ALL_ACTIONS = [
    benefactor_permissions_report_cli,
    entity_permissions_report_cli,
    user_project_access_report_cli,
    user_teams_report_cli,
    team_members_report_cli
]


def __on_after_login__(hook):
    for name, default, attr in [
        ('SYNTOOLS_MULTI_THREADED', 'False', 'multi_threaded'),
        ('SYNTOOLS_USE_BOTO_STS_TRANSFERS', 'False', 'use_boto_sts_transfers')
    ]:
        env_value = os.environ.get(name, default).lower() == 'true'
        setattr(Synapsis.Synapse, attr, env_value)
        if env_value:
            logging.info('Setting {0}={1}'.format(attr, env_value))


def __init__hooks__():
    Synapsis.hooks.after_login(__on_after_login__)


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
        try:
            __init__hooks__()
            synapsis_cli.configure(cmd_args, login=True)
            cmd = cmd_args._execute(cmd_args)
            if cmd.errors:
                print('Finished with errors.')
                for error in cmd.errors:
                    print(error)
                sys.exit(1)
            else:
                print('Finished successfully.')
                sys.exit(0)
        except Exception as ex:
            print(ex)
            sys.exit(1)
    else:
        main_parser.print_help()
        sys.exit(1)
