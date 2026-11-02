import re

from Crypto.Hash import keccak

ARRAY_RE = re.compile(r"^(.*)\[(\d*)\]$")


def keccak256(data):
    h = keccak.new(digest_bits=256)
    h.update(data)
    return h.digest()


def to_bytes(value):
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    if isinstance(value, str) and value.startswith("0x"):
        return bytes.fromhex(value[2:])
    raise ValueError(f"cannot convert {value!r} to bytes")


def to_int(value):
    if isinstance(value, bool):
        return int(value)
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        return int(value, 16) if value.lower().startswith("0x") else int(value)
    raise ValueError(f"cannot convert {value!r} to int")


def base_type(type_name):
    while ARRAY_RE.match(type_name):
        type_name = ARRAY_RE.match(type_name).group(1)
    return type_name


def find_dependencies(primary, types, found=None):
    if found is None:
        found = []
    if primary in found or primary not in types:
        return found
    found.append(primary)
    for field in types[primary]:
        find_dependencies(field["type"], types, found)
    return found


def encode_type(primary, types):
    ordered = sorted(find_dependencies(primary, types))
    return "".join(
        name + "(" + ",".join(f'{f["type"]} {f["name"]}' for f in types[name]) + ")"
        for name in ordered
    )


def type_hash(primary, types):
    return keccak256(encode_type(primary, types).encode())


def encode_value(type_name, value, types):
    match = ARRAY_RE.match(type_name)
    if match:
        item_type = match.group(1)
        if item_type in types:
            return keccak256(b"".join(encode_data(item_type, v, types) for v in value))
        return keccak256(b"".join(encode_value(item_type, v, types) for v in value))
    if type_name in types:
        return hash_struct(type_name, value, types)
    if type_name == "string":
        return keccak256(value.encode())
    if type_name == "bytes":
        return keccak256(to_bytes(value))
    if type_name.startswith("bytes"):
        return to_bytes(value).rjust(32, b"\0")
    if type_name == "bool":
        return to_int(bool(value)).to_bytes(32, "big")
    if type_name == "address":
        return to_bytes(value).rjust(32, b"\0")
    if type_name.startswith("uint"):
        return to_int(value).to_bytes(32, "big")
    if type_name.startswith("int"):
        bits = int(type_name[3:] or 256)
        return (to_int(value) % (1 << bits)).to_bytes(32, "big")
    raise ValueError(f"unsupported type {type_name}")


def encode_data(primary, data, types):
    return type_hash(primary, types) + b"".join(
        encode_value(f["type"], data[f["name"]], types) for f in types[primary]
    )


def hash_struct(primary, data, types):
    return keccak256(encode_data(primary, data, types))


DOMAIN_FIELD_TYPES = {
    "name": "string",
    "version": "string",
    "chainId": "uint256",
    "verifyingContract": "address",
    "salt": "bytes32",
}


def domain_separator(typed_data):
    domain = typed_data["domain"]
    types = dict(typed_data["types"])
    types["EIP712Domain"] = [{"name": k, "type": DOMAIN_FIELD_TYPES[k]} for k in domain]
    return hash_struct("EIP712Domain", domain, types)


def typed_data_digest(typed_data):
    types = typed_data["types"]
    return "0x" + keccak256(
        b"\x19\x01"
        + domain_separator(typed_data)
        + hash_struct(typed_data["primaryType"], typed_data["message"], types)
    ).hex()
