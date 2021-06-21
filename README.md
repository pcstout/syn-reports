# Synapse Reporting

Utilities for reporting on [Synapse](https://www.synapse.org/).

## Dependencies

- [Python3.7](https://www.python.org/)
- A [Synapse](https://www.synapse.org/) account with a username/password. Authentication through a 3rd party (.e.g.,
  Google) will not work, you must have a Synapse user/pass for
  the [API to authenticate](http://docs.synapse.org/python/#connecting-to-synapse).

## Install

```bash
pip install syn-reports
```

## Configuration

Your Synapse credential can be provided on the command line (`--username`, `--password`) or via environment variables.

```bash
SYNAPSE_USERNAME=your-synapse-username
SYNAPSE_PASSWORD=your-synapse-password
```

## Usage

```text
usage: syn-reports [-h]
                   {benefactor-permissions,entity-permissions,user-project-access,user-teams,team-members}
                   ...

Synapse Reports

optional arguments:
  -h, --help            show this help message and exit

Commands:
  {benefactor-permissions,entity-permissions,user-project-access,user-teams,team-members}
    benefactor-permissions
                        Report the unique permissions on a Synapse entity and
                        all its child entities.
    entity-permissions  Report the permissions of each user and team on a
                        Synapse entity.
    user-project-access
                        Report the projects a user has access to. NOTE: Only
                        public projects or projects the user executing this
                        script has access to will be reported.
    user-teams          Report the teams a user is a member of.
    team-members        Report the members on a team.
```

### entity-permissions

```text
usage: syn-reports entity-permissions [-h] [-u USERNAME] [-p PASSWORD]
                                      [-o OUT_PATH] [-r] [-a]
                                      entities [entities ...]

positional arguments:
  entities              The IDs and/or names of the entities to report on.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Synapse username.
  -p PASSWORD, --password PASSWORD
                        Synapse password.
  -o OUT_PATH, --out-path OUT_PATH
                        Path to export the report to. Specify a path that ends
                        in ".csv" to export to a specific file otherwise a
                        timestamped filename will be created in the out-path.
  -r, --recursive       Recursively report permissions on child entities. Will
                        report on each sub-folder/file/table that has
                        different permissions from the starting entity.
  -a, --all             Report permissions on every entity regardless of the
                        parent permission.
```

### benefactor-permissions

```text
sage: syn-reports benefactor-permissions [-h] [-u USERNAME] [-p PASSWORD]
                                          [-o OUT_PATH]
                                          entities [entities ...]

positional arguments:
  entities              The IDs and/or names of the entities to report on.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Synapse username.
  -p PASSWORD, --password PASSWORD
                        Synapse password.
  -o OUT_PATH, --out-path OUT_PATH
                        Path to export the report to. Specify a path that ends
                        in ".csv" to export to a specific file otherwise a
                        timestamped filename will be created in the out-path.
```

### user-project-access

```text
usage: syn-reports user-project-access [-h] [-u USERNAME] [-p PASSWORD]
                                       [-o OUT_PATH]
                                       users [users ...]

positional arguments:
  users                 The IDs and/or usernames of the users to report on.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Synapse username.
  -p PASSWORD, --password PASSWORD
                        Synapse password.
  -o OUT_PATH, --out-path OUT_PATH
                        Path to export the report to. Specify a path that ends
                        in ".csv" to export to a specific file otherwise a
                        timestamped filename will be created in the out-path.
```

### user-teams

```text
usage: syn-reports user-teams [-h] [-u USERNAME] [-p PASSWORD] [-o OUT_PATH]
                              [--has-member [HAS_MEMBER]]
                              users [users ...]

positional arguments:
  users                 The IDs and/or usernames of the users to report on.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Synapse username.
  -p PASSWORD, --password PASSWORD
                        Synapse password.
  -o OUT_PATH, --out-path OUT_PATH
                        Path to export the report to. Specify a path that ends
                        in ".csv" to export to a specific file otherwise a
                        timestamped filename will be created in the out path.
  --has-member [HAS_MEMBER]
                        Only report teams that also have this user in the
                        team.
```

### team-members

```text
usage: syn-reports team-members [-h] [-u USERNAME] [-p PASSWORD] [-o OUT_PATH]
                                teams [teams ...]

positional arguments:
  teams                 The IDs and/or names of the teams to report on.

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        Synapse username.
  -p PASSWORD, --password PASSWORD
                        Synapse password.
  -o OUT_PATH, --out-path OUT_PATH
                        Path to export the report to. Specify a path that ends
                        in ".csv" to export to a specific file otherwise a
                        timestamped filename will be created in the out path.
```

## Development Setup

```bash
pipenv --three
pipenv shell
make pip_install
make build
make install_local
```

See [Makefile](Makefile) for all commands.
