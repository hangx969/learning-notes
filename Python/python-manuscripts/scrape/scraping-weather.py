import requests
import json

#基础设置
base_url = "http://api.openweathermap.org/data/2.5/weather"
city = "New York"
country = "US"
api_key = "xxx"

# 构造查询url
url = f"{base_url}?q={city},{country}&appid={api_key}&units=metrics"

try:
    # 发送get请求
    response = requests.get(url)
    if response.status_code == 401:
        print("Failed to authenticate.")
    elif response.status_code == 404:
        print("Page Not Found, please check the url")
    elif response.status_code == 200:
        # 返回的data是字典
        data = response.json()
        # 返回的字段里面的cod表示状态码，不是200表示请求出错
        if data.get('cod') != 200:
            print(f"Request URL is not correct: {data.get('message')}")
        else:
            # 构造一个字典包含想要的天气信息
            weather = {
                'city': data.get('name'),
                'country': data.get('sys',{}).get('country'),
                'temerature': data.get('main',{}).get('temp'),
                'humidity': data.aget('main',{}).get('humidity'),
                # weather字段下是一个列表，列表元素是字典，所以get的默认值设为[{}]
                'description': data.get('weather',[{}])[0].get('description')
            }
            print("Weather: ")
            # 把python字典转成json格式打印
            print(json.dumps(weather, indent=4))
            with open('scrape/weather.txt', 'w', encoding='utf-8') as f:
                f.write("Weather\n")
                f.write(json.dumps(weather, indent=4))
            print("Weather info has been saved to weather.txt")
    else:
        print("Status code is unknown")

except Exception as e:
    print(f"Error: {str(e)}")