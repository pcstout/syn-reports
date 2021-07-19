from .user_teams_report import UserTeamsReport


def create(subparsers, parents):
    parser = subparsers.add_parser('user-teams',
                                   parents=parents,
                                   help='Report the teams a user is a member of.')
    parser.add_argument('users',
                        nargs='+',
                        help='The IDs and/or usernames of the users to report on.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out path.')
    parser.add_argument('--has-member',
                        help='Only report teams that also have this user in the team.',
                        action='append',
                        nargs='?')
    parser.set_defaults(_execute=execute)


def execute(args):
    return UserTeamsReport(
        args.users,
        required_member_ids_or_usernames=args.has_member,
        out_path=args.out_path
    ).execute()
