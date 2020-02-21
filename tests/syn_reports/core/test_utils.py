import pytest
from src.syn_reports.core import Utils


def test_is_synapse_id():
    assert Utils.is_synapse_id('SyN1230') is True
    assert Utils.is_synapse_id('  sYn1230  ') is True
    assert Utils.is_synapse_id('syn') is False
    assert Utils.is_synapse_id('syn 1230') is False
    assert Utils.is_synapse_id('1230') is False
    assert Utils.is_synapse_id('1230syn') is False


def test_eprint(capsys):
    err = 'a test error'
    Utils.eprint(err)
    captured = capsys.readouterr()
    assert err in captured.err
