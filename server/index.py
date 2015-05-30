from flask import Flask
import main
app = Flask(__name__)

@app.route('/')
def index():
    data = ""  
    for t in request.POST:
        data += t
    try:
        return DoAllIwant(data)
    except:
        return '{error: "error"}'


    if __name__ == '__main__':
            app.run()
