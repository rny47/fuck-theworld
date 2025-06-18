import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 1))))

from tests import BaseTestCase
from app.utils.common import CommandUtils
from app import apk_clean_one_step

class AppTest(BaseTestCase):

    def setUp(self):
        CommandUtils.enable_stdout = True
        CommandUtils.enable_stderr = True

    def test_app_clean_one_step_69(self):
        original_apk_path = os.path.join(os.path.dirname(__file__), 'apks', '69-com.lbd273e0ff.f4cad9fcbf.apk')
        target_apk_path = os.path.join(os.path.expanduser("~"), 'Downloads', '69-com.lbd273e0ff.f4cad9fcbf.apk')
        need_shrink = True
        need_change_package_name = True
        new_package_name = 'com.live888.live69'
        apk_clean_one_step(
            original_apk_path, target_apk_path, need_shrink,
            need_change_package_name, new_package_name
        )
        self.assertTrue(True)

    def test_app_clean_one_step_qubo(self):
        original_apk_path = os.path.join(os.path.dirname(__file__), 'apks', 'qubo-com.l54d295915.fe89f6fa6f.apk')
        target_apk_path = os.path.join(os.path.expanduser("~"), 'Downloads', 'qubo-com.l54d295915.fe89f6fa6f.apk')
        need_shrink = True
        need_change_package_name = True
        new_package_name = 'com.live888.livequbo'
        apk_clean_one_step(
            original_apk_path, target_apk_path, need_shrink,
            need_change_package_name, new_package_name
        )
        self.assertTrue(True)
