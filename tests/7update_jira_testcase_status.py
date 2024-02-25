import os
import shutil

from requests.auth import HTTPBasicAuth

import yml_tool
import requests
import yaml

config_data = yml_tool.read_yml()
username = config_data['username']
password = config_data['password']
testplan_key = config_data['testplan_key']
cycle_name = config_data['cycle_name']
base_url = "http://jira.jaguarmicro.com"


def update_testrun_by_run_id(testcase_key, run_id, status_id):
    api_url = f"{base_url}/rest/synapse/1.0/testRun/updateTestRunStatus?runId={run_id}&status={status_id}"
    headers = {

        "Content-Type": "application/json"
    }
    try:
        response = requests.put(api_url, headers=headers, auth=HTTPBasicAuth(username, password))

        if response.status_code == 200:
            # 解析 JSON 响应

            project_info = f"测试用例{testcase_key} 更新成功！"
            return project_info
        else:
            print(f"请求失败，HTTP状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None


def read_yaml_data(file_path):
    with open(file_path, 'r') as file:
        file_data = yaml.safe_load(file)
    return file_data


def main():
    shell5_path = r'../temp/data05.yml'
    file5_data = read_yaml_data(shell5_path)
    shell6_path = '../temp/data06.yml'
    file6_data = read_yaml_data(shell6_path)
    list1 = list(file5_data.keys())
    list2 = list(file6_data.items())

    for i in range(len(list2)):
        res = update_testrun_by_run_id(list1[i], list2[i][0], list2[i][1])
        print(res)

    #  删除res文件夹下的yml文件
    folder_path = '../temp'
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            os.remove(file_path)


if __name__ == '__main__':
    main()
