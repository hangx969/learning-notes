import subprocess

def add_server_block(file_path, server_block) -> None:
    with open(file_path, 'a') as f:
        f.write(server_block)
    print("New server block has been added to nginx config file.")

def reload_nginx() -> None:
    try:
        result = subprocess.run(['systemctl','reload', 'nginx'], capture_output=True, text=True, check=True)
        print("Nginx is reloaded successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to reload nginx: {e.stderr}.")

if __name__ == '__main__':
    config = '/etc/nginx/nginx.conf'
    new_server_block = """
    server {
    listen 8080;
    server_name example.com;
    location / {
        proxy_pass http://localhost:8000;
    }
    }
    """

    add_server_block(config, new_server_block)
    reload_nginx()
