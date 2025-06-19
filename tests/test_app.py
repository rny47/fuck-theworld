import os
import sys
import unittest
from unittest import mock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tests import BaseTestCase
from app.utils.common import CommandUtils
from app import apk_clean_one_step
import tempfile
import shutil
import logging


class AppTest(BaseTestCase):
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
                    with open(os.path.join(out_dir, 'AndroidManifest.xml'), 'w') as f:
                        f.write('<manifest package="com.old.app"/>')
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

    def test_app_clean_one_step_69(self):
        src = os.path.join(self.tmpdir, 'in.apk')
        tgt = os.path.join(self.tmpdir, 'out.apk')
        open(src, 'wb').close()

        def fake_recompile(path):
            out = os.path.join(os.path.dirname(path), 'recompile.apk')
            open(out, 'wb').close()
            return out

        def fake_jiagu(path):
            out = os.path.join(os.path.dirname(path), 'sign.apk')
            open(out, 'wb').close()
            return out

        with mock.patch('app.utils.apk.ApkUtils.recompile', side_effect=fake_recompile), \
             mock.patch('app.utils.apk.SignUtils.jiagu_sign', side_effect=fake_jiagu), \
             mock.patch('app.utils.resource.ManifestUtils.random_manifest_metadata'), \
             mock.patch('app.utils.resource.ManifestUtils.replace_package_name'), \
             mock.patch('app.utils.resource.SmaliUtils.replace_package_name'), \
             mock.patch('app.utils.resource.SmaliUtils.append_folder_smali_field'), \
             mock.patch('app.utils.resource.XmlUtils.random_xml_resource'), \
             mock.patch('app.utils.resource.PictureUtil.add_random_point_png_in_folder'):
            apk_clean_one_step(src, tgt, True, True, 'com.new.app')
            self.assertTrue(os.path.exists(tgt))

    def test_app_clean_one_step_qubo(self):
        src = os.path.join(self.tmpdir, 'in.apk')
        tgt = os.path.join(self.tmpdir, 'out2.apk')
        open(src, 'wb').close()

        with mock.patch('app.utils.apk.ApkUtils.recompile', return_value=os.path.join(self.tmpdir, 'recompile.apk')) as rpatch, \
             mock.patch('app.utils.apk.SignUtils.jiagu_sign', return_value=os.path.join(self.tmpdir, 'sign.apk')) as jpatch, \
             mock.patch('app.utils.resource.ManifestUtils.random_manifest_metadata'), \
             mock.patch('app.utils.resource.ManifestUtils.replace_package_name'), \
             mock.patch('app.utils.resource.SmaliUtils.replace_package_name'), \
             mock.patch('app.utils.resource.SmaliUtils.append_folder_smali_field'), \
             mock.patch('app.utils.resource.XmlUtils.random_xml_resource'), \
             mock.patch('app.utils.resource.PictureUtil.add_random_point_png_in_folder'):
            open(rpatch.return_value, 'wb').close()
            open(jpatch.return_value, 'wb').close()
            apk_clean_one_step(src, tgt, False, False, None)
            self.assertTrue(os.path.exists(tgt))
