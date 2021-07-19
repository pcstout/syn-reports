from .entity_permissions_report import EntityPermissionsReport


def create(subparsers, parents):
    parser = subparsers.add_parser('entity-permissions',
                                   parents=parents,
                                   help='Report the permissions of each user and team on a Synapse entity.')
    parser.add_argument('entities',
                        nargs='+',
                        help='The IDs and/or names of the entities to report on.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out-path.')
    parser.add_argument('-r', '--recursive',
                        default=False,
                        action='store_true',
                        help='Recursively report permissions on child entities. Will report on each sub-folder/file/table that has different permissions from the starting entity.')
    parser.add_argument('-a', '--all',
                        default=False,
                        action='store_true',
                        help='Report permissions on every entity regardless of the parent permission.')
    parser.set_defaults(_execute=execute)


def execute(args):
    return EntityPermissionsReport(
        args.entities,
        out_path=args.out_path,
        recursive=args.recursive,
        report_on_all=args.all
    ).execute()
