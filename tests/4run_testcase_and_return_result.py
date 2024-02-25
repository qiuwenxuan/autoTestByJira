from xml.etree import ElementTree as ET
import json
import os
import yaml
import subprocess
import yml_tool

result_robot = {'PASS': '1', 'FAIL': '2'}
result_pytest = {'passed': '1', 'failed': '2'}


def generate_command_from_yaml(yaml_data, log_dir="./"):
    command = ["python", "pybot-cli.py", "--loglevel", "DEBUG", "--listener", "allure_robotframework"]

    # 检查嵌套层级并生成命令
    for suite, content in yaml_data.items():
        if isinstance(content, dict):
            for key, value in content.items():
                if isinstance(value, dict) and all(isinstance(v, str) for v in value.values()):
                    # 三层嵌套情况
                    file = key[:-6] if key.endswith('.robot') else key
                    suite_path = f"{suite}.{file}"
                    command.extend(["-s", suite_path])
                    for test_case in value.keys():
                        command.extend(["-t", test_case])
                else:
                    # 四层嵌套情况，跳过最外层
                    for sub_suite, files in content.items():
                        for file, test_cases in files.items():
                            file = file[:-6] if file.endswith('.robot') else file
                            suite_path = f"{sub_suite}.{file}"
                            command.extend(["-s", suite_path])
                            for test_case in test_cases.keys():
                                command.extend(["-t", test_case])
        else:
            # 处理非字典类型的意外情况
            print(f"Unexpected format in YAML data: {suite}: {content}")

    command.append(log_dir)
    return command


def execute_command(command):
    # print(command)
    subprocess.run(command)


def match_and_save(xml_file_path, yml_data_path, yml_output_path):
    # 从XML文件中获取测试用例
    test_cases = parse_xml(xml_file_path)

    # 读取data03.yml文件
    with open(yml_data_path, 'r', encoding='utf-8') as file:
        data03 = yaml.safe_load(file)

    # 遍历data03.yml中的所有测试用例
    matched_results = {}
    for _, suite in data03.items():
        for key, value in suite.items():
            # 检查是否是测试用例字典
            if isinstance(value, dict) and all(isinstance(v, str) for v in value.values()):
                test_case_dict = value
                match_test_cases(test_cases, test_case_dict, matched_results)
            else:  # 进一步嵌套的情况
                for test_file, cases in value.items():
                    match_test_cases(test_cases, cases, matched_results)

    # 保存匹配结果到data04.yml
    with open(yml_output_path, 'w') as file:
        yaml.dump(matched_results, file)


def match_test_cases(test_cases, test_case_dict, matched_results):
    for case_name, jira_id in test_case_dict.items():
        # 匹配测试用例名称
        for name, status in test_cases:
            if case_name in name:
                matched_results[jira_id] = result_robot[status]
                break


def parse_xml(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()
    test_cases = []
    for test in root.iter('test'):
        name = test.get('name')
        status = test.find('status').get('status')
        test_cases.append((name, status))
    return test_cases


def build_pytest_expression(test_cases):
    """
    根据读取到的测试用例数据构建pytest命令行表达式

    :param test_cases: 读取到的测试用例，以文件:类:方法形式

    :return: 返回构建好的测试用例表达式
    """
    expressions = []
    for file, classes in test_cases.items():
        for class_name, methods in classes.items():
            for method in methods.keys():
                # 构建表达式：文件::类::方法
                expressions.append(f"{file}::{class_name}::{method}")
    return " ".join(expressions)


def run_pytest(expression, allure_report, report_file='report.json'):
    """
    使用 subprocess 运行 pytest,并输出json格式的report

    :param expression: 传入pytest命令

    :param report_file:json格式的测试报告的生成路径

    :return: 返回生成的测试报告的路径
    """
    allure_report_path = allure_report+'/output/allure'
    command = f"python -m pytest {expression} --alluredir={allure_report_path} --json-report --json-report-file={report_file}"
    subprocess.run(command, shell=True)
    file_path = os.path.abspath(report_file)
    return file_path


def output_test_report(report_file_path, output_file_path='../temp/data04_pytest.yml'):
    """
    读取并解析 JSON 测试报告文件，提取测试用例的名称和状态。

    :param report_file_path: JSON 测试报告文件的路径

    :return: 包含测试用例名称和状态的列表
    """
    test_results = {}

    # 读取并解析 JSON 文件
    with open(report_file_path, 'r') as file:
        report_data = json.load(file)

    # 提取测试用例的名称和状态
    for test in report_data['tests']:
        test_name = test['nodeid']  # 测试用例的名称
        test_status = test['outcome']  # 测试用例的执行状态

        test_results.update({
            test_name: test_status})  # 以字典的形式存储数据信息 test_blkdev.py::TestLegacyblkDev::test_blkpf_legacy_driver_ok[legacy]: failed

    with open(output_file_path, 'w') as file:
        yaml.dump(test_results, file, default_flow_style=False, allow_unicode=True)


def integrate_file(shell3_data, shell4_data):
    """
    整合 shell3.yml 和 shell4.yml 的内容

    :param shell3_data: shell3.yml 文件内容
    :param shell4_data: shell4.yml 文件内容
    :return: 新格式的匹配结果
    """
    integrated_results = {}

    for file, classes in shell3_data.items():
        for class_name, tests in classes.items():
            for test_method, jira_id in tests.items():
                # 匹配测试用例，忽略可变部分（如 [legacy]）
                for shell4_test in shell4_data:
                    if shell4_test.startswith(f"{file}::{class_name}::{test_method}"):
                        if shell4_data[shell4_test] == 'passed':
                            integrated_results[jira_id] = result_pytest[shell4_data[shell4_test]]
                        else:
                            integrated_results[jira_id] = 'failed'
                            integrated_results[jira_id] = result_pytest[integrated_results[jira_id]]

    return integrated_results


if __name__ == '__main__':
    current_path = yml_tool.read_yml()['currentpath']
    robot_path = yml_tool.read_yml()['robotpath']
    # 设置文件路径
    xml_file_path = robot_path+'/output.xml'  # 替换为实际的XML文件路径
    data03_robot_file_path = '../temp/data03_robot.yml'  # Update with the actual path if necessary
    data04_file_path = '../temp/data04.yml'  # 替换为期望保存data04.yml的路径

    with open(data03_robot_file_path, 'r', encoding='utf-8') as file:
        yaml_data = yaml.safe_load(file)
    if yaml_data:
        # Generate and execute command
        command = generate_command_from_yaml(yaml_data)
        os.chdir(robot_path)
        execute_command(command)
        os.chdir(current_path)
        match_and_save(xml_file_path, data03_robot_file_path, data04_file_path)
    # ===============================pytest=============================
    file3_path = '../temp/data03_pytest.yml'
    # 加载测试用例并构建 pytest 表达式
    test_cases = yml_tool.read_yml(file3_path)
    # 读取shell3.yml文件下的测试用例数据
    if test_cases:
        pytest_path = yml_tool.read_yml()['pytestpath']
        os.chdir(pytest_path)
        expression = build_pytest_expression(test_cases)  # 创建pytest表达式
        report_file_path = run_pytest(expression, robot_path)  # 传入表达式expression，运行并返回生成json数据文件的地址
        os.chdir(current_path)
        output_test_report(report_file_path)  # 解析数据文件，获取测试用例的执行结果

    # ===================================解析pytest测试结果=======================================
    # 读取 shell3.yml 和 shell4.yml 文件
    shell3_pytest_data = yml_tool.read_yml('../temp/data03_pytest.yml')  # 替换为实际的 shell3.yml 文件路径
    shell4_pytets_data = yml_tool.read_yml('../temp/data04_pytest.yml')  # 替换为实际的 shell4.yml 文件路径

    # 整合 shell3.yml 和 shell4.yml 的内容
    integrated_results = integrate_file(shell3_pytest_data, shell4_pytets_data)

    # 准备写入新 YAML 文件的数据
    # 写入数据到新的 YAML 文件 shell5.yml
    yml_tool.append_yml(integrated_results, data04_file_path)  # 替换为实际的 shell5.yml 文件路径
