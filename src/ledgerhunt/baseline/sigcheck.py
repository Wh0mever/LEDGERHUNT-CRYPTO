"""Recover the signer of a TRON transaction (secp256k1 public-key recovery, pure Python).

A TRON transaction id is sha256(raw_data bytes); each signature is 65 bytes r || s || v and
signs that id. Recovering the public key and deriving the address (0x41 + last 20 bytes of
keccak256(X || Y)) shows which key actually signed. Used to check the "signed with the
victim's own owner key" claim from raw data only. Read-only math, no secrets involved.
"""

from __future__ import annotations

import hashlib

from ..core.evm import keccak256
from ..core.tron import hex_to_b58

# secp256k1 domain parameters (SEC 2)
_P = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
_N = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
_G = (
    0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798,
    0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8,
)

Point = tuple[int, int] | None


def _add(a: Point, b: Point) -> Point:
    if a is None:
        return b
    if b is None:
        return a
    if a[0] == b[0] and (a[1] + b[1]) % _P == 0:
        return None
    if a == b:
        lam = 3 * a[0] * a[0] * pow(2 * a[1], -1, _P) % _P
    else:
        lam = (b[1] - a[1]) * pow(b[0] - a[0], -1, _P) % _P
    x = (lam * lam - a[0] - b[0]) % _P
    return x, (lam * (a[0] - x) - a[1]) % _P


def _mul(k: int, pt: Point) -> Point:
    result: Point = None
    addend = pt
    while k:
        if k & 1:
            result = _add(result, addend)
        addend = _add(addend, addend)
        k >>= 1
    return result


def recover_public_key(msg_hash: bytes, signature: bytes) -> tuple[int, int]:
    """Public key (x, y) that produced ``signature`` (r||s||v, 65 bytes) over ``msg_hash``."""
    if len(signature) != 65 or len(msg_hash) != 32:
        raise ValueError("expected a 32-byte hash and a 65-byte signature")
    r = int.from_bytes(signature[:32], "big")
    s = int.from_bytes(signature[32:64], "big")
    v = signature[64]
    recid = v - 27 if v >= 27 else v
    if not (0 < r < _N and 0 < s < _N and 0 <= recid <= 3):
        raise ValueError("signature values out of range")
    x = r + (recid >> 1) * _N
    y = pow((pow(x, 3, _P) + 7) % _P, (_P + 1) // 4, _P)
    if y % 2 != recid & 1:
        y = _P - y
    z = int.from_bytes(msg_hash, "big")
    r_inv = pow(r, -1, _N)
    q = _add(_mul(s * r_inv % _N, (x, y)), _mul((-z * r_inv) % _N, _G))
    if q is None:
        raise ValueError("recovered point at infinity")
    return q


def tron_address_from_public_key(pub: tuple[int, int]) -> str:
    raw = pub[0].to_bytes(32, "big") + pub[1].to_bytes(32, "big")
    return hex_to_b58("41" + keccak256(raw)[-20:].hex())


def check_tron_signatures(tx: dict) -> dict:
    """txID integrity and the signer address of every signature of a gettransactionbyid answer."""
    raw_hex = tx.get("raw_data_hex") or ""
    txid = tx.get("txID") or ""
    computed = hashlib.sha256(bytes.fromhex(raw_hex)).hexdigest() if raw_hex else None
    signers = []
    for sig in tx.get("signature") or []:
        try:
            signers.append(tron_address_from_public_key(recover_public_key(bytes.fromhex(txid), bytes.fromhex(sig))))
        except ValueError as exc:
            signers.append(f"unrecoverable: {exc}")
    return {
        "txid_matches_raw_data": computed == txid if computed else None,
        "signature_count": len(tx.get("signature") or []),
        "signers": signers,
    }
