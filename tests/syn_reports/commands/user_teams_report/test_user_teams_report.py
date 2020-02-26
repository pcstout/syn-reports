import pytest
import os
from src.syn_reports.commands.user_teams_report import UserTeamsReport


@pytest.fixture(scope='session')
def syn_user(syn_client):
    return syn_client.getUserProfile(os.environ.get('SYNAPSE_USERNAME'))


def assert_user_success_from_print(capsys, user, *teams):
    captured = capsys.readouterr()
    assert captured.err == ''
    assert 'Username: {0} ({1})'.format(user.userName, user.ownerId) in captured.out
    for team in teams:
        assert 'Team: {0} ({1})'.format(team.name, team.id) in captured.out


def assert_success_from_csv(csv_full_path, user, *teams):
    assert os.path.isfile(csv_full_path)
    with open(csv_full_path, mode='r') as f:
        contents = f.read()
        assert user.ownerId in contents
        assert user.userName in contents
        for team in teams:
            assert team.id in contents
            assert team.name in contents


def test_it_reports_by_user_id(capsys, syn_user, syn_team):
    UserTeamsReport(syn_user.ownerId).execute()
    assert_user_success_from_print(capsys, syn_user, syn_team)


def test_it_reports_by_username(capsys, syn_user, syn_team):
    UserTeamsReport(syn_user.userName).execute()
    assert_user_success_from_print(capsys, syn_user, syn_team)


def test_it_does_not_blowup_if_user_not_found(capsys, syn_test_helper):
    username = syn_test_helper.uniq_name(prefix='Invalid-User')
    UserTeamsReport(username).execute()
    captured = capsys.readouterr()
    assert 'Could not find user matching: {0}'.format(username) in captured.err


def test_it_outputs_csv_to_dir(capsys, syn_user, syn_team, mk_tempdir):
    out_dir = mk_tempdir()
    report = UserTeamsReport(syn_user.userName, out_path=out_dir)
    report.execute()
    assert_user_success_from_print(capsys, syn_user, syn_team)
    assert_success_from_csv(report._csv_full_path, syn_user, syn_team)


def test_it_outputs_csv_to_file(capsys, syn_user, syn_team, mk_tempdir):
    out_file = os.path.join(mk_tempdir(), 'outfile.csv')
    report = UserTeamsReport(syn_user.userName, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_user_success_from_print(capsys, syn_user, syn_team)
    assert_success_from_csv(report._csv_full_path, syn_user, syn_team)
