pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = './src/errbot/plugins'

def test_help(testbot):
    testbot.push_message('!help')
    assert 'All commands' in testbot.pop_message()

def test_version(testbot):
    testbot.push_message('!version')
    assert 'testa' in testbot.pop_message()
