import requests
import yaml
from requests.auth import HTTPBasicAuth
import json
import yml_tool


class JiraOperater():
    def __init__(self, base_url, username, password):  # 初始化属性值
        self.base_url = base_url
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)

    #  通过测试周期name和测试计划的key获得测试周期内全部的测试用例
    def get_testruns_by_cycle_name_and_testplan_key_new(self, testplan_key, cycle_name):
        """
        通过测试周期name和测试计划的key获得测试周期内全部的测试用例

        :param testplan_key:测试计划key

        :param cycle_name:测试周期name

        :return:返回测试计划内的测试周期内的测试用例的issuekey,并写入testcase_key.yaml文件
        """
        api_url = f"{self.base_url}/rest/synapse/latest/public/testPlan/{testplan_key}/cycle/{cycle_name}/testRuns"

        try:
            # 发送 GET 请求到 Jira API
            response = requests.get(api_url, auth=self.auth)

            # 检查响应状态码
            if response.status_code == 200:
                # 解析 JSON 响应
                data = json.loads(response.text)

                # 提取 testCaseKey 并构建列表
                testcase_keys = [item["testCaseKey"] for item in data if "testCaseKey" in item]

                try:
                    with open('../temp/data01.yml', 'w', encoding='utf-8') as file:
                        yaml.dump(testcase_keys, file, allow_unicode=True)
                except Exception as e:
                    print(f"写入该文件发生错误：{e}")

                return testcase_keys
            else:
                print(f"请求失败，HTTP状态码: {response.status_code}")
                return None
        except requests.exceptions.RequestException as e:
            print(f"请求发生错误: {e}")
            return None


config_data = yml_tool.read_yml()

username = config_data['username']
password = config_data['password']
testplan_key = config_data['testplan_key']
cycle_name = config_data['cycle_name']
base_url = "http://jira.jaguarmicro.com"

if __name__ == '__main__':
    jira = JiraOperater(base_url, username, password)  # 创建JiraOperater对象

    jira.get_testruns_by_cycle_name_and_testplan_key_new(testplan_key, cycle_name)
