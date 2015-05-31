from flask import Flask, request
import main
app = Flask(__name__)

@app.route('/', methods = ['POST'])
def index():
    data = ""  
    try:
     #   for t in request.POST:
     #           data += t
#        return main.DoAllIwant(request.get_data())
        return main.getOlool(request.get_data())
    except Exception as abc:
#        return str("Pavel's exception: " + abc)
        return "error!"

if __name__ == '__main__':
    app.run()


