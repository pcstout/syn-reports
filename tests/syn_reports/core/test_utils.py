import pytest
from src.syn_reports.core import Utils


def test_eprint(capsys):
    err = 'a test error'
    Utils.eprint(err)
    captured = capsys.readouterr()
    assert err in captured.err
