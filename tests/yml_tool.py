import yaml


def write_yml(output_data, output_file_path):
    with open(output_file_path, 'w', encoding='utf-8') as file:
        yaml.dump(output_data, file, allow_unicode=True)


def read_yml(input_file_path='../res/config.yml'):
    with open(input_file_path, 'r', encoding='utf-8') as file:
        input_data = yaml.safe_load(file)
        return input_data


def append_yml(output_data, output_file_path):
    with open(output_file_path, 'a', encoding='utf-8') as file:
        yaml.dump(output_data, file, allow_unicode=True)
