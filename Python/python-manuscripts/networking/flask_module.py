from flask import Flask

app = Flask(__name__) # __name__是当前模块的名字
@app.route("/") # 定义路由

def home():
    return "Hello from Flask"

if __name__ == "__main__":
    app.run(debug=True)