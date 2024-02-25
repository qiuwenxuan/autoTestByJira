import subprocess
import os
import sys
import yaml
import yml_tool


def get_numbered_files():
    files = os.listdir('.')  # 获取当前目录下的所有文件名
    numbered_files = []
    for file in files:
        if file[0].isdigit():  # 如果文件名的第一个字符是数字
            numbered_files.append(file)
    numbered_files.sort(key=lambda x: int(x.split('.')[0][0]))
    return numbered_files


def main():
    for file in get_numbered_files():  # 遍历文件名

        print(f'{file}运行中……')
        # 对于其他文件，不传递参数并使用 subprocess.Popen
        process = subprocess.Popen(['python', file])
        process.wait()

        print(f'{file}运行完毕！')


def save_config_to_yaml(args, file_path):
    with open(file_path, 'w') as file:
        yaml.dump(args, file)


if __name__ == "__main__":
    # 接收除脚本名之外的所有命令行参数
    args = sys.argv[1:]
    # main()
    config_data = {}
    config_data['username'] = args[0]
    config_data['password'] = args[1]
    config_data['testplan_key'] = args[2]
    config_data['cycle_name'] = args[3]
    config_data['robotpath'] = r'Z:\code\sw_itest\tests\robotFramework\DPE'
    config_data['pytestpath'] = r'Z:\code\sw_itest\tests\pytestCase'
    config_data['currentpath'] = os.getcwd()

    yml_tool.write_yml(config_data, '../res/config.yml')
    main()
