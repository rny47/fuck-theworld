import os
import shutil
import tempfile

from app.utils.apk import ApkUtils, SignUtils
from app.utils.common import PackageNameUtils
from app.utils.resource import ManifestUtils, SmaliUtils, XmlUtils, PictureUtil


def apk_clean_one_step(
        original_apk_path: str, target_apk_path: str, need_shrink: bool,
        need_change_package_name: bool, new_package_name) -> None:
    """
    一步完成 apk 清理
    :param original_apk_path: 原包 apk 路径
    :param target_apk_path: 目标生成路径
    :param need_shrink: 是否需要压缩
    :param need_change_package_name: 是否替换应用包名
    :param new_package_name: 替换后的包名
    """
    # 工作目录不存在则会创建一个工作目录
    work_dir_path = tempfile.mkdtemp()                                          # 在临时目录中做处理
    if not os.path.exists(work_dir_path):
        os.makedirs(work_dir_path)

    # 反编译 apk
    apk_output_path = os.path.join(work_dir_path, 'output')
    ApkUtils.decompile_to_folder(original_apk_path, apk_output_path)

    # 做一些处理
    manifest_path = os.path.join(apk_output_path, 'AndroidManifest.xml')
    original_package_name, new_package_name = PackageNameUtils.generate_package_pair(
        manifest_path, need_change_package_name, new_package_name
    )
    ManifestUtils.random_manifest_metadata(manifest_path)
    ManifestUtils.replace_package_name(manifest_path, original_package_name, new_package_name)
    SmaliUtils.replace_package_name(apk_output_path, original_package_name, new_package_name)
    # SmaliUtils.random_activity_name(apk_output_path)  # 先不要启用这一步，有些应用有兼容性问题
    SmaliUtils.append_folder_smali_field(apk_output_path)
    XmlUtils.random_xml_resource(apk_output_path)
    PictureUtil.add_random_point_png_in_folder(os.path.join(apk_output_path)) # 不要限定在 res 目录，有的项目在其它位置也有图片

    # 压缩与重新编译
    ApkUtils.shrink_package(apk_output_path, need_shrink)
    recompile_apk_path = ApkUtils.recompile(apk_output_path)
    sign_apk_path = SignUtils.jiagu_sign(recompile_apk_path)

    # 善后工作：复制生成的 apk 到目标路径并删除工作目录，如果存在则先删除
    if os.path.exists(target_apk_path):
        os.remove(target_apk_path)
    shutil.copy(sign_apk_path, target_apk_path)     # 同名文件新的会覆盖旧的
    shutil.rmtree(work_dir_path)
