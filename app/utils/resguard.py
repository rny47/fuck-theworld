"""Simplified replacement for AndResGuard."""
import os
import random
import re
import shutil
import tempfile
import xml.etree.ElementTree as ET

from app.utils.common import CommandUtils
from app.utils.signing import KeyStoreInfo


def _random_name() -> str:
    return ''.join(random.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=7))


def _rename_resources(res_dir: str) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for root, _, files in os.walk(res_dir):
        for f in files:
            name, ext = os.path.splitext(f)
            if not name:
                continue
            new_name = _random_name()
            while new_name in mapping.values():
                new_name = _random_name()
            mapping[name] = new_name
            os.rename(os.path.join(root, f), os.path.join(root, new_name + ext))
    return mapping


def _replace_references(target_dir: str, mapping: dict[str, str]) -> None:
    for root, _, files in os.walk(target_dir):
        for f in files:
            if f.endswith(('.xml', '.smali')):
                file_path = os.path.join(root, f)
                with open(file_path, 'r', encoding='utf-8') as fh:
                    content = fh.read()
                for old, new in mapping.items():
                    content = re.sub(r'\b' + re.escape(old) + r'\b', new, content)
                with open(file_path, 'w', encoding='utf-8') as fh:
                    fh.write(content)


def _parse_config(config_path: str | None) -> dict:
    opts = {"sevenzip": False}
    if config_path and os.path.exists(config_path):
        try:
            root = ET.parse(config_path).getroot()
            prop = root.find("./issue[@id='property']/seventzip")
            if prop is not None and prop.attrib.get('value') == 'true':
                opts["sevenzip"] = True
        except Exception:
            pass
    return opts


def _write_mapping(mapping: dict[str, str], mapping_path: str) -> None:
    with open(mapping_path, "w", encoding="utf-8") as fh:
        for old, new in mapping.items():
            fh.write(f"{old}->{new}\n")


def _sevenzip_if_needed(src: str, dest: str) -> None:
    if shutil.which("7z"):
        CommandUtils.run_system_command(f"7z a -tzip -mx9 {dest} {src}")
        os.replace(dest, src)


def resguard_sign(apk_path: str, keystore_info: KeyStoreInfo, config_path: str | None = None) -> str:
    """Obfuscate resources and sign the APK with optional 7zip compression."""
    work_dir = tempfile.mkdtemp()
    decompiled_dir = os.path.join(work_dir, 'apk')
    CommandUtils.run_system_command(f'apktool d -f -o {decompiled_dir} {apk_path}')

    res_dir = os.path.join(decompiled_dir, 'res')
    mapping = {}
    if os.path.exists(res_dir):
        mapping = _rename_resources(res_dir)
        _replace_references(decompiled_dir, mapping)

    rebuilt_apk = os.path.join(work_dir, 'resguard.apk')
    CommandUtils.run_system_command(f'apktool b -o {rebuilt_apk} {decompiled_dir}')
    aligned_apk = os.path.join(work_dir, 'aligned.apk')
    CommandUtils.run_system_command(f'zipalign -p -f -v 4 {rebuilt_apk} {aligned_apk}')
    output_apk = os.path.join(os.path.dirname(apk_path), 'sign.apk')
    command = (
        f'apksigner sign --ks {keystore_info.keystore_path} '
        f'--ks-key-alias {keystore_info.key_alias} --ks-pass pass:{keystore_info.key_store_pass} '
        f'--key-pass pass:{keystore_info.key_pass} --out {output_apk} {aligned_apk}'
    )
    CommandUtils.run_system_command(command)

    opts = _parse_config(config_path)
    if opts.get("sevenzip"):
        _sevenzip_if_needed(output_apk, os.path.join(work_dir, '7zip.apk'))

    mapping_path = os.path.join(os.path.dirname(apk_path), 'resguard_mapping.txt')
    if mapping:
        _write_mapping(mapping, mapping_path)
    shutil.rmtree(work_dir)
    idsig = f'{output_apk}.idsig'
    if os.path.exists(idsig):
        os.remove(idsig)
    return output_apk
