import json

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


def get_testruns_by_cycle_name_and_testplan_key(testplan_key, cycle_name):
    api_url = f"{base_url}/rest/synapse/latest/public/testPlan/{testplan_key}/cycle/{cycle_name}/testRuns"

    try:
        # 发送 GET 请求到 Jira API
        response = requests.get(api_url, auth=HTTPBasicAuth(username, password))

        # 检查响应状态码
        if response.status_code == 200:
            # 解析 JSON 响应

            project_info = json.dumps(json.loads(response.text), sort_keys=True, indent=4,
                                      ensure_ascii=False)  # 转化为json换行的可读形式

            testrun_dates = json.loads(project_info)

            output_file_date = {testrun_date["testCaseKey"]: testrun_date["id"] for testrun_date in testrun_dates}

            with open("../temp/data05.yml", 'w') as file:
                yaml.dump(output_file_date, file)

            return output_file_date
        else:
            print(f"请求失败，HTTP状态码: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"请求发生错误: {e}")
        return None


get_testruns_by_cycle_name_and_testplan_key(testplan_key, cycle_name)
