import sqlite3
import datetime
import time
import json
import BaseHTTPServer


HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 12888 # Maybe set this to 9000.
token_check_url = "https://www.googleapis.com/oauth2/v1/tokeninfo?id_token="

def check(data, requied_fields):
    try:
        for f in requied_fields:
            data[f]
    except:
        return False
    return True

def randomId():
    import random
    #TODO: check for duplicates
    return random.randrange(1000000)

class RestSystem:
    def status_ok(self):
        return {"status": "ok"}

    def status_error(self, error):
        return {"error": error}

    def __init__(self):
        self.sql = sqlite3.connect('rest.db', detect_types=sqlite3.PARSE_DECLTYPES)
        #TODO: logining
        self.uid = 228

    def getResponse(self, data):
        a = data["action"]
        if not check(data, ["token"]):
            return self.status_error("Token is requried")
        import urllib2
        user = json.loads(urllib2.urlopen(token_check_url+data["token"]).read())
        self.uid = user["user_id"]
        print "UID:", self.uid
        
        if a == "signin":
            return self.signin(data)
        if a == "create_user":
            return self.createUser(data)
        if a == "create_post":
            return self.createPost(data)
        if a == "hate_hashing":
            return self.hateHashtag(data)
        if a == "like_post":
            return self.likePost(data)
        if a == "get_alarms":
            return self.getAlarms(data)
        if a == "get_posts":
            return self.getPosts(data)

        return self.status_error("Action is not found")

    def signin(self, data):
        c = self.sql.cursor()
        if c.execute("SELECT COUNT(*) FROM users WHERE uid=?", (self.uid, )).next()[0] != 0:
            return {"instructions": "login"}
        else:
            return {"instructions": "register"}

    def createUser(self, data):
        c = self.sql.cursor()

        if check(data, ["name", "gid"]):
            if self.existGroup(data["gid"]):
                c.execute("INSERT INTO users (name) VALUES (?)", (data["name"],));
                c.execute("INSERT INTO groups_users (gid, uid) values (?, ?)", (data["gid"], self.uid));
                self.sql.commit()
                return self.status_ok()
            else:
                return self.status_error("There is no such group")
        elif check(data, ["name", "group_name"]):
            gid = self.createGroup(data["group_name"])
            c.execute("INSERT INTO users (name) VALUES (?)", (data["name"], ));
            c.execute("INSERT INTO groups_users (gid, uid) values (?, ?)", (gid, self.uid));
            self.sql.commit()
            return self.status_ok()

        return self.status_error("Some requred fields are not filled");

    def existGroup(self, gid):
        #ugly
        c = self.sql.cursor()
        for _ in c.execute("SELECT gid FROM groups WHERE gid=?", (gid, )):
            return True
        return False

    def createGroup(self, name):
        c = self.sql.cursor()
        gid = randomId()
        c.execute("INSERT INTO groups (gid, name) VALUES (?, ?)", (gid, name))
        self.sql.commit()
        return gid
        

    def createPost(self, data):
        if check(data, ["content", "duration", "start", "end"]):
            try:
                c = self.sql.cursor()
                #get group of user
                gid = c.execute("SELECT gid FROM groups_users WHERE uid=?", (self.uid,)).next()[0]
                #creating post
                pid = randomId()
                c.execute("INSERT INTO posts (pid, gid, author, content, duration, start, end) VALUES (?, ?, ?, ?, ?, ?, ?)", (pid, gid, self.uid, data["content"], datetime.datetime.strptime(data["duration"], "%H:%M"), datetime.datetime.strptime(data["start"], "%H:%M"), datetime.datetime.strptime(data["end"], "%H:%M")))
                self.sql.commit()
                return self.status_ok() 
            except:
                return self.status_error("Something is wrong")
        else:
            return self.status_error("Some requred fields are not filled");

    def hateHashtag(self, data):
        return self.status_error("Yet, it is not done.");

    def likePost(self, data):
        if check(data, ["pid", "like"]):
            c = self.sql.cursor()
            c.execute("DELETE FROM users_posts_like WHERE uid=? AND pid=?", (self.uid, data["pid"]))
            c.execute("INSERT INTO users_posts_like (uid, pid, like) VALUES (?, ?, ?)", (self.uid, data["pid"], data["like"] == "like"))
            self.sql.commit()
            return self.status_ok() 
        else:
            return self.status_error("Some requred fields are not filled");

    def getAlarms(self, data):
        return self.status_error("Yet, it is not done.");

    def getPosts(self, data):
        c = self.sql.cursor()
        c2 = self.sql.cursor()
        #get group of user
        gid = c.execute("SELECT gid FROM groups_users WHERE uid=?", (self.uid,)).next()[0]
        print "gid: ", gid 
        #get all not finished posts for this group
        posts = c.execute("SELECT pid, content, duration, start, end FROM posts WHERE gid=? AND NOT finished", (gid, ))
        kpost = []
        for post in posts:
            #likes, dislikes
            post = list(post)
            post.append(c2.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND like", (post[0], )).next()[0])
            post.append(c2.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND NOT like", (post[0], )).next()[0])
            print "Post:", post
            lockarma = post[5]
            kpost.append((lockarma, post))

        kpost.sort(key=lambda kp: -kp[0]) #desc
        res_posts = []
        for kp in kpost:
            p = kp[1]
            res_posts.append(
                    {
                        "pid": p[0],
                        "content": p[1],
                        "duration": datetime.datetime.strptime(p[2],"%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                        "start": datetime.datetime.strptime(p[3],"%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                        "end": datetime.datetime.strptime(p[4],"%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                        "like": p[5],
                        "dislike": p[6],
                    }
                    )
        return {"status":"ok", "posts": res_posts}

    def setReleaseTime(self, data):
        return self.status_error("Yet, it is not done.");

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
