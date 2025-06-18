import logging
import os
import random
import string
import glob
from xml.dom.minidom import Element, parse
from PIL import Image, ImageDraw

from app.utils.common import RandomNameUtils, FileUtils


class ManifestUtils:

    @staticmethod
    def random_manifest_metadata(manifest_path: str, just_print: bool = False) -> None:
        """
        随机修改 manifest 中的 部分元数据
        :param manifest_path: 清单文件上路径
        :param just_print: 是否只打印内容，如果是则不会写回文件
        """
        logging.debug('manifest meta randing...')
        doc: Element = parse(manifest_path).documentElement

        ### 替换清单文件顶部的一些属性
        # 生成关键属性
        random_code = str(random.randint(14, 25))
        package_name = doc.getAttribute("package")
        # 替换元数据
        doc.setAttribute('android:compileSdkVersion', random_code)
        doc.setAttribute(
            'android:compileSdkVersionCodename',
            f"{doc.getAttribute('android:compileSdkVersion')}-{RandomNameUtils.random_package_name_part()}"
        )
        doc.setAttribute('android:sharedUserId', package_name)
        doc.setAttribute('platformBuildVersionCode', random_code)
        doc.setAttribute(
            'platformBuildVersionName',
            f"{doc.getAttribute('platformBuildVersionCode')}-{RandomNameUtils.random_package_name_part()}"
        )
        ### 为所有元素添加一个随机启动顺序
        # 定义一个递归函数来遍历并修改节点，为每个节点添加一个随机启动顺序
        # order 必须是字符串
        def add_init_order_attribute(node, order: str):
            if node.nodeType == node.ELEMENT_NODE:
                node.setAttribute('android:initOrder', order)
            for child in node.childNodes:
                add_init_order_attribute(child, order)
        # 生成一个随机启动顺序，所有节点都修改为一样的启动顺序，避免出现莫名问题
        random_order = str(random.randint(20, 999))
        add_init_order_attribute(doc, random_order)

        ### 最后的工作：文件写入保存
        if just_print:
            # logging.debug(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            print(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            return
        # 保存回文件
        with open(manifest_path, 'w') as f:
            f.write(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
        logging.debug('manifest meta randed')

    @staticmethod
    def replace_package_name(
            manifest_path: str, original_package_name: str, new_package_name: str, just_print: bool = False
    ) -> None:
        """
        修改和包名替换有关的部分
        :param manifest_path: 清单文件上路径
        :param original_package_name: 清单文件中的原始包名
        :param new_package_name: 要应用的新的包名
        :param just_print: 是否只打印内容，如果是则不会写回文件
        """
        # 替换清单文件，只是替换 applicationId 相关
        if original_package_name == new_package_name:
            logging.debug('no need change package name, new package name is same as original')
            return
        logging.debug(f'replace package name..., from {original_package_name} to {new_package_name}')
        FileUtils.replace_file_content(
            manifest_path,
            lambda content: content.replace(original_package_name, new_package_name),
            just_print
        )
        logging.debug('replace package name done')


class SmaliUtils:

    @staticmethod
    def replace_package_name(
            decompile_output_path: str, original_package_name: str, new_package_name: str, just_print: bool = False
    ) -> None:
        """
        重命名 smali 相关代码的包名与路径
        :param decompile_output_path: 反编译的结果输出目录
        :param original_package_name: 原始包名
        :param new_package_name: 要应用的新的包名
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        # 替换 smali 文件内容的包名
        logging.debug('rename package name in smali...')
        smali_file_paths = FileUtils.search_files_with_dir_name(
            decompile_output_path, lambda path: 'smali' in path
        )
        original_smali_path = original_package_name.replace('.', '/')
        new_smali_path = new_package_name.replace('.', '/')
        FileUtils.replace_files_content(
            smali_file_paths,
            lambda content: content
            .replace(original_package_name, new_package_name)
            .replace(original_smali_path, new_smali_path),
            just_print
        )
        # 对代码目录名重命名
        logging.debug('rename package name for dir...')
        for root, dirs, files in os.walk(decompile_output_path):
            if 'smali' in root and os.path.exists(os.path.join(root, original_smali_path)):
                if just_print:
                    logging.debug(f'rename {original_smali_path} to {new_smali_path}')
                else:
                    os.renames(
                        os.path.join(root, original_smali_path), os.path.join(root, new_smali_path)
                    )
        logging.debug('rename package name done')

    @staticmethod
    def random_activity_name(decompile_output_path: str, just_print: bool = False) -> None:
        """
        随机命名关键 Activity。这一步先不要启用了，有些应用有兼容性问题
        :param decompile_output_path: 反编译的结果输出目录
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        manifest_path = os.path.join(decompile_output_path, 'AndroidManifest.xml')
        # 查找关键 Activity 信息
        activity_nodes = parse(manifest_path).getElementsByTagName("activity")
        main_activity_note = list(filter(lambda node: "android.intent.action.MAIN" in node.toxml(), activity_nodes))[0]
        main_activity_name = main_activity_note.getAttribute("android:name")
        new_activity_name = ".".join(main_activity_name.split('.')[0:-1]) + "." + RandomNameUtils.random_class_name()
        # 替换清单文件
        logging.debug('rename activity name in AndroidManifest...')
        FileUtils.replace_file_content(
            manifest_path,
            lambda content: content.replace(main_activity_name, new_activity_name),
            just_print
        )
        # 替换 Smali 文件
        logging.debug('rename activity name in smali...')
        smali_file_paths = FileUtils.search_files_with_dir_name(
            decompile_output_path, lambda path: 'smali' in path
        )
        for smali_file_path in smali_file_paths:
            SmaliUtils.random_smali(smali_file_path, main_activity_name, new_activity_name, just_print)

    @staticmethod
    def random_smali(
            smali_file_path: str, activity_name: str, new_activity_name: str, just_print: bool = False
    ) -> None:
        # 声明一些常用参数
        activity_smali_path = activity_name.replace(".", os.path.sep)
        activity_simple_name = activity_name.split(".")[-1]
        new_activity_name_smali_path = new_activity_name.replace(".", os.path.sep)
        new_activity_simple_name = new_activity_name.split(".")[-1]

        # 替换 Smali 内容
        def func_replace_smali(content: str):
            new_content = content.replace(
                activity_name.replace(".", "/"), new_activity_name.replace(".", "/")
            )
            new_content = new_content.replace(
                f'.source "{activity_simple_name}.java"', f'.source "{new_activity_simple_name}.java"'
            )
            return new_content

        FileUtils.replace_file_content(
            smali_file_path, func_replace_smali, just_print
        )
        # 重名名 Smali 文件：如果这个 Smali 文件是 activity_name 的类文件，则重命名
        if activity_smali_path in smali_file_path:
            new_smali_file_path = smali_file_path.replace(
                activity_smali_path, new_activity_name_smali_path
            )
            if just_print:
                logging.debug(f'rename {smali_file_path} to {new_smali_file_path}')
            else:
                os.rename(smali_file_path, new_smali_file_path)

    @staticmethod
    def append_folder_smali_field(decompile_output_path):
        """
        遍历 decompile_output_path，向所有 smali 文件追加字段
        :param decompile_output_path: 反编译的目录
        :type decompile_output_path: str
        """

        # 如果分包已经到 4 了，说明代码已经非常多了，此时混入过多编译时会包 65535 错误，导致反编译失败
        if os.path.exists(os.path.join(decompile_output_path, 'smali_classes4')):
            return

        # 查找清单文件中的 application、activity、service、provider、receiver
        manifest_path = os.path.join(decompile_output_path, 'AndroidManifest.xml')
        doc = parse(manifest_path).documentElement
        application_name = doc.getElementsByTagName('application')[0].getAttribute('android:name')
        print(application_name)
        activity_names = [activity.getAttribute('android:name') for activity in doc.getElementsByTagName('activity')]
        print(activity_names)
        service_names = [service.getAttribute('android:name') for service in doc.getElementsByTagName('service')]
        print(service_names)
        provider_names = [service.getAttribute('android:name') for service in doc.getElementsByTagName('provider')]
        print(provider_names)
        receiver_names = [service.getAttribute('android:name') for service in doc.getElementsByTagName('receiver')]
        print(receiver_names)
        # 将这些关键组件转换为路径
        application_path = application_name.replace('.', os.path.sep) + '.smali'
        print(application_path)
        activity_paths = [activity_name.replace('.', os.path.sep) + '.smali' for activity_name in activity_names]
        print(activity_paths)
        service_paths = [service_name.replace('.', os.path.sep) + '.smali' for service_name in service_names]
        print(service_paths)
        provider_paths = [provider_name.replace('.', os.path.sep) + '.smali' for provider_name in provider_names]
        print(provider_paths)
        receiver_paths = [receiver_name.replace('.', os.path.sep) + '.smali' for receiver_name in receiver_names]
        print(receiver_paths)
        # 查找所有的 smali 目录
        smali_dir_pattern = os.path.join(decompile_output_path, 'smali*')
        smali_dirs = glob.glob(smali_dir_pattern, recursive=False)
        print(smali_dirs)
        # 将所有的 smali 文件保存到一起，统一处理
        smali_paths = [application_path] + activity_paths + service_paths + provider_paths + receiver_paths
        print(smali_paths)
        # 分别与 smali_dirs 路径串联，排除掉不存在的路径
        smali_file_paths = [
            os.path.join(smali_dir, smali_path)
            for smali_dir in smali_dirs
            for smali_path in smali_paths
            if os.path.isfile(os.path.join(smali_dir, smali_path))
        ]
        print(smali_file_paths)

        # 清单文件中的类还比较少，先添加一波方法，否则后面再添加就会导致编译失败
        for smali_path in smali_file_paths:
            SmaliUtils.append_smali_method(smali_path)

        # 除了上面的 smali 之外，还要在追加一些，避免处理的太少没有效果
        all_smali_file_paths = FileUtils.search_files_with_dir_name(
            decompile_output_path, lambda path: 'smali' in path
        )
        min_count = 5000
        some_random_smali_file_paths = random.sample(all_smali_file_paths, min(min_count, len(all_smali_file_paths)))
        smali_file_paths += some_random_smali_file_paths
        print(smali_file_paths)

        # 像这些 smali 文件追加字段
        for smali_path in smali_file_paths:
            SmaliUtils.append_smali_field(smali_path)


    @staticmethod
    def append_smali_field(smali_path):
        """
        向 smali 文件添加一些随机的字段
        :param smali_path: 文件路径
        :type smali_path: str
        """
        with open(smali_path, 'a') as file:
            # 添加随机次数字段。这里不能太多，否则乘以要修改的数量也是一个庞大的数字，导致编译失败
            for i in range(random.randint(1, 2)):
                random_name = f'{"".join(random.sample(string.ascii_lowercase, 5))}{RandomNameUtils.random_class_name()}'
                # 写入随机变量
                file.write(f'.field public static final {random_name}:I = {random.randint(0, 1000)}\n')


    @staticmethod
    def append_smali_method(smali_path):
        """
        向 smali 文件添加一些随机的方法
        :param smali_path: 文件路径
        :type smali_path: str
        """
        with open(smali_path, 'a') as file:
            for i in range(random.randint(1, 2)):
                random_name = f'{"".join(random.sample(string.ascii_lowercase, 5))}{RandomNameUtils.random_class_name()}'
                # 写入随机方法
                file.write(f'.method public static {random_name}()V\n')
                file.write('    .locals 2\n')
                file.write('    const-string v0, "TAG"\n')
                file.write('    const-string v1, "Hello, World!"\n')
                file.write('    invoke-static {v0, v1}, Landroid/util/Log;->i(Ljava/lang/String;Ljava/lang/String;)I\n')
                file.write('    return-void\n')
                file.write('.end method\n')

class XmlUtils:

    @staticmethod
    def random_xml_resource(decompile_output_path: str, just_print: bool = False) -> None:
        """
        随机乱序可修改的 XML 资源。对于 values[-xx] 和 xml 目录下的 xml，调整二级节点的顺序不影响程序使用
        :param decompile_output_path: 反编译的结果输出目录
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        logging.debug('xml files randing...')
        xml_paths = FileUtils.search_files_with_dir_name(
            os.path.join(decompile_output_path, 'res'),
            lambda path: 'values' in path or 'xml' in path
        )
        print(xml_paths)
        for xml_path in xml_paths:
            XmlUtils.append_nodes_for_arrays(xml_path, just_print)
            XmlUtils.append_nodes_to_strings(xml_path, just_print)
            XmlUtils.append_nodes_to_attrs(xml_path, just_print)
            XmlUtils.append_nodes_to_bools(xml_path, just_print)
            XmlUtils.shuffle_xml_nodes(xml_path, just_print)
        logging.debug('xml files randed')

    @staticmethod
    def append_nodes_for_arrays(xml_path: str, just_print: bool = False) -> None:
        """
        在 arrays.xml 文件中追加一些节点
        :param xml_path: XML 文件路径
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        if 'arrays.xml' not in xml_path:
            return
        doc = parse(xml_path)
        root = doc.documentElement
        for i in range(random.randint(1, 5)):
            # 创建一个数组节点
            item_array = doc.createElement('string-array')
            item_array.setAttribute('name', f'string_box_{RandomNameUtils.random_xml_tag_name()}')
            # 随机创建内部数据
            for i in range(random.randint(1, 5)):
                inside_string = doc.createElement('item')
                inside_string.appendChild(doc.createTextNode(RandomNameUtils.random_en_string()))
                item_array.appendChild(inside_string)
            root.appendChild(item_array)
        if just_print:
            print(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            return
        with open(xml_path, 'w') as f:
            f.write(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
        logging.debug('append nodes in arrays.xml done')

    @staticmethod
    def append_nodes_to_strings(xml_path, just_print=False) -> None:
        """
        在 strings.xml 文件中追加一些节点
            1. 字符串节点，为避免警告，只操作 values 目录下的 strings.xml
        :param xml_path: XML 文件路径
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        if os.path.join('values', 'strings.xml') not in xml_path:
            return
        doc = parse(xml_path)
        root = doc.documentElement
        for i in range(random.randint(1, 5)):
            inside_string = doc.createElement('string')
            inside_string.setAttribute('name', f'string_item_{RandomNameUtils.random_xml_tag_name()}')
            inside_string.appendChild(doc.createTextNode(RandomNameUtils.random_en_string()))
            root.appendChild(inside_string)
        if just_print:
            print(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            return
        with open(xml_path, 'w') as f:
            f.write(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
        logging.debug('append nodes in strings.xml done')

    @staticmethod
    def append_nodes_to_attrs(xml_path, just_print=False) -> None:
        """
        在 attrs.xml 文件中追加一些节点
        :param xml_path: XML 文件路径
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        if 'attrs.xml' not in xml_path:
            return
        doc = parse(xml_path)
        root = doc.documentElement
        for i in range(random.randint(1, 5)):
            inside_attr = doc.createElement('attr')
            inside_attr.setAttribute('name', f'string_attr_{RandomNameUtils.random_xml_tag_name()}')
            inside_attr.setAttribute('format', 'reference')
            root.appendChild(inside_attr)
        for i in range(random.randint(1, 5)):
            inside_attr = doc.createElement('attr')
            inside_attr.setAttribute('name', f'enum_attr_{RandomNameUtils.random_xml_tag_name()}')
            for i in range(random.randint(1, 5)):
                inside_enum = doc.createElement('enum')
                inside_enum.setAttribute('name', f'enum_item_{RandomNameUtils.random_xml_tag_name()}')
                inside_enum.setAttribute('value', f'{i}')
                inside_attr.appendChild(inside_enum)
            root.appendChild(inside_attr)
        if just_print:
            print(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            return
        with open(xml_path, 'w') as f:
            f.write(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
        logging.debug('append nodes in attrs.xml done')

    @staticmethod
    def append_nodes_to_bools(xml_path, just_print=False) -> None:
        """
        在 bools.xml 文件中追加一些节点
        :param xml_path: XML 文件路径
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        if os.path.join('values', 'bools.xml') not in xml_path:
            return
        doc = parse(xml_path)
        root = doc.documentElement
        for i in range(random.randint(1, 5)):
            inside_bool = doc.createElement('bool')
            inside_bool.setAttribute('name', f'bool_item_{RandomNameUtils.random_xml_tag_name()}')
            inside_bool.appendChild(doc.createTextNode('false'))
            root.appendChild(inside_bool)
        if just_print:
            print(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            return
        with open(xml_path, 'w') as f:
            f.write(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
        logging.debug('append nodes in bools.xml done')

    @staticmethod
    def shuffle_xml_nodes(xml_path: str, just_print: bool = False) -> None:
        """
        打乱 XML 文件的节点顺序，只乱序二级节点不影响使用
        :param xml_path: XML 文件路径
        :param just_print: 是否只打印执行过程，如果是则不会写入文件
        """
        logging.debug('shuffle xml nodes...')
        doc = parse(xml_path)
        root = doc.documentElement
        children = list(root.childNodes)
        random.shuffle(children)
        for child in children:
            root.removeChild(child)
            root.appendChild(child)
        if just_print:
            print(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
            return
        with open(xml_path, 'w') as f:
            f.write(doc.toprettyxml(encoding='utf-8').decode('utf-8'))
        logging.debug(f'shuffle xml nodes in {xml_path} done')


class PictureUtil:

    @staticmethod
    def add_random_point_png_in_folder(folder_path):
        png_file_paths = FileUtils.search_files_with_file_name(
            folder_path, lambda path: '.9.png' not in path and '.png' in path
        )
        for png_file_path in png_file_paths:
            logging.debug(png_file_path)
            PictureUtil.add_random_point(png_file_path, png_file_path)

    @staticmethod
    def add_random_point(input_path, output_path):
        # 打开图片
        img = Image.open(input_path)
        # 图片的宽度和高度
        width, height = img.size
        # 随机选择一个点的坐标
        x = random.randint(0, width - 1)
        y = random.randint(0, height - 1)
        # 获取选定点的颜色
        pixel_color = img.getpixel((x, y))
        logging.debug(pixel_color)
        try:
            # 根据亮度进行调整
            brightness_threshold = sum(pixel_color[:3]) / 3 / 255  # 计算颜色的亮度
            factor = 1.05
            adjusted_color = PictureUtil.adjust_color_brightness(pixel_color, factor) if brightness_threshold > 0.5 \
                else PictureUtil.adjust_color_brightness(pixel_color, 1 / factor)
            # 在原图上绘制调整后的颜色
            draw = ImageDraw.Draw(img)
            draw.point((x, y), fill=adjusted_color)
        except Exception as e:
            logging.debug(e)
        # 保存生成的图片
        img.save(output_path, optimize=True, quality=75)

    @staticmethod
    def adjust_color_brightness(color, factor):
        """
        调整颜色的亮度

        Parameters:
        - color: 输入颜色，形如 (R, G, B) 或 (R, G, B, A)
        - factor: 亮度调整因子，大于 1 表示加深，小于 1 表示减深

        Returns:
        - 调整后的颜色，形如 (R, G, B) 或 (R, G, B, A)
        """
        adjusted_color = tuple(int(max(1, min(255, c * factor))) for c in color)
        return adjusted_color

if __name__ == '__main__':
    # ManifestUtils.random_manifest_metadata(
    #     '/Users/crux/Downloads/apkTest/gytyc-decompiled/AndroidManifest.xml',
    #         False)
    # SmaliUtils.append_folder_smali_field('/Users/crux/Downloads/apkTest/gytyc-decompiled')
    XmlUtils.random_xml_resource('/Users/crux/Downloads/apkTest/gytyc-decompiled', True)