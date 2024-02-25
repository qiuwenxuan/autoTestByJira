import yaml


def find_test_cases_recursive(testissue_keys, test_struct, path=[], matches=None):
    if matches is None:
        matches = {}

    if isinstance(test_struct, dict):
        for key, value in test_struct.items():
            find_test_cases_recursive(testissue_keys, value, path+[key], matches)
    elif isinstance(test_struct, list):
        for test_case in test_struct:
            for testissue_key in testissue_keys:
                if testissue_key in test_case:
                    full_path = " > ".join(path)
                    matches.setdefault(testissue_key, []).append((full_path, test_case))

    return matches


def create_yaml_output(file_path_1, file_path_2, output_file_path):
    # Load and parse the YAML files
    with open(file_path_1, 'r', encoding='utf-8') as file1:
        testissue_keys = yaml.safe_load(file1)

    with open(file_path_2, 'r', encoding='utf-8') as file2:
        test_cases = yaml.safe_load(file2)

    # Finding the matches with a recursive approach
    matches = find_test_cases_recursive(testissue_keys, test_cases)

    # Creating the output structure
    output_data = {}
    for key, matched_tests in matches.items():
        for path, test_case in matched_tests:
            # Splitting the path and adding the test case to the nested dictionary
            path_elements = path.split(" > ")
            current_level = output_data

            for element in path_elements:
                current_level = current_level.setdefault(element, {})

            current_level[test_case] = key

    # Writing the structured data to the new YAML file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        yaml.dump(output_data, file, allow_unicode=True)


def merge_and_filter_yaml(input_file1_path, input_file2_path, output_file_path):
    """
    该函数接收两个YAML文件的路径作为输入，将shell1.yml和shell2.yml做一个映射，输出映射后的文件shell3.yml

    @param input_file1_path: 文件1的路径（包含测试周期内测试用例的issuekey的YAML文件）

    @param input_file2_path: 文件2的路径（包含抽象出的YAML数据文件）

    @param output_file_path: 输出文件的路径，默认为当前目录下的shell3.yaml文件

    @return: 无返回值。函数会生成一个新的YAML文件,输出映射后的shell3.yml
    """
    with open(input_file1_path, 'r') as file:
        shell1_data = yaml.safe_load(file)

    with open(input_file2_path, 'r') as file:
        output_data = yaml.safe_load(file)

    filtered_output_data = {}

    for file, tests in output_data.items():
        for test_class, test_cases in tests.items():
            filtered_cases = {case: key for case, key in test_cases.items() if key in shell1_data}
            if filtered_cases:
                if file not in filtered_output_data:
                    filtered_output_data[file] = {}
                filtered_output_data[file][test_class] = filtered_cases

    try:
        with open(output_file_path, 'w') as file:
            yaml.dump(filtered_output_data, file)
    except Exception as e:
        print(f"写入文件过程中发生错误：{e}")


# File paths
file_path_1 = '../temp/data01.yml'  # Path to your first file
robot_path_2 = '../temp/data02_robot.yml'  # Path to your second file
pytest_path_2 = '../temp/data02_pytest.yml'  # Path to your second file
output_robot_file_path = '../temp/data03_robot.yml'  # Desired path for the output file
output_pytest_file_path = '../temp/data03_pytest.yml'  # Desired path for the output file

# Generate the output file
create_yaml_output(file_path_1, robot_path_2, output_robot_file_path)
merge_and_filter_yaml(file_path_1, pytest_path_2, output_pytest_file_path)
