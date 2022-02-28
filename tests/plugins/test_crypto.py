pytest_plugins = ["errbot.backends.test"]

extra_plugin_dir = "./src/errbot/plugins"


def test_crypto(requests_mock, testbot):
    requests_mock.get(
        "https://min-api.cryptocompare.com/data/price?fsym=btc&tsyms=USD",
        json={"USD": "1.00"},
    )
    testbot.push_message("!crypto btc")
    assert "$1.00" in testbot.pop_message()


def test_crypto_with_error(requests_mock, testbot):
    requests_mock.get(
        "https://min-api.cryptocompare.com/data/price?fsym=evilcrypto&tsyms=USD",
        json={
            "Response": "Error",
            "Message": "market does not exist for this coin pair (EVILCRYPTO-USD)",
        },
    )
    testbot.push_message("!crypto evilcrypto")
    assert "not a valid crypto currency" in testbot.pop_message()
