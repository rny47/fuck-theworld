import logging
import os
import random
import shutil

from app.utils.common import CommandUtils, RandomNameUtils
from app.utils import resguard, packager
from app.utils.signing import KeyStoreInfo


class ApkUtils:

    @staticmethod
    def decompile_to_folder(apk_path: str, decompiled_path: str) -> None:
        """
        将 apk 文件反编译到 output 目录下
        :param apk_path: 被反编译的 apk 路径
        :param decompiled_path: 反编译的结果输出目录
        """
        command_decompile = f'apktool d -f -o {decompiled_path} {apk_path}'
        CommandUtils.run_system_command(command_decompile)

    @staticmethod
    def shrink_package(decompiled_path: str, need_shrink: bool) -> None:
        """
        压缩 apk 中的文件，目前的手段如下
            1. 尽可能删除多余的 cpu 架构文件
        :param decompiled_path: apk 反翻译后的目录
        :param need_shrink: 是否需要压缩开关
        """
        if not need_shrink:
            logging.debug('need shrink: false, skipped shrink apk')
            return
        if not os.path.exists(os.path.join(decompiled_path, 'lib')):
            logging.debug('lib c dir not exist, skipped shrink apk')
            return
        logging.debug('need shrink: true, start shrink apk...')
        # 收集所有的 cpu 架构
        lib_c_paths = [
            os.path.join(decompiled_path, 'lib', path)
            for path in os.listdir(os.path.join(decompiled_path, 'lib'))
        ]
        lib_c_armeabi_v7a = os.path.join(decompiled_path, 'lib', 'armeabi-v7a')
        lib_c_arm64_v8a = os.path.join(decompiled_path, 'lib', 'arm64-v8a')
        # 去除多余的 arm 架构，优先保留 lib/armeabi-v7a 而后 lib/arm64-v8a，其它情况结果无法预测则保留全部
        # lib_c_paths 中的目录下一步要删除，这里将需要保留的目录剔除出去，后续就不会被删除了
        if lib_c_armeabi_v7a in lib_c_paths:
            lib_c_paths.remove(lib_c_armeabi_v7a)
        elif lib_c_arm64_v8a in lib_c_paths:
            lib_c_paths.remove(lib_c_arm64_v8a)
        else:
            lib_c_paths = []  # 不删除任何目录
        # 删除记录下来的 cpu 架构
        for lib_c_path in lib_c_paths:
            shutil.rmtree(lib_c_path)
        logging.debug('shrink apk done!')

    @staticmethod
    def recompile(decompiled_path: str) -> str:
        """
        重新编译出新的 apk
        :param decompiled_path: 被编译的 apk 目录
        :return: apk 的输出路径，与输入路径同级目录
        """
        logging.debug('recompile...')
        # 编译输出到上层目录
        apk_output_path = os.path.join(os.path.dirname(decompiled_path), 'recompile.apk')
        command_recompile = f'apktool b -o {apk_output_path} {decompiled_path}'
        CommandUtils.run_system_command(command_recompile)
        logging.debug('recompile done')
        return apk_output_path




class SignUtils:

    @staticmethod
    def new_temp_key_store(keystore_path: str) -> KeyStoreInfo:
        """
        生成一个临时的 keystore 文件，用于签名
        :param keystore_path: 签名文件的生成路径
        :return: 生成签名文件的信息
        """
        # 准备基础信息
        key_alias = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', random.randint(3, 5)))
        key_store_pass = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 6))
        key_pass = key_store_pass       # key_pass 和 key_store_pass 必须相同，且必须是 6 位
        # 清除旧的 keystore 文件
        if os.path.exists(keystore_path):
            os.remove(keystore_path)
        # 组装命令
        command_create_keystore = (
            f'keytool -genkey -alias {key_alias} '
            f'-keyalg RSA -validity 3650 '
            f'-keystore {keystore_path} '
            f'-storepass {key_store_pass} '
            f'-keypass {key_pass} {RandomNameUtils.random_dname()}'
        )
        CommandUtils.run_system_command(command_create_keystore)
        return KeyStoreInfo(keystore_path, key_alias, key_store_pass, key_pass)

    @staticmethod
    def manual_sign(apk_path: str) -> str:
        """
        手动签名，原生方式写法
        :param apk_path: 被处理的 apk 路径
        :return 输出 apk 路径
        """
        # 4k 对齐，在 apk_path 同目录下生成，使用过后会删除
        logging.debug('manual signature apk...')
        zipalign_apk_path = os.path.join(os.path.dirname(apk_path), 'zipalign.apk')
        command_4k_zip = f'zipalign -p -f -v 4 {apk_path} {zipalign_apk_path}'
        CommandUtils.run_system_command(command_4k_zip)
        # 生成临时签名文件，在 apk_path 同目录下生成，使用过后会删除
        keystore_path = os.path.join(os.path.dirname(apk_path), 'android.keystore')
        keystore_info = SignUtils.new_temp_key_store(keystore_path)
        # 重新签名，在 apk_path 同目录下生成
        apk_output_path = os.path.join(os.path.dirname(apk_path), 'sign.apk')
        command_signature: str = (
            f'apksigner sign --ks {keystore_info.keystore_path} '
            f'--ks-key-alias {keystore_info.key_alias} --ks-pass pass:{keystore_info.key_store_pass} '
            f'--key-pass pass:{keystore_info.key_pass} --out {apk_output_path} {zipalign_apk_path}'
        )
        CommandUtils.run_system_command(command_signature)
        # 删除临时的 4k对其apk 与 签名文件，签名后会多生成一个 sign.apk.idsig 文件，也要删除
        os.remove(zipalign_apk_path)
        os.remove(keystore_path)
        os.remove(f'{apk_output_path}.idsig')
        # 签名完毕
        logging.debug('manual signature done')
        return apk_output_path

    @staticmethod
    def res_guard_sign(apk_path: str) -> str:
        """
        ResGuard 签名
        :param apk_path: 被处理的 apk 路径
        :return 输出 apk 路径
        """
        logging.debug('res guard signature apk...')
        keystore_path = os.path.join(os.path.dirname(apk_path), 'android.keystore')
        keystore_info = SignUtils.new_temp_key_store(keystore_path)
        config_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "lib", "config.xml"))
        apk_output_path = resguard.resguard_sign(apk_path, keystore_info, config_path)
        logging.debug('res guard signature done')
        return apk_output_path

    @staticmethod
    def jiagu_sign(apk_path: str) -> str:
        """
        先加固，再签名
        :param apk_path: 被处理的 apk 路径
        :return 输出 apk 路径
        """
        logging.debug('jiagu signature apk...')
        # 生成临时签名文件，并且移动到 apk_path 同目录下
        keystore_path = os.path.join(os.path.dirname(apk_path), 'android.keystore')
        keystore_info = SignUtils.new_temp_key_store(keystore_path)
        jiagu_tool_dir_path = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", "JiaguTool"))
        shell_dex_path = os.path.join(jiagu_tool_dir_path, 'bin', 'classes.dex')
        shell_lib_path = os.path.join(jiagu_tool_dir_path, 'bin', 'jni')
        apk_output_path = packager.pack_and_sign(apk_path, shell_dex_path, shell_lib_path, keystore_info, True)
        logging.debug('jiagu signature done')
        return apk_output_path
