import subprocess

command = ['docker', 'pull', 'calico/kube-controllers:v3.31.0-0.dev-507-gdc1c0b1b3c18']


while True:
    try:
        result = subprocess.run(command, capture_output=True, check=True, text=True)
        if result.returncode == 0:
            print(result.stdout)
            break
    except subprocess.CalledProcessError as e:
        print(f"Command failed with: {str(e)}.")