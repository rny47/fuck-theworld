import logging
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 1))))

from app.utils.apk import ApkUtils, SignUtils
from app.utils.common import CommandUtils
from tests import BaseTestCase


class ApkUtilsTest(BaseTestCase):

    def setUp(self):
        CommandUtils.enable_stdout = True
        CommandUtils.enable_stderr = True

    def test_decompile_to_folder(self):
        apk_path = os.path.join(os.path.dirname(__file__), 'apks', 'qubo-com.l7b1a70e74.f9726cf5b6.apk')
        decompiled_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'output')
        ApkUtils.decompile_to_folder(apk_path, decompiled_path)
        self.assertTrue(True)

    def test_shrink_package(self):
        decompiled_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'output')
        ApkUtils.shrink_package(decompiled_path, True)
        self.assertTrue(True)

    def test_recompile(self):
        decompiled_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'output')
        apk_output_path = ApkUtils.recompile(decompiled_path)
        logging.debug(apk_output_path)
        self.assertTrue(True)


class SignUtilsTest(BaseTestCase):

    def setUp(self):
        CommandUtils.enable_stdout = True
        CommandUtils.enable_stderr = True

    def test_new_temp_key_store(self):
        keystore_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'android.keystore')
        keystore_info = SignUtils.new_temp_key_store(keystore_path)
        logging.debug(keystore_info)
        self.assertTrue(True)

    def test_manual_sign(self):
        apk_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'recompile.apk')
        apk_output_path = SignUtils.manual_sign(apk_path)
        logging.debug(apk_output_path)
        self.assertTrue(True)

    def test_res_guard_sign(self):
        apk_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'recompile.apk')
        apk_output_path = SignUtils.res_guard_sign(apk_path)
        logging.debug(apk_output_path)
        self.assertTrue(True)

    def test_jiagu_sign(self):
        apk_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'recompile.apk')
        # apk_output_path = SignUtils.jiagu_sign(apk_path)
        # logging.debug(apk_output_path)
        apk_path = '/Users/spark/Downloads/69-com.lbd273e0ff.f4cad9fcbf.apk'
        apk_name = os.path.splitext(os.path.basename(apk_path))[0]
        print(apk_name)
        self.assertTrue(True)
