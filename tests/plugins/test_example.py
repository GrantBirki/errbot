pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = "./src/errbot/plugins"


def test_hello(testbot):
    testbot.push_message("!hello")
    assert "Hello, world!" in testbot.pop_message()
