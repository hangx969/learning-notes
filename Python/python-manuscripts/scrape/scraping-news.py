import requests

def fetch_news(api_key):
    #构造API
    url = f"https://newsapi.org/v2/top-headlines?country=us&apikey={api_key}"
    # 发送get请求
    response = requests.get(url)
    if response.status_code == 200:
        # 把json格式数据转成python字典
        data = response.json()
        # 从相应数据里面获取articles字段，返回的是列表
        articles = data.get('articles',[{}])
        for article in articles:
            title = article.get('title','N/A')
            description = article.get('description', 'N/A')
            link = article.get('url', 'N/A')
            with open('scrape/news.txt', 'a', encoding='utf-8') as f:
                f.write(f"Title: {title}\nDescription: {description}\nURL: {url}\n")
            print("News has been save to news.txt")
    else:
        print(f"Failed to fetch news, status code is {response.status_code}.")

if __name__ == '__main__':
    fetch_news("xxxx")