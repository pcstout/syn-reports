from .benefactor_permissions_report import BenefactorPermissionsReport


def create(subparsers, parents):
    parser = subparsers.add_parser('benefactor-permissions',
                                   parents=parents,
                                   help='Report the unique permissions on a Synapse entity and all its child entities.')
    parser.add_argument('entities',
                        nargs='+',
                        help='The IDs and/or names of the entities to report on.')
    parser.add_argument('-o', '--out-path', default=None,
                        help='Path to export the report to. Specify a path that ends in ".csv" to export to a specific file otherwise a timestamped filename will be created in the out-path.')
    parser.set_defaults(_execute=execute)


def execute(args):
    bpr = BenefactorPermissionsReport(
        args.entities,
        out_path=args.out_path
    )
    bpr.execute()
    if bpr.errors:
        print('!' * 80)
        print('Finished with errors.')
        for error in bpr.errors:
            print(error)
