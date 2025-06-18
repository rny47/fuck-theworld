import logging
import os
import random
import subprocess
from typing import Callable, List
from xml.dom.minidom import parse

common_words = []       # 常用英语词汇
with open(os.path.realpath(os.path.join(os.path.dirname(__file__), '..', 'lib', 'common_words.txt')), 'r') as f:
    common_words += [line for line in f.read().splitlines() if len(line.strip()) >= 2]


class RandomNameUtils:

    @staticmethod
    def random_package_name_part() -> str:
        """ 随机生成包名的一段，多段拼装才是个完整的包名 """
        part1 = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz', 2))
        part2 = ''.join(random.sample('abcdefghijklmnopqrstuvwxyz0123456789', random.randint(3, 18)))
        return part1 + part2

    @staticmethod
    def random_class_name() -> str:
        return ''.join(random.sample('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', 16))

    @staticmethod
    def random_xml_tag_name() -> str:
        return '_'.join([random.choice(common_words) for i in range(random.randint(5, 10))])

    @staticmethod
    def random_en_string() -> str:
        """ 随机生成英文字符串句子 """
        return ' '.join([random.choice(common_words) for i in range(random.randint(5, 10))])

    @staticmethod
    def random_dname() -> str:
        """ 随机生成 dname 字符串，生成签名文件时使用 """
        random_source = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
        return (
            f'-dname "CN={"".join(random.sample(random_source, 10)) + ".com"}, '
            f'OU={"".join(random.sample(random_source, 10))}, '
            f'O={"".join(random.sample(random_source, 10))}, '
            f'ST={"".join(random.sample(random_source, 10))}, '
            f'L=BJ, C=CN"'
        )


class PackageNameUtils:

    @staticmethod
    def generate_package_pair(
            manifest_path: str, need_change_package_name: bool, new_package_name) -> tuple[str, str]:
        """
        从清单文件中解析出 原始包名 和 新包名对，新包名可以指定是否需要更换
            1. 不改变包名则使用原始包名
            2. 改变包名则使用指定的新包名，不指定新包名则会自动生成一个新的包名
        注意：新包名需要与原始包名段数保持一致，目前不支持不同段数的配置
        :param manifest_path: 清单文件路径
        :param need_change_package_name: 是否需要替换包名
        :param new_package_name: 指定的新包名，可以为 None
        :return: 原始包名 和 新包名
        """
        original_package_name = parse(manifest_path).documentElement.getAttribute("package")
        if not need_change_package_name:
            return original_package_name, original_package_name
        else:
            new_package_name = new_package_name \
                if new_package_name \
                else PackageNameUtils.new_package_name_from_original(original_package_name)
            if len(original_package_name.split('.')) != len(new_package_name.split('.')):
                raise Exception(
                    f'原始包名和新包名段数不一致，原始包名: {original_package_name} 新包名: {new_package_name}')
            return original_package_name, new_package_name

    @staticmethod
    def new_package_name_from_original(original_package_name: str) -> str:
        """
        根据原包名生成一个新的包名
        :param original_package_name: 原始包名
        :return: 新的包名，段数和上方 original_package_name 一致
        """
        count = len(original_package_name.split('.'))
        new_package_name = '.'.join([RandomNameUtils.random_package_name_part() for i in range(0, count)])
        return new_package_name


class FileUtils:

    @staticmethod
    def search_files_with_dir_name(root_path: str, func_in: Callable[[str], bool]) -> List[str]:
        """
        从 root_path 中将符合 func_in 查询条件的路径收集起来并返回
          1. 匹配回调传入的是目录路径，若匹配则会将该目录下的所有文件路径收集起来
        :param root_path: 查询根目录路径
        :param func_in: 查询条件，要返回布尔值
        :return: 收集到的路径数组
        """
        file_paths = []
        for root, dirs, files in os.walk(root_path):
            if func_in(root):
                for file in files:
                    file_path = os.path.join(root, file)
                    file_paths.append(file_path)
        return file_paths

    @staticmethod
    def search_files_with_file_name(root_path: str, func_in: Callable[[str], bool]) -> List[str]:
        """
        从 root_path 中将符合 func_in 查询条件的路径收集起来并返回
          1. 匹配回调传入的是文件路径，若匹配则会将该文件路径收集起来
        :param root_path: 查询根目录路径
        :param func_in: 查询条件，要返回布尔值
        :return: 收集到的路径数组
        """
        file_paths = []
        for root, dirs, files in os.walk(root_path):
            for file in files:
                file_path = os.path.join(root, file)
                if func_in(file_path):
                    file_paths.append(file_path)
        return file_paths

    @staticmethod
    def replace_files_content(file_paths: List[str], func_replace: Callable[[str], str], just_print: bool = False) -> None:
        """
        批量替换版本
        :param file_paths: 文件路径数组
        :param func_replace: 执行内容替换函数
        :param just_print: 是否只打印内容，如果是则不会写回文件
        """
        for file_path in file_paths:
            FileUtils.replace_file_content(file_path, func_replace, just_print)

    @staticmethod
    def replace_file_content(file_path: str, func_replace: Callable[[str], str], just_print: bool = False) -> None:
        """
        替换文件的内容，如果内容会发生变化则会执行重新写入操作
        :param file_path: 被操作的文件路径
        :param func_replace: 执行内容替换函数
        :param just_print: 是否只打印内容，如果是则不会写回文件
        """
        with open(file_path, 'r') as f:
            file_content = f.read()
        new_content = func_replace(file_content)
        if just_print:
            logging.debug(new_content)
            return
        if new_content == file_content:
            return
        with open(file_path, 'w') as f:
            f.write(new_content)
            logging.debug(f'replacing content {file_path}')


class CommandUtils:
    enable_stdout: bool = False     # 默认不打印输出信息
    enable_stderr: bool = True      # 默认只打印错误信息

    @staticmethod
    def run_system_command(command: str, cwd: str = None) -> None:
        """
        执行系统命令，并打印输出。 默认只打印错误信息
        :param command: 执行的命令
        :param cwd: 工作目录，默认为当前工作目录
        """
        logging.debug(f'run system command: {command}')
        try:
            result = subprocess.run(command, shell=True,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                    text=True, cwd=cwd)
            if CommandUtils.enable_stdout and result.stdout:
                logging.info(result.stdout)
            if CommandUtils.enable_stderr and result.stderr:
                logging.error(result.stderr)
        except subprocess.CalledProcessError as e:
            logging.error(e)
