def test_it_returns_success(expect_cli_exit_code, syn_client):
    expect_cli_exit_code('user-project-access', 0, syn_client.getUserProfile().ownerId)


def test_it_returns_failure(expect_cli_exit_code):
    expect_cli_exit_code('user-project-access', 1, '000000')
