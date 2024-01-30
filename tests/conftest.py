import pytest
import os
from synapse_test_helper import SynapseTestHelper
from synapsis import Synapsis
from syn_reports.cli import main as cli_main
from syn_reports.core import Utils
import synapseclient as syn
from synapseclient.core.exceptions import SynapseHTTPError
from dotenv import load_dotenv

load_dotenv(override=True)


@pytest.fixture(autouse=TabError)
def before_each():
    return Utils.WithCache.clear_cache()


@pytest.fixture(scope='session')
def test_synapse_auth_token():
    return os.environ.get('SYNAPSE_AUTH_TOKEN')


@pytest.fixture(scope='session', autouse=True)
def syn_client(test_synapse_auth_token):
    Synapsis.configure(authToken=test_synapse_auth_token)
    SynapseTestHelper.configure(Synapsis.login().Synapse)
    return Synapsis.Synapse


@pytest.fixture(scope='session')
def synapse_test_helper():
    with SynapseTestHelper() as sth:
        yield sth


@pytest.fixture(scope='session')
def syn_project(synapse_test_helper):
    return synapse_test_helper.create_project(prefix='Project-')


@pytest.fixture(scope='session')
def syn_project2(synapse_test_helper):
    return synapse_test_helper.create_project(prefix='Project2-')


@pytest.fixture(scope='session')
def syn_folder(synapse_test_helper, syn_project):
    return synapse_test_helper.create_folder(parent=syn_project, prefix='Folder-')


@pytest.fixture(scope='session')
def syn_file(synapse_test_helper, syn_project):
    return synapse_test_helper.create_file(parent=syn_project, path=synapse_test_helper.create_temp_file(),
                                           prefix='File-')


@pytest.fixture(scope='session')
def syn_team(synapse_test_helper, syn_client):
    return synapse_test_helper.create_team()


@pytest.fixture(scope='session')
def expect_cli_exit_code():
    def _fn(command, expected_code, *args):
        with pytest.raises(SystemExit) as pytest_wrapped_e:
            cli_main([command, *args])
        assert pytest_wrapped_e.type == SystemExit
        assert pytest_wrapped_e.value.code == expected_code

    yield _fn


@pytest.fixture(scope='session')
def has_permission_to(synapse_test_helper):
    def _m(entity, principal, access_types=None):
        principal_id = syn.core.utils.id_of(principal)
        current_access_types = synapse_test_helper.client().getPermissions(entity, principalId=principal_id)
        if access_types is None:
            return len(current_access_types) > 0
        else:
            return set(current_access_types) == set(access_types)

    yield _m


@pytest.fixture(scope='session')
def has_direct_permission_to(synapse_test_helper):
    def _m(entity, principal, access_types=None):
        entity_id = Synapsis.id_of(entity)
        try:
            entity_acl = synapse_test_helper.client().restGET('/entity/{0}/acl'.format(entity_id))
        except SynapseHTTPError as ex:
            if ex.response.status_code == 404:
                # The requested ACL does not exist. This entity inherits its permissions from: /entity/syn0000000/acl
                return False
            else:
                raise
        resource_access = Synapsis.Utils.find_acl_resource_access(entity_acl, principal)
        current_access_types = resource_access['accessType'] if resource_access else []
        if access_types is None:
            return len(current_access_types) > 0
        else:
            return set(current_access_types) == set(access_types)

    yield _m
