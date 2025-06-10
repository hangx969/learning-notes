import yaml, os

def get_config(yaml_dir):
    report = []
    for file in os.listdir(yaml_dir):
        if file.endswith('.yaml'):
            with open(os.path.join(yaml_dir,file), 'r') as f:
                config = yaml.safe_load(f)
            name = config['metadata']['name']
            image = config['spec']['template']['spec']['containers'][0]['image']
            report.append(f"Service name: {name}, image version: {image}")
    return report

if __name__ == '__main__':
    os.chdir('Python/python-manuscripts')
    yaml_dir = 'configs'
    report = get_config(yaml_dir)
    for line in report:
        print(line)