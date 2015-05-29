import sqlite3
import time
import json
import BaseHTTPServer


HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 12888 # Maybe set this to 9000.

class RestSystem:
    #TODO: security check
    def status_ok(self):
        return {"status": "ok"}

    def status_error(self, error):
        return {"error": error}

    def __init__(self):
        self.sql = sqlite3.connect('rest.db')

    def getResponse(self, data):
        a = data["action"]
        if a == "create_user":
            return self.createUser(data)
        return self.status_error("Action is not found")

    def createUser(self, data):
        c = self.sql.cursor()
        c.execute("INSERT INTO users (name) VALUES ('{name}')".format(**data));
        self.sql.commit();
        return self.status_ok()

    def createPost(self, data):
        pass

    def hateHashtag(self, data):
        pass

    def likePost(self, data):
        pass

    def getAlarms(self, data):
        pass

    def getPosts(self, data):
        pass

    def setReleaseTime(self, data):
        pass

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
        res = (RestSystem()).getResponse(data)
        print "Result:", res
        s.wfile.write(json.dumps(res))

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_HEAD(s):
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
    def do_GET(s):
        """Respond to a GET request."""
        s.send_response(200)
        s.send_header("Content-type", "text/html")
        s.end_headers()
        s.wfile.write("<html><head><title>Title goes here.</title></head>")
        s.wfile.write("<body><p>This is a test.</p>")
        
        
        conn = sqlite3.connect('mydb.db')
        c = conn.cursor()
        c.execute("INSERT INTO entries VALUES (CURRENT_TIMESTAMP);")
        conn.commit()
        get = conn.cursor()
        for row in get.execute("SELECT time FROM entries"):
            s.wfile.write(row[0])
            s.wfile.write("<br>")

        # If someone went to "http://something.somewhere.net/foo/bar/",
        # then s.path equals "/foo/bar/".
        s.wfile.write("<p>You accessed path: %s</p>" % s.path)
        s.wfile.write("</body></html>")
    def do_POST(s):
        s.send_response(200)
        s.end_headers()
        varLen = int(s.headers['Content-Length'])
        print "Data:"
        print s.rfile.read(varLen)


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
