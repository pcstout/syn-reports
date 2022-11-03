import pytest
from synapse_test_helper import SynapseTestHelper
from src.syn_reports.core import SynapseProxy
from src.syn_reports.cli import main as cli_main
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope='session', autouse=True)
def syn_client():
    SynapseTestHelper.configure(SynapseProxy.client())
    return SynapseProxy.client()


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
