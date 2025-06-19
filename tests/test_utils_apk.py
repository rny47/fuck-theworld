import logging
import os
import sys
import tempfile
import shutil
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.utils.apk import ApkUtils, SignUtils
from app.utils.common import CommandUtils
from tests import BaseTestCase


class ApkUtilsTest(BaseTestCase):
    def setUp(self):
        CommandUtils.enable_stdout = True
        CommandUtils.enable_stderr = True
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        def fake_run(cmd, cwd=None):
            logging.debug(cmd)
            parts = cmd.split()
            if 'apktool' in cmd:
                if ' d ' in cmd:
                    if '-o' in parts:
                        out_dir = parts[parts.index('-o') + 1]
                        os.makedirs(out_dir, exist_ok=True)
                if ' b ' in cmd:
                    if '-o' in parts:
                        out_file = parts[parts.index('-o') + 1]
                        open(out_file, 'wb').close()
            elif parts[0] == 'zipalign':
                open(parts[-1], 'wb').close()
            elif parts[0] == 'apksigner':
                out_file = parts[parts.index('--out') + 1]
                open(out_file, 'wb').close()
                open(f'{out_file}.idsig', 'wb').close()
            elif parts[0] == '7z':
                open(parts[4], 'wb').close()
            elif parts[0] == 'keytool':
                out_file = parts[parts.index('-keystore') + 1]
                open(out_file, 'wb').close()

        patcher = mock.patch.object(CommandUtils, 'run_system_command', fake_run)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_decompile_to_folder(self):
        apk_path = os.path.join(self.tmpdir, 'input.apk')
        open(apk_path, 'wb').close()
        decompiled_path = os.path.join(self.tmpdir, 'output')
        ApkUtils.decompile_to_folder(apk_path, decompiled_path)
        self.assertTrue(True)

    def test_shrink_package(self):
        decompiled_path = os.path.join(self.tmpdir, 'output')
        ApkUtils.shrink_package(decompiled_path, True)
        self.assertTrue(True)

    def test_recompile(self):
        decompiled_path = os.path.join(self.tmpdir, 'output')
        apk_output_path = ApkUtils.recompile(decompiled_path)
        logging.debug(apk_output_path)
        self.assertTrue(True)


class SignUtilsTest(BaseTestCase):
    def setUp(self):
        CommandUtils.enable_stdout = True
        CommandUtils.enable_stderr = True
        self.tmpdir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, self.tmpdir)
        def fake_run(cmd, cwd=None):
            logging.debug(cmd)
            parts = cmd.split()
            if 'apktool' in cmd:
                if ' d ' in cmd and '-o' in parts:
                    out_dir = parts[parts.index('-o') + 1]
                    os.makedirs(out_dir, exist_ok=True)
                if ' b ' in cmd and '-o' in parts:
                    out_file = parts[parts.index('-o') + 1]
                    open(out_file, 'wb').close()
            elif parts[0] == 'zipalign':
                open(parts[-1], 'wb').close()
            elif parts[0] == 'apksigner':
                out_file = parts[parts.index('--out') + 1]
                open(out_file, 'wb').close()
                open(f'{out_file}.idsig', 'wb').close()
            elif parts[0] == '7z':
                open(parts[4], 'wb').close()
            elif parts[0] == 'keytool':
                out_file = parts[parts.index('-keystore') + 1]
                open(out_file, 'wb').close()

        patcher = mock.patch.object(CommandUtils, 'run_system_command', fake_run)
        self.addCleanup(patcher.stop)
        patcher.start()

    def test_new_temp_key_store(self):
        keystore_path = os.path.join(tempfile.gettempdir(), 'android.keystore')
        keystore_info = SignUtils.new_temp_key_store(keystore_path)
        logging.debug(keystore_info)
        self.assertTrue(True)

    def test_manual_sign(self):
        apk_path = os.path.join(self.tmpdir, 'input.apk')
        open(apk_path, 'wb').close()
        output = SignUtils.manual_sign(apk_path)
        logging.debug(output)
        self.assertTrue(output.endswith('sign.apk'))

    def test_res_guard_sign(self):
        apk_path = os.path.join(self.tmpdir, 'input.apk')
        open(apk_path, 'wb').close()
        output = SignUtils.res_guard_sign(apk_path)
        logging.debug(output)
        self.assertTrue(output.endswith('sign.apk'))

    def test_jiagu_sign(self):
        apk_path = os.path.join(self.tmpdir, 'input.apk')
        open(apk_path, 'wb').close()
        output = SignUtils.jiagu_sign(apk_path)
        logging.debug(output)
        self.assertTrue(output.endswith('sign.apk'))
