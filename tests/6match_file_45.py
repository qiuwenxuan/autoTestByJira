import yaml


def read_yaml(file_path):
    """读取 YAML 文件内容"""
    with open(file_path, 'r') as file:
        data = yaml.safe_load(file)
    return data


def match_and_write_yaml(file_path1, file_path2, output_file_path='../temp/data06.yml'):
    """
    匹配两个 YAML 文件中相同的键，并将结果写入新的 YAML 文件。

    :param file_path1: 第一个 YAML 文件的路径（例如：'shell5.yml'）
    :param file_path2: 第二个 YAML 文件的路径（例如：'shell6.yml'）
    :param output_file_path: 输出文件的路径
    """
    # 读取文件
    data1 = read_yaml(file_path1)
    data2 = read_yaml(file_path2)

    # 匹配键并组合值
    matched_values = {data2[key]: data1[key] for key in data1 if key in data2}

    # 写入新的 YAML 文件
    with open(output_file_path, 'w') as file:
        yaml.dump(matched_values, file)


# 使用示例
file_path_shell5 = '../temp/data04.yml'
file_path_shell6 = '../temp/data05.yml'

match_and_write_yaml(file_path_shell5, file_path_shell6)
