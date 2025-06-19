import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 1))))

import logging
from tests import BaseTestCase
from app.utils.common import RandomNameUtils, PackageNameUtils, FileUtils, CommandUtils


class RandomNameUtilsTest(BaseTestCase):

    def test_random_package_name_part(self):
        logging.debug(RandomNameUtils.random_package_name_part())
        self.assertTrue(True)

    def test_random_class_name(self):
        logging.debug(RandomNameUtils.random_class_name())
        self.assertTrue(True)

    def test_random_xml_tag_name(self):
        logging.debug(RandomNameUtils.random_xml_tag_name())
        self.assertTrue(True)

    def test_random_en_string(self):
        logging.debug(RandomNameUtils.random_en_string())
        self.assertTrue(True)

    def test_random_dname(self):
        logging.debug(RandomNameUtils.random_dname())
        self.assertTrue(True)


class PackageNameUtilsTest(BaseTestCase):

    def test_generate_package_pair(self):
        manifest_path = os.path.join(os.path.dirname(__file__), 'assets', 'AndroidManifest.xml')
        original_package_name, new_package_name = PackageNameUtils.generate_package_pair(
            manifest_path, True, 'com.example.test.jump'
        )
        logging.debug(f"{original_package_name} -> {new_package_name}")
        self.assertTrue(True)

    def test_new_package_name_from_original(self):
        original_package_name = 'com.example.test'
        new_package_name = PackageNameUtils.new_package_name_from_original(original_package_name)
        logging.debug(f"{original_package_name} -> {new_package_name}")
        self.assertTrue(True)


class FileUtilsTest(BaseTestCase):

    def test_search_files_with_dir_name(self):
        file_paths = FileUtils.search_files_with_dir_name(
            os.path.dirname(__file__), lambda path: 'assets' in path
        )
        logging.debug(file_paths)
        self.assertTrue(True)

    def test_search_files_with_file_name(self):
        file_paths = FileUtils.search_files_with_file_name(
            os.path.dirname(__file__), lambda path: '.py' in path
        )
        logging.debug(file_paths)
        self.assertTrue(True)

    def test_replace_files_content(self):
        file_paths = FileUtils.search_files_with_dir_name(
            os.path.dirname(__file__), lambda path: 'assets' in path
        )
        FileUtils.replace_files_content(
            file_paths, lambda content: content.replace('abc_config_activityDefaultDur', 'test2'),
            just_print=True
        )
        self.assertTrue(True)

    def test_replace_file_content(self):
        file_path = os.path.join(os.path.dirname(__file__), 'assets', 'values', 'integers.xml')
        FileUtils.replace_file_content(
            file_path, lambda content: content.replace('abc_config_activityDefaultDur', 'test2'),
            just_print=True
        )
        self.assertTrue(True)


class CommandUtilsTest(BaseTestCase):

    def test_run_system_command(self):
        CommandUtils.enable_stdout = True
        CommandUtils.enable_stderr = True
        CommandUtils.run_system_command("pwd")
        self.assertTrue(True)
