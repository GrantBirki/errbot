pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = "./src/errbot/plugins"


def test_crypto(requests_mock, testbot):
    requests_mock.get(
        "https://min-api.cryptocompare.com/data/price?fsym=btc&tsyms=USD",
        json={"USD": "1.00"},
    )
    testbot.push_message("!crypto btc")
    assert "$1.00" in testbot.pop_message()
