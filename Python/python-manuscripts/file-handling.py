import re

config_files = ['config1.conf', 'config2.conf']
pattern = re.compile(r'(DB_CONNECTION="mysql://)([^:]+)(:password@localhost/[^"]+)')
new_user = 'admin_user'

for file in config_files:
    with open(file, 'r') as f:
        content = f.read()

    new_content = pattern.sub(r'\1' + new_user + r'\3', content)

    with open(file, 'w') as f:
        f.write(new_content)

    print(f"Updated {file}")