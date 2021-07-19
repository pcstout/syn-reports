import pytest
import os
import csv
from src.syn_reports.commands.benefactor_permissions_report import BenefactorPermissionsReport
from src.syn_reports.core import SynapseProxy


def assert_success_from_print(capsys, *entities):
    captured = capsys.readouterr()
    assert captured.err == ''
    for entity in entities:
        log_msg = '{0}: {1} ({2})'.format(SynapseProxy.entity_type_display_name(entity),
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
    BenefactorPermissionsReport(syn_project.id).execute()
    assert_success_from_print(capsys, syn_project)


def test_it_reports_on_projects_by_name(capsys, syn_project):
    BenefactorPermissionsReport(syn_project.name).execute()
    assert_success_from_print(capsys, syn_project)


def test_it_does_not_blowup_if_entity_not_found(capsys):
    BenefactorPermissionsReport('syn000').execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity:' in captured.err


def test_it_reports_on_uniq_permissions(capsys, syn_project, syn_folder, syn_file, syn_test_helper):
    folder_team = syn_test_helper.create_team()
    file_team = syn_test_helper.create_team()
    SynapseProxy.client().setPermissions(syn_folder, folder_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    SynapseProxy.client().setPermissions(syn_file, file_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    BenefactorPermissionsReport(syn_project.name).execute()
    assert_success_from_print(capsys, syn_project, syn_folder, syn_file)


def test_it_outputs_csv_to_dir(capsys, syn_project, syn_folder, syn_file, mk_tempdir):
    out_dir = mk_tempdir()
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_dir)
    report.execute()
    assert_success_from_print(capsys, syn_project)
    # Folder and File have the same permissions as the project so they are not in the CSV.
    assert_success_from_csv(report._csv_full_path, syn_project)


def test_it_outputs_csv_to_file(capsys, syn_project, syn_folder, syn_file, mk_tempdir):
    out_file = os.path.join(mk_tempdir(), 'outfile.csv')
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_success_from_print(capsys, syn_project)
    # Folder and File have the same permissions as the project so they are not in the CSV.
    assert_success_from_csv(report._csv_full_path, syn_project)


def test_it_outputs_csv_to_file_without_entity_parent_id_for_projects(capsys, syn_test_helper,
                                                                      syn_project, syn_folder, syn_file,
                                                                      mk_tempdir):
    folder_team = syn_test_helper.create_team()
    file_team = syn_test_helper.create_team()
    SynapseProxy.client().setPermissions(syn_folder, folder_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    SynapseProxy.client().setPermissions(syn_file, file_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)

    out_file = os.path.join(mk_tempdir(), 'outfile.csv')
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_success_from_print(capsys, syn_project)

    assert_success_from_csv(report._csv_full_path, syn_project, syn_folder, syn_file)
    with open(out_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['entity_type'] == 'Project':
                assert row['entity_parent_id'] == ''
            else:
                assert row['entity_parent_id'] == syn_project.id


def test_it_reports_on_folders_by_id(capsys, syn_folder):
    BenefactorPermissionsReport(syn_folder.id).execute()
    assert_success_from_print(capsys, syn_folder)


def test_it_cannot_report_folders_by_name(capsys, syn_folder):
    BenefactorPermissionsReport(syn_folder.name).execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity:' in captured.err


def test_it_reports_on_files_by_id(capsys, syn_file):
    BenefactorPermissionsReport(syn_file.id).execute()
    assert_success_from_print(capsys, syn_file)


def test_it_cannot_report_files_by_name(capsys, syn_file):
    BenefactorPermissionsReport(syn_file.name).execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity:' in captured.err


def test_it_does_not_raise_error_on_projects_not_found(capsys, syn_test_helper):
    for id_or_name in ['syn000', syn_test_helper.uniq_name(prefix='DOES NOT EXIST')]:
        BenefactorPermissionsReport(id_or_name).execute()
        captured = capsys.readouterr()
        assert 'Entity does not exist or you do not have access to the entity:' in captured.err
