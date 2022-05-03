import pytest
import os
from src.syn_reports.commands.user_project_access_report import UserProjectAccessReport


@pytest.fixture(scope='session')
def syn_user(syn_client):
    return syn_client.getUserProfile(os.environ.get('SYNAPSE_USERNAME'))


def assert_user_success_from_print(capsys, *users):
    captured = capsys.readouterr()
    assert captured.err == ''
    for user in users:
        assert 'Username: {0} ({1})'.format(user.userName, user.ownerId) in captured.out


def assert_project_success_from_print(capsys, *projects):
    captured = capsys.readouterr()
    assert captured.err == ''
    for project in projects:
        'Project: {0} ({1}) [{2}]'.format(project.name, project.id, 'Adminitrator') in captured.out


def assert_success_from_csv(csv_full_path, user, *entities):
    assert os.path.isfile(csv_full_path)
    with open(csv_full_path, mode='r') as f:
        contents = f.read()
        assert user.ownerId in contents
        assert user.userName in contents
        for entity in entities:
            assert entity.id in contents
            assert entity.name in contents


def test_it_reports_by_user_id(capsys, syn_user, syn_project):
    UserProjectAccessReport(syn_user.ownerId).execute()
    assert_user_success_from_print(capsys, syn_user)
    assert_project_success_from_print(capsys, syn_project)


def test_it_reports_by_username(capsys, syn_user, syn_project):
    UserProjectAccessReport(syn_user.userName).execute()
    assert_user_success_from_print(capsys, syn_user)
    assert_project_success_from_print(capsys, syn_project)


def test_it_does_not_blowup_if_user_not_found(capsys, synapse_test_helper):
    username = synapse_test_helper.uniq_name(prefix='Invalid-User')
    UserProjectAccessReport(username).execute()
    captured = capsys.readouterr()
    assert 'Could not find user matching: {0}'.format(username) in captured.err


def test_it_outputs_csv_to_dir(capsys, synapse_test_helper, syn_user, syn_project):
    out_dir = synapse_test_helper.create_temp_dir()
    report = UserProjectAccessReport(syn_user.userName, out_path=out_dir)
    report.execute()
    assert_user_success_from_print(capsys, syn_user)
    assert_project_success_from_print(capsys, syn_project)
    assert_success_from_csv(report._csv_full_path, syn_user, syn_project)


def test_it_outputs_csv_to_file(capsys, synapse_test_helper, syn_user, syn_project):
    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
    report = UserProjectAccessReport(syn_user.userName, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_user_success_from_print(capsys, syn_user)
    assert_project_success_from_print(capsys, syn_project)
    assert_success_from_csv(report._csv_full_path, syn_user, syn_project)
