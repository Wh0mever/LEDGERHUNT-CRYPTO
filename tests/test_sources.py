import json

import httpx
import pytest

from ledgerhunt.core.http import RecordingClient
from ledgerhunt.core.redact import register_secret
from ledgerhunt.sources import (
    BlockscoutClient,
    EthRpcClient,
    JsonRpcError,
    LayerZeroScanClient,
    SourceError,
    TronGridClient,
    TronNodeClient,
    is_empty,
)

FAKE_KEY = "fake-tg-key-a1b2c3d4e5f6"


def client(tmp_path, handler, **kw):
    return RecordingClient(
        transport=httpx.MockTransport(handler),
        store_dir=tmp_path / "store",
        shared_limiter=False,
        default_rps=0,
        rate_limits={"api.trongrid.io": 0, "eth.blockscout.com": 0},
        sleep=lambda s: None,
        mode=kw.pop("mode", "record"),
        **kw,
    )


def test_trongrid_pagination_key_header_and_rate_bucket(tmp_path):
    register_secret(FAKE_KEY)
    seen = []

    def handler(r: httpx.Request) -> httpx.Response:
        seen.append((r.headers.get("TRON-PRO-API-KEY"), dict(r.url.params)))
        if "fingerprint" not in r.url.params:
            return httpx.Response(200, json={"data": [{"transaction_id": "a", "value": "1"}], "success": True,
                                             "meta": {"fingerprint": "FP1", "page_size": 1}})
        return httpx.Response(200, json={"data": [{"transaction_id": "b", "value": "2"}], "success": True,
                                         "meta": {"page_size": 1}})

    http = client(tmp_path, handler)
    tg = TronGridClient(http, api_key=FAKE_KEY)
    assert tg.has_key and tg._rate_key == "api.trongrid.io#key"
    assert http.limiter.rate_for("api.trongrid.io#key") == 10.0
    paged = tg.trc20_transfers("TYGdh7qysHLr3A4gVGivcRwSg79PpVzgNn", limit=1)
    assert paged.complete and [r["transaction_id"] for r in paged.rows] == ["a", "b"]
    assert len(paged.refs) == 2
    assert all(h == FAKE_KEY for h, _ in seen)
    assert seen[0][1]["contract_address"] == "TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t"
    assert seen[1][1]["fingerprint"] == "FP1"
    index = (tmp_path / "store" / "index.jsonl").read_text(encoding="utf-8")
    assert FAKE_KEY not in index and '"provider": "trongrid"' in index.replace('":"', '": "')
    assert http.metrics[0]["rate_key"] == "api.trongrid.io#key"


def test_trongrid_keyless_and_max_pages(tmp_path):
    def handler(r):
        return httpx.Response(200, json={"data": [1], "success": True, "meta": {"fingerprint": "next"}})

    tg = TronGridClient(client(tmp_path, handler), api_key=None)
    assert not tg.has_key and tg._rate_key == "api.trongrid.io"
    paged = tg.account_transactions("TNakrL7VUMLNN4EEpi64HKjj5YqafR5tUx", max_pages=2)
    assert not paged.complete and len(paged.pages) == 2


def test_trongrid_success_false_raises(tmp_path):
    tg = TronGridClient(client(tmp_path, lambda r: httpx.Response(200, json={"success": False, "error": "x"})),
                        api_key=None)
    with pytest.raises(SourceError):
        tg.transaction_events("a" * 64)


def test_tron_node_empty_and_balance(tmp_path):
    def handler(r):
        body = json.loads(r.content)
        if r.url.path.endswith("gettransactionbyid"):
            return httpx.Response(200, json={})
        assert body["function_selector"] == "balanceOf(address)"
        assert len(body["parameter"]) == 64
        return httpx.Response(200, json={"constant_result": ["00" * 31 + "2a"], "result": {"result": True}})

    node = TronNodeClient(client(tmp_path, handler), base_url="https://tron-rpc.publicnode.com")
    assert is_empty(node.get_transaction_by_id("a" * 64))
    value, f = node.trc20_balance_of("TYHeH2HQn7pM5fe6aYwGabz9x4yizJbwp6")
    assert value == 42 and f.ref is not None


def test_eth_rpc_result_and_error(tmp_path):
    def handler(r):
        body = json.loads(r.content)
        assert body["id"] == 1
        if body["method"] == "eth_blockNumber":
            return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "result": "0x10"})
        return httpx.Response(200, json={"jsonrpc": "2.0", "id": 1, "error": {"code": -32000, "message": "nope"}})

    eth = EthRpcClient(client(tmp_path, handler))
    n, f = eth.block_number()
    assert n == 16 and f.data == "0x10"
    with pytest.raises(JsonRpcError):
        eth.get_transaction_receipt("0x" + "0" * 64)
    assert eth.http.metrics[0]["endpoint"] == "jsonrpc/eth_blockNumber"


def test_layerzero_adds_0x_and_returns_404(tmp_path):
    paths = []

    def handler(r):
        paths.append(r.url.path)
        return httpx.Response(404, json={"message": "Message not found", "code": 4040})

    lz = LayerZeroScanClient(client(tmp_path, handler))
    f = lz.messages_by_tx("b" * 64)
    assert f.status == 404 and paths == ["/v1/messages/tx/0x" + "b" * 64]


def test_blockscout_pagination(tmp_path):
    def handler(r):
        if "block_number" in r.url.params:
            return httpx.Response(200, json={"items": [{"i": 2}], "next_page_params": None})
        return httpx.Response(200, json={"items": [{"i": 1}], "next_page_params": {"block_number": 5, "index": 1}})

    bs = BlockscoutClient(client(tmp_path, handler), api_key=None)
    paged = bs.address_token_transfers("0x4079047990917F3150353FBd8A13b05b6286926d")
    assert paged.complete and [r["i"] for r in paged.rows] == [1, 2]
