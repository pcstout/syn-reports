from .team_members_report import TeamMembersReport


def create(subparsers, parents):
    parser = subparsers.add_parser('team-members',
                                   parents=parents,
                                   help='Show the members of a team.')
    parser.add_argument('team', help='The ID or name of the team to report on.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out path.')
    parser.set_defaults(_execute=execute)


def execute(args):
    TeamMembersReport(args.team, out_path=args.out_path).execute()
