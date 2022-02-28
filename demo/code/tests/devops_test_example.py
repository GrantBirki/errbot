pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = "./src/errbot/plugins"


def test_devops(testbot):
    testbot.push_message("!devops")
    assert "demo/assets/devops.jpg" in testbot.pop_message()
