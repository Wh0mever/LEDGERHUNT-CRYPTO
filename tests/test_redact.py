from ledgerhunt.core.redact import (
    clear_registered_secrets,
    contains_registered_secret,
    redact,
    redact_bytes,
    redact_obj,
    register_secret,
)

FAKE = "fake-secret-value-0123456789abcdef"


def test_registered_secret_replaced_everywhere():
    register_secret(FAKE)
    assert redact(f"prefix {FAKE} suffix") == "prefix *** suffix"
    assert FAKE not in redact_obj({"a": [FAKE, {"b": f"x{FAKE}y"}]}).__repr__()
    assert contains_registered_secret(FAKE.encode())
    assert redact_bytes(b"k=" + FAKE.encode()) == b"k=***"
    clear_registered_secrets()
    assert redact(FAKE) == FAKE


def test_url_secret_parts_registered():
    url = "https://tron-mainnet.example-provider.com/a1b2c3d4e5f6a7b8c9d0e1f2/"
    register_secret(url)
    assert redact(url + "wallet/getnowblock") == "***/wallet/getnowblock"
    # the embedded key alone is also caught (URL rebuilt differently)
    assert "a1b2c3d4e5f6a7b8c9d0e1f2" not in redact("https://other/a1b2c3d4e5f6a7b8c9d0e1f2/x")


def test_patterns_without_registration():
    assert redact("key sk-ant-api03-AbCdEf_123-xyz end") == "key *** end"
    assert redact("TRON-PRO-API-KEY: 1234-abcd-5678") == "TRON-PRO-API-KEY: ***"
    assert redact('{"TRON-PRO-API-KEY": "1234-abcd"}') == '{"TRON-PRO-API-KEY": "***"}'
    assert redact("{'x-api-key': 'abc123'}") == "{'x-api-key': '***'}"
    assert redact("Authorization: Bearer abc.def.ghi") == "Authorization: ***"
    assert redact("https://h/x?apikey=ZZZ&module=account") == "https://h/x?apikey=***&module=account"
    assert redact("https://h/x?a=1&api_key=ZZZ") == "https://h/x?a=1&api_key=***"
    assert redact("https://h/x?key=ZZZ") == "https://h/x?key=***"
    assert redact("https://h/x?token=ZZZ") == "https://h/x?token=***"


def test_patterns_do_not_eat_public_data():
    # token filters with a public address stay intact (Blockscout ?token=0x...)
    u = "https://eth.blockscout.com/api/v2/addresses/0xabc/token-transfers?token=0xdAC17F958D2ee523a2206206994597C13D831ec7"
    assert redact(u) == u
    # booleans in presence maps are not secrets
    s = '{"ANTHROPIC_API_KEY": true, "TRONGRID_API_KEY": false}'
    assert redact(s) == s
    # a longer word ending in a secret-ish name is not treated as a header
    assert redact("monkey=banana") == "monkey=banana"
    assert redact("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t") == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"


def test_env_style_assignment_redacted():
    assert redact("SOME_API_KEY=abcdef123") == "SOME_API_KEY=***"
    assert redact("CLIENT_SECRET: hunter2") == "CLIENT_SECRET: ***"
