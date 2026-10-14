from decimal import Decimal

import pytest

from ledgerhunt.core import tron


def test_usdt_contract_b58_hex_roundtrip():
    assert tron.b58_to_hex(tron.USDT_TRC20) == tron.USDT_TRC20_HEX
    assert tron.hex_to_b58(tron.USDT_TRC20_HEX) == tron.USDT_TRC20
    assert tron.hex_to_b58("0x" + tron.USDT_TRC20_HEX[2:]) == tron.USDT_TRC20
    assert tron.hex_to_b58(tron.USDT_TRC20_HEX[2:]) == tron.USDT_TRC20
    assert tron.b58_to_evm_hex(tron.USDT_TRC20) == "0x" + tron.USDT_TRC20_HEX[2:]


def test_word_conversion_roundtrip():
    word = tron.address_to_word(tron.USDT_TRC20)
    assert len(word) == 64 and word.startswith("0" * 24)
    assert tron.word_to_b58(word) == tron.USDT_TRC20
    assert tron.word_to_b58("0x" + word) == tron.USDT_TRC20


@pytest.mark.parametrize(
    "addr",
    [
        "TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx",
        "TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn",
        "TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6",
        "TFG4wBaDQ8sHWWP1ACeSGnoNR6RRzevLPt",
    ],
)
def test_case001_addresses_roundtrip(addr):
    assert tron.is_valid_address(addr)
    assert tron.hex_to_b58(tron.b58_to_hex(addr)) == addr
    assert tron.to_b58(tron.b58_to_hex(addr)) == addr


def test_checksum_validation_rejects_typo():
    bad = "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6u"  # last char changed
    with pytest.raises(tron.InvalidTronAddress):
        tron.b58_to_hex(bad)
    assert not tron.is_valid_address(bad)
    assert not tron.is_valid_address("0x1234")
    with pytest.raises(tron.InvalidTronAddress):
        tron.hex_to_b58("42" + "00" * 20)  # wrong prefix


def test_format_amount_exact():
    assert tron.format_amount(13041400772) == "13041.400772"
    assert tron.format_amount("12878454902") == "12878.454902"
    assert tron.format_amount(5) == "0.000005"
    assert tron.format_amount(0) == "0.000000"
    assert tron.format_amount(-1500000) == "-1.500000"
    assert tron.format_amount(345000, tron.TRX_DECIMALS) == "0.345000"
    with pytest.raises(TypeError):
        tron.format_amount(1.5)  # floats never accepted


def test_parse_amount_exact():
    assert tron.parse_amount("13041.400772") == 13041400772
    assert tron.parse_amount("162.94587") == 162945870
    assert tron.parse_amount(Decimal("0.000001")) == 1
    with pytest.raises(ValueError):
        tron.parse_amount("0.0000001")
    with pytest.raises(TypeError):
        tron.parse_amount(0.1)
    assert tron.to_decimal(130356401) == Decimal("130.356401")
