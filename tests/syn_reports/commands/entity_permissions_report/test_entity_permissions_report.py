import pytest
import os
from src.syn_reports.commands.entity_permissions_report import EntityPermissionsReport
from src.syn_reports.core import Utils, SynapseProxy


def assert_success_from_print(capsys, *entities):
    captured = capsys.readouterr()
    assert captured.err == ''
    for entity in entities:
        log_msg = '{0}: {1} ({2}) found.'.format(SynapseProxy.entity_type_display_name(entity),
                                                 entity.name,
                                                 entity.id)
        assert log_msg in captured.out


def assert_success_from_csv(csv_full_path, *entities):
    assert os.path.isfile(csv_full_path)
    with open(csv_full_path, mode='r') as f:
        contents = f.read()
        for entity in entities:
            assert entity.id in contents
            assert entity.name in contents


def test_it_reports_on_projects_by_id(capsys, syn_project):
    EntityPermissionsReport(syn_project.id).execute()
    assert_success_from_print(capsys, syn_project)


def test_it_reports_on_projects_by_name(capsys, syn_project):
    EntityPermissionsReport(syn_project.name).execute()
    assert_success_from_print(capsys, syn_project)


def test_it_does_not_blowup_if_entity_not_found(capsys):
    EntityPermissionsReport('syn000').execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity.' in captured.err


def test_it_reports_recursively_by_project(capsys, syn_project, syn_folder, syn_file):
    EntityPermissionsReport(syn_project.id, recursive=True).execute()
    assert_success_from_print(capsys, syn_project, syn_folder, syn_file)


def test_it_reports_all_permissions_by_project(capsys, syn_project, syn_folder, syn_file):
    EntityPermissionsReport(syn_project.id, recursive=True, report_on_all=True).execute()
    assert_success_from_print(capsys, syn_project, syn_folder, syn_file)


def test_it_outputs_csv_to_dir(capsys, synapse_test_helper, syn_project, syn_folder, syn_file):
    out_dir = synapse_test_helper.create_temp_dir()
    report = EntityPermissionsReport(syn_project.id, recursive=True, out_path=out_dir)
    report.execute()
    assert_success_from_print(capsys, syn_project, syn_folder, syn_file)
    # Folder and File have the same permissions as the project so they are not in the CSV.
    assert_success_from_csv(report._csv_full_path, syn_project)


def test_it_outputs_csv_to_file(capsys, synapse_test_helper, syn_project, syn_folder, syn_file):
    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
    report = EntityPermissionsReport(syn_project.id, recursive=True, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_success_from_print(capsys, syn_project, syn_folder, syn_file)
    # Folder and File have the same permissions as the project so they are not in the CSV.
    assert_success_from_csv(report._csv_full_path, syn_project)


def test_it_reports_on_folders_by_id(capsys, syn_folder):
    EntityPermissionsReport(syn_folder.id).execute()
    assert_success_from_print(capsys, syn_folder)


def test_it_cannot_report_folders_by_name(capsys, syn_folder):
    EntityPermissionsReport(syn_folder.name).execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity.' in captured.err


def test_it_reports_on_files_by_id(capsys, syn_file):
    EntityPermissionsReport(syn_file.id).execute()
    assert_success_from_print(capsys, syn_file)


def test_it_cannot_report_files_by_name(capsys, syn_file):
    EntityPermissionsReport(syn_file.name).execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity.' in captured.err


def test_it_does_not_raise_error_on_projects_not_found(capsys, synapse_test_helper):
    for id_or_name in ['syn000', synapse_test_helper.uniq_name(prefix='DOES NOT EXIST')]:
        EntityPermissionsReport(id_or_name).execute()
        captured = capsys.readouterr()
        assert 'Entity does not exist or you do not have access to the entity.' in captured.err
