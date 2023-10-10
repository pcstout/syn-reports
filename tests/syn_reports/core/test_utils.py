import pytest
from syn_reports.core import Utils
from synapsis import Synapsis
import synapseclient as syn


def test_eprint(capsys):
    err = 'a test error'
    Utils.eprint(err)
    captured = capsys.readouterr()
    assert err in captured.err


def test_with_cache_get_user(synapse_test_helper):
    user_id = Synapsis.getUserProfile().get('ownerId')
    user = Utils.WithCache.get_user(user_id)
    assert user['ownerId'] == user_id

    # Returns None if the user does not exist
    assert Utils.WithCache.get_user('-9999999') is None
    assert Utils.WithCache.get_user('000') is None
    assert Utils.WithCache.get_user(synapse_test_helper.uniq_name(prefix='notarealname')) is None


def test_with_cache_get_team(synapse_test_helper):
    team = synapse_test_helper.create_team()
    team_id = team.get('id')
    team_name = team.get('name')

    team = Utils.WithCache.get_team(team_id)
    assert team['id'] == team_id

    team = Utils.WithCache.get_team(team_name)
    assert team['id'] == team_id

    # Returns None if the team does not exist
    assert Utils.WithCache.get_team('-9999999') is None
    assert Utils.WithCache.get_team('000') is None
    assert Utils.WithCache.get_team(synapse_test_helper.uniq_name(prefix='notarealname')) is None


def test_with_cache_get_user_or_team(synapse_test_helper):
    user_id = Synapsis.getUserProfile().get('ownerId')
    team_id = synapse_test_helper.create_team().get('id')

    user = Utils.WithCache.get_user_or_team(user_id)
    assert isinstance(user, syn.UserProfile)
    assert user['ownerId'] == user_id

    team = Utils.WithCache.get_user_or_team(team_id)
    assert isinstance(team, syn.Team)
    assert team['id'] == team_id

    # Returns None if the user and team do not exist
    assert Utils.WithCache.get_user_or_team('-9999999') is None
    assert Utils.WithCache.get_user_or_team('000') is None
    assert Utils.WithCache.get_user_or_team(synapse_test_helper.uniq_name(prefix='notarealname')) is None
    assert Utils.WithCache.get_user_or_team(synapse_test_helper.uniq_name(prefix='notarealname')) is None


def test_with_cache_get_team_members(synapse_test_helper):
    team = synapse_test_helper.create_team()
    members = Utils.WithCache.get_team_members(team.id)
    assert len(members) == 1

    # Returns [] if the team does not exist
    assert Utils.WithCache.get_team_members('-9999999') == []
    assert Utils.WithCache.get_team_members('000') == []
