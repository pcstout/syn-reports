import pytest
import os
from src.syn_reports.commands.team_members_report import TeamMembersReport


def assert_success_from_print(capsys, *teams):
    captured = capsys.readouterr()
    assert captured.err == ''
    for team in teams:
        assert 'Found team: {0} ({1}) with {2} members.'.format(team.name, team.id, 1) in captured.out


def assert_success_from_csv(csv_full_path, *teams):
    assert os.path.isfile(csv_full_path)
    with open(csv_full_path, mode='r') as f:
        contents = f.read()
        for team in teams:
            assert team.id in contents
            assert team.name in contents


def test_it_reports_on_teams_by_id(capsys, syn_team):
    TeamMembersReport(syn_team.id).execute()
    assert_success_from_print(capsys, syn_team)


def test_it_reports_on_teams_by_name(capsys, syn_team):
    TeamMembersReport(syn_team.name).execute()
    assert_success_from_print(capsys, syn_team)


def test_it_does_not_blowup_if_entity_not_found(capsys):
    TeamMembersReport('0').execute()
    captured = capsys.readouterr()
    assert 'Team does not exist or you do not have access to the team.' in captured.err


def test_it_outputs_csv_to_dir(capsys, synapse_test_helper, syn_team):
    out_dir = synapse_test_helper.create_temp_dir()
    report = TeamMembersReport(syn_team.id, out_path=out_dir)
    report.execute()
    assert_success_from_print(capsys, syn_team)
    assert_success_from_csv(report._csv_full_path, syn_team)


def test_it_outputs_csv_to_file(capsys, synapse_test_helper, syn_team):
    out_file = os.path.join(synapse_test_helper.create_temp_dir(), 'outfile.csv')
    report = TeamMembersReport(syn_team.id, out_path=out_file)
    report.execute()
    assert report._csv_full_path == out_file
    assert_success_from_print(capsys, syn_team)
    assert_success_from_csv(report._csv_full_path, syn_team)
