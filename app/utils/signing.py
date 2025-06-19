from dataclasses import dataclass


@dataclass
class KeyStoreInfo:
    keystore_path: str
    key_alias: str
    key_store_pass: str
    key_pass: str
