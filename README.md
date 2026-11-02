# sablehash

Pure-Python EIP-712 typed-data hashing. `typedhash.typed_data_digest(typed_data)` returns the 32-byte digest a wallet signs for `eth_signTypedData_v4`, as a `0x`-prefixed hex string.

```python
from typedhash import typed_data_digest

digest = typed_data_digest({
    "types": {
        "EIP712Domain": [{"name": "name", "type": "string"}, {"name": "chainId", "type": "uint256"}],
        "Mail": [{"name": "to", "type": "address"}, {"name": "contents", "type": "string"}],
    },
    "primaryType": "Mail",
    "domain": {"name": "Mail", "chainId": 1},
    "message": {"to": "0x0000000000000000000000000000000000000001", "contents": "hi"},
})
```

Depends only on `pycryptodome` for keccak256.

## Install

```
pip install .
```

## License

MIT
