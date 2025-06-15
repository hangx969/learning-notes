import requests

url = 'https://httpbin.org/redirect/3'
response = requests.get(url)
for r in response.history:
    print(f"Redirect url: {r.url}")