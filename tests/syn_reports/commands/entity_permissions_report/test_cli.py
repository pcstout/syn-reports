def test_it_returns_success(expect_cli_exit_code, syn_project):
    expect_cli_exit_code('entity-permissions', 0, syn_project.id)


def test_it_returns_failure(expect_cli_exit_code):
    expect_cli_exit_code('entity-permissions', 1, 'syn00000')
