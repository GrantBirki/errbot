pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = "./src/errbot/plugins"


def test_help(testbot):
    testbot.push_message("!help")
    assert "All commands" in testbot.pop_message()


def test_version(testbot):
    testbot.push_message("!version")
    assert "test" in testbot.pop_message()

def test_ping(testbot):
    testbot.push_message("!ping")
    assert "🟢 Pong!" in testbot.pop_message()

def test_banned_users(testbot):
    testbot.push_message("!banned users")
    assert "This command is only available to bot admins." in testbot.pop_message()