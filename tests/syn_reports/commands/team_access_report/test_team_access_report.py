import pytest
from src.syn_reports.commands.team_access_report import TeamAccessReport


def test_it_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        TeamAccessReport('0').execute()
