import logging
import os, sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), *(['..'] * 1))))
import click
from app import apk_clean_one_step


@click.command()
@click.option('--original-apk-path', required=True, type=click.Path(exists=True), help='原始包路径，可以是相对路径或绝对路径')
@click.option('--target-apk-path', required=True, type=click.Path(exists=False), help='生成目标包路径，可以是相对路径或绝对路径')
@click.option('--need-shrink', default=True, show_default=True, type=bool, help='是否需要压缩 apk，开启可能会有兼容性问题')
@click.option('--need-change-package-name', default=True, show_default=True, type=bool, help='是否需要修改包名，不开启则使用原包名')
@click.option(
    '--new-package-name', default=None, show_default=True, type=str,
    help='当开启包名修改时：若需要修改包名，可以指定一个固定的包名，不指定则会使用随机包名'
)
def clean_apk(
        original_apk_path: str, target_apk_path: str, need_shrink: bool,
        need_change_package_name: bool, new_package_name: str
):
    """
    一步完成 apk 清理，可在任意位置执行该命令。注意：若要指定包名，则段数必须与原包名段数相同，否则运行时会报错
    """
    # 运行环境校验
    original_apk_path = os.path.realpath(original_apk_path)
    target_apk_path = os.path.realpath(target_apk_path)
    if not os.path.exists(original_apk_path):
        logging.error(f'original apk path not exists! -> {original_apk_path}')
        exit(1)
    target_apk_dir = os.path.dirname(target_apk_path)
    if not os.path.exists(target_apk_dir):
        os.makedirs(target_apk_dir)
    # 开始清理
    apk_clean_one_step(
        original_apk_path, target_apk_path, need_shrink,
        need_change_package_name, new_package_name
    )


if __name__ == "__main__":
    clean_apk()
