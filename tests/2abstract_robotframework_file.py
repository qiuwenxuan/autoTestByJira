import ast

import robot.errors
import yaml
import os
from robot.api import TestSuiteBuilder
import yml_tool


def robot2yaml(current_path, frame_path):
    result = {}
    os.chdir(frame_path)
    current_directory = os.getcwd()
    dir2dict(current_directory, result)
    yaml_data = result
    # Save the parsed data to a YAML file
    os.chdir(current_path)
    output_file = '../temp/data02_robot.yml'
    with open(output_file, 'w', encoding='utf-8') as file:
        file.write(yaml.safe_dump(yaml_data, allow_unicode=True))


def parse_robot_file(robot_file):
    test_cases = []
    builder = TestSuiteBuilder()
    # Load the Robot Framework file
    try:
        suite = builder.build(robot_file)
    except robot.errors.DataError:
        return None
    # Iterate over test cases in the file
    for test in suite.tests:
        test_cases.append(test.name)

    # Create a dictionary with the test case data

    return test_cases


def dir2dict(directory: str, d: dict):
    for root, dirs, files in os.walk(directory):
        for dir in dirs:
            temp = {}
            # We pass temp as a new dictionary for the subdirectory
            dir2dict(os.path.join(root, dir), temp)
            if temp:  # Only add non-empty dictionaries
                d[dir] = temp
        for file in files:
            if file.endswith('.robot'):
                data = parse_robot_file(os.path.join(root, file))
                if data:
                    d[file] = data
        break  # Only process the first layer of directories/files

    return bool(d)  # Return True if the dictionary is not empty


class PytestFeatureVisitor(ast.NodeVisitor):  # 创建工具类去遍历其他文件下的所有类定义
    def __init__(self):
        self.classes = {}

    def visit_ClassDef(self, node):
        """
        重写ast.NodeVisitor的类方法，每当遇到类定义时，都会调用此方法，用于访问AST中所有的类定义（ClassDef节点）

        @param node: 当前指针所指类定义对象

        @return: 将提取的方法列表与当前类名关联，储存在初始化集合classes内
        """
        current_class = node.name
        methods = []
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                feature = self.extract_feature(item.decorator_list)
                methods.append((item.name, feature))
        self.classes[current_class] = methods

    def extract_feature(self, decorators):
        """
        遍历节点树查找需要的标签

        @param decorators:装饰器列表

        @return:如果在装饰器列表中找到了匹配的feature装饰器并提取了其参数，函数返回该参数（一个字符串）。如果没有找到匹配的装饰器，函数返回 None。
        """
        for decorator in decorators:
            if isinstance(decorator, ast.Call) and hasattr(decorator.func, 'attr') and decorator.func.attr == 'feature':
                if len(decorator.args) > 0 and isinstance(decorator.args[0], ast.Str):
                    return decorator.args[0].s
        return None


def get_pytest_date_in_file(file_path):
    """
    获取python文件内的类，方法和对应的feature

    @param file_path: 传入.py文件和路径

    @return: 返回文件内所有以Test开头的文件的类定义数据，返回形式 文件{类{方法：testissue_key}
    """
    with open(file_path, 'r', encoding='utf-8') as file:
        node = ast.parse(file.read())
        visitor = PytestFeatureVisitor()
        visitor.visit(node)
        return visitor.classes


def get_pytest_date_in_directory(directory_path):
    """
    获取文件夹内python文件夹内的类，方法和对应的feature

    @param directory_path: 传入含.py文件的文件夹路径

    @return: 返回文件夹内所有以Test开头的文件的类定义数据，返回形式 文件{类{方法：testissue_key}
    """
    all_features = {}
    for root, dirs, files in os.walk(directory_path):
        for file in files:
            if file.startswith('test') and file.endswith('.py'):
                file_path = os.path.join(root, file)
                file_features = get_pytest_date_in_file(file_path)
                all_features[file] = file_features
    return all_features


def save_to_yaml_file(data, output_file):
    """
    将从python文件抽象出来的数据写入yaml文件并输出

    @param data: 输入的数据

    @param output_file: 输出文件的绝对路径

    @return:将抽象出来的数据保存为名为 `output.yaml` 的文件。
    """
    transformed_data = {cls: {method: feature for method, feature in methods} for cls, methods in data.items()}
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            yaml.dump(transformed_data, file, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        print(f"写入文件过程中发生错误：{e}")

    # 检查文件是否存在，无论是否捕获到异常


def save_to_yaml_directory(data, output_file):
    """
    将从文件夹内python文件抽象出来的数据写入yaml文件并输出

    @param data: 输入的数据

    @param output_file: 输出文件的绝对路径

    @return:将抽象出来的数据保存为名为 `output.yaml` 的文件。
    """
    transformed_data = {
        file: {cls: {method: feature for method, feature in methods} for cls, methods in class_methods.items()} for
        file, class_methods in data.items()}
    try:
        with open(output_file, 'w', encoding='utf-8') as file:
            yaml.dump(transformed_data, file, default_flow_style=False, allow_unicode=True)
    except Exception as e:
        print(f"写入文件过程中发生错误：{e}")

    # 检查文件是否存在，无论是否捕获到异常


def get_file_and_class_and_method_in_pytest(file_path, output_file='../temp/data02_pytest.yml'):
    """
    提供外部调用的方法：传入包含Test开头的python文件的文件夹，输出抽象的数据并导出为yaml文件

    @param file_dir: 传入需要抽象数据的Python文件的路径。

    @return: 无。结果将抽象出来的数据保存为名为 `output.yaml` 的文件。
    """

    result = get_pytest_date_in_directory(file_path)
    save_to_yaml_directory(result, output_file)


if __name__ == '__main__':
    current_path = yml_tool.read_yml()['currentpath']
    robot_path = yml_tool.read_yml()['robotpath']
    robot2yaml(current_path, robot_path)
    pytest_path = yml_tool.read_yml()['pytestpath']
    get_file_and_class_and_method_in_pytest(pytest_path)
