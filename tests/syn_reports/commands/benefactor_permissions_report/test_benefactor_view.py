import pytest
from synapseclient.core.exceptions import SynapseHTTPError
from src.syn_reports.commands.benefactor_permissions_report import BenefactorView
from src.syn_reports.core.synapse_proxy import SynapseProxy
import synapseclient as syn


@pytest.fixture()
def benefactor_view(synapse_test_helper):
    bv = BenefactorView()
    yield bv
    if bv.view_project:
        synapse_test_helper.dispose(bv.view_project)


@pytest.fixture(scope='session')
def grant_access(syn_client):
    def _grant(syn_id, principal_id, access_type=SynapseProxy.Permissions.ADMIN):
        syn_client.setPermissions(syn_id, principalId=principal_id, accessType=access_type, warn_if_inherits=False)

    yield _grant


@pytest.fixture(scope='session')
def test_data(synapse_test_helper, syn_client, grant_access):
    # Project
    # file0
    # folder1/
    #   file1
    #   folder2/
    #     file2
    #     folder3/
    #       file3
    user_id = syn_client.getUserProfile()['ownerId']

    project = synapse_test_helper.create_project(prefix='project_')
    file0 = synapse_test_helper.create_file(parent=project, path=synapse_test_helper.create_temp_file(),
                                            prefix='file0_')
    grant_access(file0.id, user_id)

    folder1 = synapse_test_helper.create_folder(parent=project, prefix='folder1_')
    grant_access(folder1.id, user_id)
    file1 = synapse_test_helper.create_file(parent=folder1, path=synapse_test_helper.create_temp_file(),
                                            prefix='file1_')
    grant_access(file1.id, user_id)

    folder2 = synapse_test_helper.create_folder(parent=folder1, prefix='folder2_')
    grant_access(folder2.id, user_id)
    file2 = synapse_test_helper.create_file(parent=folder2, path=synapse_test_helper.create_temp_file(),
                                            prefix='file2_')
    grant_access(file2.id, user_id)

    folder3 = synapse_test_helper.create_folder(parent=folder2, prefix='folder3_')
    grant_access(folder3, user_id)
    file3 = synapse_test_helper.create_file(parent=folder3, path=synapse_test_helper.create_temp_file(),
                                            prefix='file3_')
    grant_access(file3, user_id)

    return {
        'project': project,
        'file0': file0,

        'folder1': folder1,
        'file1': file1,

        'folder2': folder2,
        'file2': file2,

        'folder3': folder3,
        'file3': file3,

        'all_entities': [project, file0, folder1, file1, folder2, file2, folder3, file3]
    }


def test_it_loads_all_the_benefactors_for_a_project(benefactor_view, test_data):
    project = test_data['project']
    benefactor_view.set_scope(project)

    expected_entities = test_data['all_entities']
    assert len(benefactor_view) == len(expected_entities)
    for entity in expected_entities:
        assert {'benefactor_id': entity.id, 'project_id': project.id} in benefactor_view


def test_it_loads_all_the_benefactors_for_a_folder(benefactor_view, test_data):
    project = test_data['project']
    folder1 = test_data['folder1']
    benefactor_view.set_scope(folder1)

    expected_entities = [e for e in test_data['all_entities'] if
                         e not in [test_data['project'], test_data['file0']]]
    assert len(benefactor_view) == len(expected_entities)
    for entity in expected_entities:
        assert {'benefactor_id': entity.id, 'project_id': project.id} in benefactor_view


def test_it_loads_all_the_benefactors_for_a_file(benefactor_view, test_data):
    project = test_data['project']
    file0 = test_data['file0']
    benefactor_view.set_scope(file0)

    expected_entities = [file0]
    assert len(benefactor_view) == len(expected_entities)
    for entity in expected_entities:
        assert {'benefactor_id': entity.id, 'project_id': project.id} in benefactor_view


def test_it_falls_back_to_individual_loading(benefactor_view, test_data, mocker):
    project = test_data['project']
    folder3 = test_data['folder3']

    orig__create_view = benefactor_view._create_view

    def mock__create_view(entity_types):
        # Allow the project view and folder3 view to be created, all others should fail and use the fallback.
        if entity_types == [syn.EntityViewType.PROJECT] or benefactor_view.scope == folder3:
            return orig__create_view(entity_types)
        else:
            raise SynapseHTTPError('scope exceeds the maximum number')

    mocker.patch.object(benefactor_view, '_create_view', new=mock__create_view)
    benefactor_view.set_scope(project)

    expected_entities = test_data['all_entities']
    assert len(benefactor_view) == len(expected_entities)
    for entity in expected_entities:
        assert {'benefactor_id': entity.id, 'project_id': project.id} in benefactor_view


def test_it_does_not_add_duplicate_items(benefactor_view):
    benefactor_view._add_item('1', '2')
    benefactor_view._add_item('1', '2')
    benefactor_view._add_item('1', '2')
    assert len(benefactor_view) == 1
