import yaml

yaml_str = """
name: John
age: 30
languages:
- Python
- Java
"""

data = yaml.safe_load(yaml_str)
print(data)