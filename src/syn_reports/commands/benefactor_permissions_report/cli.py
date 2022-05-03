from .benefactor_permissions_report import BenefactorPermissionsReport


def create(subparsers, parents):
    parser = subparsers.add_parser('benefactor-permissions',
                                   parents=parents,
                                   help='Report the unique permissions on a Synapse entity and all its child entities.')
    parser.add_argument('entities',
                        nargs='*',
                        help='The IDs and/or names of the entities to report on. Will report on all Projects the user has access to if not set.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out-path.')
    parser.add_argument('--out-file-prefix', help='The prefix to use for each CSV file that is created.')
    parser.add_argument('--out-file-per-entity', default=False,
                        action='store_true',
                        help='Create one CSV file per entity reported on.')
    parser.add_argument('--out-file-without-timestamp', default=False,
                        action='store_true',
                        help='Exclude the timestamp in each CSV file\'s name.')
    parser.add_argument('--out-file-name-max-length', type=int,
                        help='The max length of the CSV file name (minus the extension).')

    parser.set_defaults(_execute=execute)


def execute(args):
    return BenefactorPermissionsReport(
        args.entities,
        out_path=args.out_path,
        out_file_prefix=args.out_file_prefix,
        out_file_per_entity=args.out_file_per_entity,
        out_file_without_timestamp=args.out_file_without_timestamp,
        out_file_name_max_length=args.out_file_name_max_length
    ).execute()
