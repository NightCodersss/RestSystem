import sqlite3
import datetime
import time
import json
import BaseHTTPServer
import main

HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 12888

class RestSystemHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>You are wrong</title></head>")
        s.wfile.write("<body><p>This API does work through POST method.</p>")
        s.wfile.write("</body></html>")

    def do_POST(s):
        s.send_response(200)
        s.send_header("Access-Control-Allow-Origin", "*")
        s.end_headers()
        varLen = int(s.headers['Content-Length'])
        print "Got data:"
        post = str(s.rfile.read(varLen));
        print post
        try:
            data = json.loads(post);
        except:
            print "Error: json decode"
            s.wfile.write("{\"error\": \"data is not correct JSON\"}")
            return
        print data
        res = (main.RestSystem()).getResponse(data)
        print "Result:", res
        s.wfile.write(json.dumps(res))

if __name__ == '__main__':
    server_class = BaseHTTPServer.HTTPServer
    httpd = server_class((HOST_NAME, PORT_NUMBER), RestSystemHandler)
    print time.asctime(), "Server Starts - %s:%s" % (HOST_NAME, PORT_NUMBER)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    print time.asctime(), "Server Stops - %s:%s" % (HOST_NAME, PORT_NUMBER)
