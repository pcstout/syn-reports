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
