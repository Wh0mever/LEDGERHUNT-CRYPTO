import pytest

from ledgerhunt.core import evm

# EIP-55 reference vectors (from the EIP text) plus the USDT ERC-20 contract.
EIP55_VECTORS = [
    "0x5aAeb6053F3E94C9b9A09f33669435E7Ef1BeAed",
    "0xfB6916095ca1df60bB79Ce92cE3Ea74c37c5d359",
    "0xdbF03B407c01E7cD3CBea99509d93f8DDDC8C6FB",
    "0xD1220A0cf47c7B9Be7A2E6BA89F429762e7b9aDb",
    "0x52908400098527886E0F7030069857D2E4169EE7",
    "0x8617E340B3D01FA5F11F306F4090FD50E238070D",
    "0xde709f2102306220921060314715629080e2fb77",
    "0x27b1fdb04752bbc536007a920d24acb045561c26",
    evm.USDT_ERC20,
]


@pytest.mark.parametrize("addr", EIP55_VECTORS)
def test_eip55(addr):
    assert evm.to_checksum_address(addr.lower()) == addr
    assert evm.to_checksum_address(addr.upper().replace("0X", "0x")) == addr
    assert evm.is_checksum_address(addr)


def test_eip55_rejects_wrong_case_and_bad_input():
    assert not evm.is_checksum_address("0x5aaeb6053F3E94C9b9A09f33669435E7Ef1BeAed")
    with pytest.raises(ValueError):
        evm.to_checksum_address("0x1234")


def test_keccak_and_topics():
    assert evm.keccak256(b"").hex() == "c5d2460186f7233c927e7db2dcc703c0e500b653ca82273b7bfad8045d85a470"
    assert evm.event_topic("Transfer(address,address,uint256)") == evm.TRANSFER_TOPIC
    assert evm.event_topic("Approval(address,address,uint256)") == evm.APPROVAL_TOPIC
    assert evm.function_selector("balanceOf(address)") == "70a08231"
    assert evm.function_selector("transfer(address,uint256)") == "a9059cbb"


def test_words():
    word = "000000000000000000000000" + "4079047990917f3150353fbd8a13b05b6286926d"
    assert evm.word_to_address(word) == "0x4079047990917F3150353FBd8A13b05b6286926d"
    assert evm.word_to_uint("0x" + "0" * 56 + "30953fbc") == 0x30953FBC
    assert evm.word_to_int("f" * 64) == -1
    assert evm.split_words("0x" + "00" * 64) == ["0" * 64, "0" * 64]
    with pytest.raises(ValueError):
        evm.word_to_address("01" + "0" * 62)
    with pytest.raises(ValueError):
        evm.split_words("0x1234")


def test_ascii_helpers():
    # Rango destinationChainId 1414680398 is "TRON" in ASCII (case-001).
    assert evm.uint_to_ascii(1414680398) == "TRON"
    assert evm.bytes_to_ascii(b"TYHeH2\x00\x00") == "TYHeH2"
    assert evm.bytes_to_ascii(b"\x01\x02") is None


def test_dynamic_bytes():
    # abi.encode(bytes("TYHeH2")) as a single dynamic argument: offset, length, data
    payload = (
        (32).to_bytes(32, "big")
        + (6).to_bytes(32, "big")
        + b"TYHeH2".ljust(32, b"\x00")
    )
    assert evm.decode_dynamic_bytes(payload, 0) == b"TYHeH2"
    assert evm.decode_dynamic_string("0x" + payload.hex(), 0) == "TYHeH2"


def test_decode_erc20_transfer():
    log = {
        "address": evm.USDT_ERC20.lower(),
        "topics": [
            evm.TRANSFER_TOPIC,
            "0x" + "0" * 24 + "1f748c76de468e9d11bd340fa9d5cbadf315dfb0",
            "0x" + "0" * 24 + "4079047990917f3150353fbd8a13b05b6286926d",
        ],
        "data": "0x" + hex(12901408416)[2:].rjust(64, "0"),
    }
    out = evm.decode_erc20_transfer(log)
    assert out == {
        "token": evm.USDT_ERC20,
        "from": "0x1F748c76dE468e9D11bd340fA9D5CBADf315dFB0",
        "to": "0x4079047990917F3150353FBd8A13b05b6286926d",
        "value": 12901408416,
    }
    assert evm.decode_erc20_transfer({"topics": [evm.APPROVAL_TOPIC, "0x0", "0x0"]}) is None
