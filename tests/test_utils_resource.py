import os, sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 1))))

from app.utils.resource import ManifestUtils, SmaliUtils, XmlUtils, PictureUtil
from tests import BaseTestCase


class ManifestUtilsTest(BaseTestCase):

    def test_random_manifest_metadata(self):
        manifest_path = os.path.join(os.path.dirname(__file__), 'assets', 'AndroidManifest.xml')
        ManifestUtils.random_manifest_metadata(manifest_path, just_print=True)
        self.assertTrue(True)

    def test_replace_package_name(self):
        manifest_path = os.path.join(os.path.dirname(__file__), 'assets', 'AndroidManifest.xml')
        ManifestUtils.replace_package_name(
            manifest_path,
            'com.vip361b7.d1020.com', 'com.example.test.jump',
            just_print=True
        )
        self.assertTrue(True)


class SmaliUtilsTest(BaseTestCase):

    def test_replace_package_name(self):
        decompile_output_path = os.path.join(os.path.dirname(__file__), 'assets')
        SmaliUtils.replace_package_name(
            decompile_output_path,
            'com.vip361b7.d1020.com', 'com.example.test.jump',
            just_print=True
        )
        self.assertTrue(True)

    def test_random_activity_name(self):
        decompile_output_path = os.path.join(os.path.dirname(__file__), 'assets')
        SmaliUtils.random_activity_name(decompile_output_path, just_print=True)
        self.assertTrue(True)

    def test_random_smali(self):
        # 后续优化 smali 处理过程的时候再编写这里的测试
        self.assertTrue(True)

    def test_append_folder_smali_field(self):
        decompile_output_path = os.path.join(os.path.dirname(__file__), 'assets')
        SmaliUtils.append_folder_smali_field(decompile_output_path)
        self.assertTrue(True)

    def test_append_smali_field(self):
        smali_path = os.path.join(os.path.dirname(__file__), 'smali', 'test1.smali')
        SmaliUtils.append_smali_field(smali_path)
        self.assertTrue(True)


class XmlUtilsTest(BaseTestCase):

    def test_random_xml_resource(self):
        decompile_output_path = os.path.join(os.path.dirname(__file__), 'assets')
        XmlUtils.random_xml_resource(decompile_output_path, just_print=True)
        self.assertTrue(True)

    def test_append_nodes_for_arrays(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'assets', 'values', 'arrays.xml')
        XmlUtils.append_nodes_for_arrays(xml_path, just_print=True)
        self.assertTrue(True)

    def test_append_nodes_to_strings(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'assets', 'values', 'strings.xml')
        XmlUtils.append_nodes_to_strings(xml_path, just_print=True)
        self.assertTrue(True)

    def test_append_nodes_to_attrs(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'assets', 'values', 'attrs.xml')
        XmlUtils.append_nodes_to_attrs(xml_path, just_print=True)
        self.assertTrue(True)

    def test_append_nodes_to_bools(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'assets', 'values', 'bools.xml')
        XmlUtils.append_nodes_to_bools(xml_path, just_print=True)
        self.assertTrue(True)

    def test_shuffle_xml_nodes(self):
        xml_path = os.path.join(os.path.dirname(__file__), 'assets', 'values', 'integers.xml')
        XmlUtils.shuffle_xml_nodes(xml_path, just_print=True)
        self.assertTrue(True)


class PictureUtilsTest(BaseTestCase):

    def test_add_random_point_png_in_folder(self):
        folder_path = os.path.join(os.path.dirname(__file__), 'res')
        PictureUtil.add_random_point_png_in_folder(folder_path)
        self.assertTrue(True)

    def test_add_transparent_point(self):
        input_path = os.path.join(os.path.dirname(__file__), 'res', 'drawable-night-mdpi', 'yd_ic_close.png')
        output_path = os.path.join(os.path.dirname(__file__), 'res', 'drawable-night-mdpi', 'yd_ic_close.png')
        PictureUtil.add_random_point(input_path, output_path)
        self.assertTrue(True)
