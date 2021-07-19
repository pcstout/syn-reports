from .team_members_report import TeamMembersReport


def create(subparsers, parents):
    parser = subparsers.add_parser('team-members',
                                   parents=parents,
                                   help='Report the members on a team.')
    parser.add_argument('teams',
                        nargs='+',
                        help='The IDs and/or names of the teams to report on.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out path.')
    parser.set_defaults(_execute=execute)


def execute(args):
    return TeamMembersReport(
        args.teams,
        out_path=args.out_path
    ).execute()
