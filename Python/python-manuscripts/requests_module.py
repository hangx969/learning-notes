import requests

url = 'https://httpbin.org/redirect/1'
response = requests.get(url, allow_redirects=False)
print(f"Status code: {response.status_code}.")
print(f"Redirect URL: {response.headers.get('Location')}")
print(response.content)

url = 'https://httpbin.org/redirect/1'
response = requests.get(url)
print(f"Status code: {response.status_code}.")
print(f"Redirect URL: {response.headers.get('Location')}")
print(response.content)