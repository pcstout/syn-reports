# Synapse Reporting

Utilities for reporting on [Synapse](https://www.synapse.org/).

## Dependencies

- [Python3.10+](https://www.python.org/)
- A [Synapse](https://www.synapse.org/) account with an auth
  token. [API to authenticate](http://docs.synapse.org/python/#connecting-to-synapse).

## Install

```bash
pip install syn-reports
```

## Configuration

Your Synapse credential can be provided on the command line or with environment variables.

Environment Variables:

```shell
# For auth token, set:
SYNAPSE_AUTH_TOKEN=

# For Synapse Config file, have a valid config file in:
~/.synapseConfig
# Or, have the environment variable set:
SYNAPSE_CONFIG_FILE=
```

Command Line:

```shell
-u USERNAME, --username USERNAME
                      Synapse username.
-p PASSWORD, --password PASSWORD
                      Synapse password.
--auth-token AUTH_TOKEN
                      Synapse auth token.
--synapse-config SYNAPSE_CONFIG
                      Path to Synapse configuration file.
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

## Development Setup

```bash
pipenv --python 3.11
pipenv shell
make pip_install
make build
make install_local
```

See [Makefile](Makefile) for all commands.

### Testing

- Create and activate a virtual environment:
- Rename [.env-template](.env-template) to [.env](.env) and set each of the variables.
- Run the tests: `make test`
