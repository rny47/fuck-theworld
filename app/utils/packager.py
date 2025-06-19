import os
import shutil
import tempfile
from xml.dom import minidom

from app.utils.common import CommandUtils
from app.utils.signing import KeyStoreInfo


def _sevenzip_if_needed(apk_path: str) -> None:
    if shutil.which("7z"):
        tmp = apk_path + ".7z"
        CommandUtils.run_system_command(f"7z a -tzip -mx9 {tmp} {apk_path}")
        os.replace(tmp, apk_path)


def pack_and_sign(apk_path: str, shell_dex: str, shell_lib_dir: str, keystore_info: KeyStoreInfo, use_sevenzip: bool = True) -> str:
    """Inject shell dex/libs, tweak manifest and sign the APK."""
    work_dir = tempfile.mkdtemp()
    decompiled_dir = os.path.join(work_dir, 'apk')
    CommandUtils.run_system_command(f'apktool d -f -o {decompiled_dir} {apk_path}')

    shutil.copy(shell_dex, os.path.join(decompiled_dir, 'classes.dex'))
    for root, _, files in os.walk(shell_lib_dir):
        for f in files:
            rel = os.path.relpath(os.path.join(root, f), shell_lib_dir)
            dest = os.path.join(decompiled_dir, 'lib', rel)
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copy(os.path.join(root, f), dest)

    manifest_path = os.path.join(decompiled_dir, 'AndroidManifest.xml')
    if os.path.exists(manifest_path):
        doc = minidom.parse(manifest_path)
        application = doc.getElementsByTagName('application')[0]
        meta = doc.createElement('meta-data')
        meta.setAttribute('android:name', 'packed')
        meta.setAttribute('android:value', 'true')
        application.appendChild(meta)
        with open(manifest_path, 'w', encoding='utf-8') as f:
            doc.writexml(f, encoding='utf-8')

    rebuilt_apk = os.path.join(work_dir, 'packed.apk')
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

    if use_sevenzip:
        _sevenzip_if_needed(output_apk)

    shutil.rmtree(work_dir)
    idsig = f'{output_apk}.idsig'
    if os.path.exists(idsig):
        os.remove(idsig)
    return output_apk
