import pytest
import os
from synapse_test_helper import SynapseTestHelper
from synapsis import Synapsis
from syn_reports.cli import main as cli_main, __init__hooks__, __on_after_login__
from dotenv import load_dotenv

load_dotenv(override=True)


@pytest.fixture(scope='session', autouse=True)
def syn_client():
    auth_token = os.environ.get('SYNAPSE_AUTH_TOKEN', None)
    assert auth_token
    SynapseTestHelper.configure(Synapsis.login().Synapse)
    return Synapsis.Synapse


@pytest.fixture(autouse=True)
def init_hooks():
    __init__hooks__()
    __on_after_login__(Synapsis.hooks.AFTER_LOGIN)
    assert Synapsis.Synapse.multi_threaded is False


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
