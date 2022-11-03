import pytest
import os
import csv
import json
from src.syn_reports.commands.benefactor_permissions_report import BenefactorPermissionsReport
from src.syn_reports.core import SynapseProxy, Utils


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


def test_it_reports_on_all_accessible_projects(capsys, syn_project, syn_project2, mocker):
    mocker.patch('src.syn_reports.core.synapse_proxy.SynapseProxy.users_project_access',
                 return_value=iter([syn_project, syn_project2]))
    BenefactorPermissionsReport(None).execute()
    assert_success_from_print(capsys, syn_project, syn_project2)


def test_it_does_not_blowup_if_entity_not_found(capsys):
    BenefactorPermissionsReport('syn000').execute()
    captured = capsys.readouterr()
    assert 'Entity does not exist or you do not have access to the entity:' in captured.err


def test_it_reports_on_uniq_permissions(capsys, syn_project, syn_folder, syn_file, synapse_test_helper):
    folder_team = synapse_test_helper.create_team()
    file_team = synapse_test_helper.create_team()
    SynapseProxy.client().setPermissions(syn_folder, folder_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    SynapseProxy.client().setPermissions(syn_file, file_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    BenefactorPermissionsReport(syn_project.name).execute()
    assert_success_from_print(capsys, syn_project, syn_folder, syn_file)


def test_it_outputs_csv_to_dir(capsys, synapse_test_helper, syn_project, syn_folder, syn_file):
    out_dir = synapse_test_helper.create_temp_dir()
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_dir)
    report.execute()
    assert_success_from_print(capsys, syn_project)
    # Folder and File have the same permissions as the project so they are not in the CSV.
    assert_success_from_csv(report._csv_full_path, syn_project)


def test_it_outputs_csv_to_file(capsys, synapse_test_helper, syn_project, syn_folder, syn_file):
    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_success_from_print(capsys, syn_project)
    # Folder and File have the same permissions as the project so they are not in the CSV.
    assert_success_from_csv(report._csv_full_path, syn_project)


def test_it_creates_csv_files_for_each_entity(capsys, synapse_test_helper, syn_project, syn_project2):
    out_dir = synapse_test_helper.create_temp_dir()
    report = BenefactorPermissionsReport([syn_project.id, syn_project2.id], out_path=out_dir, out_file_per_entity=True)
    report.execute()
    assert_success_from_print(capsys, syn_project, syn_project2)
    assert len(report.csv_files_created) == 2
    for csv_file in report.csv_files_created:
        if syn_project.name in csv_file:
            assert_success_from_csv(csv_file, syn_project)
        else:
            assert_success_from_csv(csv_file, syn_project2)


def test_it_uses_the_out_file_prefix(capsys, synapse_test_helper, syn_project):
    out_dir = synapse_test_helper.create_temp_dir()
    prefix = 'ZzZzZzZz--'
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_dir, out_file_prefix=prefix)
    report.execute()
    assert_success_from_print(capsys, syn_project)
    for csv_file in report.csv_files_created:
        assert os.path.basename(csv_file).startswith(prefix)


def test_it_does_not_add_timestamp_to_out_file_name(capsys, synapse_test_helper, syn_project):
    out_dir = synapse_test_helper.create_temp_dir()
    partial_timestamp = Utils.timestamp_str()[:8]
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_dir, out_file_without_timestamp=True)
    report.execute()
    assert_success_from_print(capsys, syn_project)
    for csv_file in report.csv_files_created:
        assert partial_timestamp not in csv_file


def test_it_trims_the_out_file_name(capsys, synapse_test_helper, syn_project):
    out_dir = synapse_test_helper.create_temp_dir()
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_dir, out_file_name_max_length=3)
    report.execute()
    assert_success_from_print(capsys, syn_project)
    for csv_file in report.csv_files_created:
        assert len(os.path.basename(csv_file)) == (3 + len('.csv'))


def test_it_outputs_csv_to_file_without_entity_parent_id_for_projects(capsys, synapse_test_helper,
                                                                      syn_project, syn_folder, syn_file):
    folder_team = synapse_test_helper.create_team()
    file_team = synapse_test_helper.create_team()
    SynapseProxy.client().setPermissions(syn_folder, folder_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    SynapseProxy.client().setPermissions(syn_file, file_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)

    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
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


def test_it_outputs_team_invites_by_user_to_csv(synapse_test_helper, syn_project):
    project_team = synapse_test_helper.create_team()
    SynapseProxy.client().setPermissions(syn_project, project_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    invite_user_id = os.environ.get('TEST_OTHER_SYNAPSE_USER_ID')
    invite_user = SynapseProxy.client().getUserProfile(invite_user_id)
    body = {
        'teamId': project_team.id,
        'inviteeId': invite_user_id
    }
    SynapseProxy.client().restPOST('/membershipInvitation', body=json.dumps(body))

    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_file)
    report.execute()
    csv_passed = False
    with open(out_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == invite_user['userName']:
                assert row['principal_type'] == 'Invite'
                assert row['team_id'] == project_team.id
                assert row['user_id'] == invite_user_id
                csv_passed = True
    assert csv_passed is True


def test_it_outputs_team_invites_by_email_to_csv(synapse_test_helper, syn_project):
    project_team = synapse_test_helper.create_team()
    SynapseProxy.client().setPermissions(syn_project, project_team.id,
                                         accessType=SynapseProxy.Permissions.CAN_EDIT_AND_DELETE,
                                         warn_if_inherits=False)
    invite_user_email = os.environ.get('TEST_EMAIL')
    body = {
        'teamId': project_team.id,
        'inviteeEmail': invite_user_email
    }
    SynapseProxy.client().restPOST('/membershipInvitation', body=json.dumps(body))

    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
    report = BenefactorPermissionsReport(syn_project.id, out_path=out_file)
    report.execute()
    csv_passed = False
    with open(out_file, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            if row['username'] == invite_user_email:
                assert row['principal_type'] == 'Invite'
                assert row['team_id'] == project_team.id
                assert row['user_id'] == ''
                csv_passed = True
    assert csv_passed is True


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


def test_it_does_not_raise_error_on_projects_not_found(capsys, synapse_test_helper):
    for id_or_name in ['syn000', synapse_test_helper.uniq_name(prefix='DOES NOT EXIST')]:
        BenefactorPermissionsReport(id_or_name).execute()
        captured = capsys.readouterr()
        assert 'Entity does not exist or you do not have access to the entity:' in captured.err
