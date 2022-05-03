import pytest
import asyncio
from src.syn_reports.core import SynapseProxy
import synapseclient as syn


def test_is_synapse_id():
    assert SynapseProxy.is_synapse_id('SyN1230') is True
    assert SynapseProxy.is_synapse_id('  sYn1230  ') is True
    assert SynapseProxy.is_synapse_id('syn') is False
    assert SynapseProxy.is_synapse_id('syn 1230') is False
    assert SynapseProxy.is_synapse_id('1230') is False
    assert SynapseProxy.is_synapse_id('1230syn') is False


def test__extract_concrete_type():
    assert SynapseProxy._extract_concrete_type(syn.Project()) == 'org.sagebionetworks.repo.model.Project'
    assert SynapseProxy._extract_concrete_type(
        {'concreteType': 'org.sagebionetworks.repo.model.Project'}) == 'org.sagebionetworks.repo.model.Project'
    assert SynapseProxy._extract_concrete_type(
        {'type': 'org.sagebionetworks.repo.model.Project'}) == 'org.sagebionetworks.repo.model.Project'

    with pytest.raises(ValueError) as err:
        SynapseProxy._extract_concrete_type({})
    assert 'Cannot extract type from' in str(err)


def test_entity_type_display_name():
    assert SynapseProxy.entity_type_display_name(
        'org.sagebionetworks.repo.model.Project') == SynapseProxy.PROJECT_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(syn.Project()) == SynapseProxy.PROJECT_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(
        {'concreteType': 'org.sagebionetworks.repo.model.Project'}) == SynapseProxy.PROJECT_TYPE_DISPLAY_NAME

    assert SynapseProxy.entity_type_display_name(
        'org.sagebionetworks.repo.model.Folder') == SynapseProxy.FOLDER_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(syn.Folder(parentId='syn0')) == SynapseProxy.FOLDER_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(
        {'concreteType': 'org.sagebionetworks.repo.model.Folder'}) == SynapseProxy.FOLDER_TYPE_DISPLAY_NAME

    assert SynapseProxy.entity_type_display_name(
        'org.sagebionetworks.repo.model.FileEntity') == SynapseProxy.FILE_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(syn.File(parentId='syn0')) == SynapseProxy.FILE_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(
        {'concreteType': 'org.sagebionetworks.repo.model.FileEntity'}) == SynapseProxy.FILE_TYPE_DISPLAY_NAME

    assert SynapseProxy.entity_type_display_name(
        'org.sagebionetworks.repo.model.Link') == SynapseProxy.LINK_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(
        syn.Link(parentId='syn0', targetId='syn0')) == SynapseProxy.LINK_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(
        {'concreteType': 'org.sagebionetworks.repo.model.Link'}) == SynapseProxy.LINK_TYPE_DISPLAY_NAME

    assert SynapseProxy.entity_type_display_name(
        'org.sagebionetworks.repo.model.table.TableEntity') == SynapseProxy.TABLE_TYPE_DISPLAY_NAME
    assert SynapseProxy.entity_type_display_name(
        {'concreteType': 'org.sagebionetworks.repo.model.table.TableEntity'}) == SynapseProxy.TABLE_TYPE_DISPLAY_NAME


def test_is_project():
    assert SynapseProxy.is_project('org.sagebionetworks.repo.model.Project') is True
    assert SynapseProxy.is_project(syn.Project()) is True
    assert SynapseProxy.is_project({'concreteType': 'org.sagebionetworks.repo.model.Project'}) is True


def test_is_folder():
    assert SynapseProxy.is_folder('org.sagebionetworks.repo.model.Folder') is True
    assert SynapseProxy.is_folder(syn.Folder(parentId='syn0')) is True
    assert SynapseProxy.is_folder({'concreteType': 'org.sagebionetworks.repo.model.Folder'}) is True


def test_is_file():
    assert SynapseProxy.is_file('org.sagebionetworks.repo.model.FileEntity') is True
    assert SynapseProxy.is_file(syn.File(parentId='syn0')) is True
    assert SynapseProxy.is_file({'concreteType': 'org.sagebionetworks.repo.model.FileEntity'}) is True


def test_with_cache_get_user(synapse_test_helper):
    user_id = SynapseProxy.client().getUserProfile().get('ownerId')
    user = SynapseProxy.WithCache.get_user(user_id)
    assert user['ownerId'] == user_id

    # Returns None if the user does not exist
    assert SynapseProxy.WithCache.get_user('-9999999') is None
    assert SynapseProxy.WithCache.get_user('000') is None
    assert SynapseProxy.WithCache.get_user(synapse_test_helper.uniq_name(prefix='notarealname')) is None


def test_with_cache_get_team(synapse_test_helper):
    team = synapse_test_helper.create_team()
    team_id = team.get('id')
    team_name = team.get('name')

    team = SynapseProxy.WithCache.get_team(team_id)
    assert team['id'] == team_id

    team = SynapseProxy.WithCache.get_team(team_name)
    assert team['id'] == team_id

    # Returns None if the team does not exist
    assert SynapseProxy.WithCache.get_team('-9999999') is None
    assert SynapseProxy.WithCache.get_team('000') is None
    assert SynapseProxy.WithCache.get_team(synapse_test_helper.uniq_name(prefix='notarealname')) is None


def test_with_cache_get_user_or_team(synapse_test_helper):
    user_id = SynapseProxy.client().getUserProfile().get('ownerId')
    team_id = synapse_test_helper.create_team().get('id')

    user = SynapseProxy.WithCache.get_user_or_team(user_id)
    assert isinstance(user, syn.UserProfile)
    assert user['ownerId'] == user_id

    team = SynapseProxy.WithCache.get_user_or_team(team_id)
    assert isinstance(team, syn.Team)
    assert team['id'] == team_id

    # Returns None if the user and team do not exist
    assert SynapseProxy.WithCache.get_user_or_team('-9999999') is None
    assert SynapseProxy.WithCache.get_user_or_team('000') is None
    assert SynapseProxy.WithCache.get_user_or_team(synapse_test_helper.uniq_name(prefix='notarealname')) is None
    assert SynapseProxy.WithCache.get_user_or_team(synapse_test_helper.uniq_name(prefix='notarealname')) is None


def test_with_cache_get_team_members(synapse_test_helper):
    team = synapse_test_helper.create_team()
    members = SynapseProxy.WithCache.get_team_members(team.id)
    assert len(members) == 1

    # Returns [] if the team does not exist
    assert SynapseProxy.WithCache.get_team_members('-9999999') == []
    assert SynapseProxy.WithCache.get_team_members('000') == []
