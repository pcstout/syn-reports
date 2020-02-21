import pytest
import os
import json
import shutil
import tempfile
from .synapse_test_helper import SynapseTestHelper
from src.syn_reports.core import SynapseProxy

# Load Environment variables.
module_dir = os.path.dirname(os.path.abspath(__file__))

test_env_file = os.path.join(module_dir, 'private.test.env.json')

if os.path.isfile(test_env_file):
    with open(test_env_file) as f:
        config = json.load(f).get('test')

        for key, value in config.items():
            os.environ[key] = value
else:
    print('WARNING: Test environment file not found at: {0}'.format(test_env_file))


@pytest.fixture(scope='session')
def syn_client():
    return SynapseProxy.client()


@pytest.fixture(scope='session')
def syn_test_helper():
    """
    Provides the SynapseTestHelper as a fixture per session.
    """
    helper = SynapseTestHelper()
    yield helper
    helper.dispose()


@pytest.fixture(scope='session')
def syn_project(syn_test_helper):
    return syn_test_helper.create_project()


@pytest.fixture(scope='session')
def syn_folder(syn_test_helper, syn_project):
    return syn_test_helper.create_folder(parent=syn_project)


@pytest.fixture(scope='session')
def syn_file(syn_test_helper, mk_tempfile, syn_project):
    return syn_test_helper.create_file(parent=syn_project, path=mk_tempfile())


@pytest.fixture(scope='session')
def mk_tempdir():
    created = []

    def _mk():
        path = tempfile.mkdtemp()
        created.append(path)
        return path

    yield _mk

    for path in created:
        if os.path.isdir(path):
            shutil.rmtree(path)


@pytest.fixture(scope='session')
def mk_tempfile(mk_tempdir, syn_test_helper):
    temp_dir = mk_tempdir()

    def _mk(content=syn_test_helper.uniq_name()):
        fd, tmp_filename = tempfile.mkstemp(dir=temp_dir)
        with os.fdopen(fd, 'w') as tmp:
            tmp.write(content)
        return tmp_filename

    yield _mk

    if os.path.isdir(temp_dir):
        shutil.rmtree(temp_dir)
