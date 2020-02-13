from .user_project_access_report import UserProjectAccessReport


def create(subparsers, parents):
    parser = subparsers.add_parser('user-project-access',
                                   parents=parents,
                                   help='Report the projects a user has access to. NOTE: Only public projects or projects the user executing this script has access to will be reported.')
    parser.add_argument('users',
                        nargs='+',
                        help='The IDs and/or usernames of the users to report on.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out-path.')
    parser.set_defaults(_execute=execute)


def execute(args):
    UserProjectAccessReport(
        args.users,
        out_path=args.out_path
    ).execute()
