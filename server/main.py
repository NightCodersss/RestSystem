import sqlite3
import datetime
import time
import json
import BaseHTTPServer


HOST_NAME = 'localhost' # !!!REMEMBER TO CHANGE THIS!!!
PORT_NUMBER = 443

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
        if a == "set_release_time":
            return self.setReleaseTime(data)

        return self.status_error("Action is not found")

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
        if check(data, ["content", "theme", "duration", "start", "end"]):
            #try:
            if True:
                c = self.sql.cursor()
                #get group of user
                gid = c.execute("SELECT gid FROM groups_users WHERE uid=?", (self.uid,)).next()[0]
                #creating post
                pid = randomId()
                c.execute("INSERT INTO posts (pid, gid, author, theme, content, duration, start, end) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (pid, gid, self.uid, data["theme"], data["content"], datetime.datetime.strptime(data["duration"], "%H:%M"), datetime.datetime.strptime(data["start"], "%H:%M"), datetime.datetime.strptime(data["end"], "%H:%M")))
                self.sql.commit()
                self.recalcAlarms()
                return self.status_ok() 
            #except:
            #    return self.status_error("Something is wrong")
        else:
            return self.status_error("Some requred fields are not filled");

    def recalcAlarms(self):
        c = self.sql.cursor()
        #get group of user
        gid = c.execute("SELECT gid FROM groups_users WHERE uid=?", (self.uid,)).next()[0]
        
        c.execute("DELETE FROM alarms WHERE gid=?", (gid,))
        events = []
        rnd = []
        for (pid, start, end, duration) in c.execute("SELECT pid, start, end, duration FROM posts WHERE gid=? AND NOT finished", (gid,)):
            st = datetime.datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
            et = datetime.datetime.strptime(end,"%Y-%m-%d %H:%M:%S")
            dt = datetime.datetime.strptime(end,"%Y-%m-%d %H:%M:%S")
            sts = time.mktime(st.timetuple())
            ets = time.mktime(et.timetuple())
            dts = time.mktime(dt.timetuple())
            import random
            t = datetime.datetime.fromtimestamp(random.uniform(sts, ets))
            events.append((pid, t, dts, self.getKarma(gid, pid, t)+1))
            for _ in range(events[-1][3]):
                rnd.append((pid, t,))

        print "Events: ", events

        chosen_events = []
        sumt = 0;
        while sumt < 60*60*1 and rnd != []:
            event = random.choice(rnd)
            chosen_events.append((event[1], event[0], gid)); #time, pid, gid
            sumt += time.mktime(event[1].timetuple())
            nrnd = []
            for r in rnd:
                if r[0] != event[0]:
                    nrnd.append(r)
            rnd = nrnd
        print "Chosen events:", chosen_events
        c.executemany("INSERT INTO alarms (time, pid, gid) VALUES (?, ?, ?)", chosen_events)
        self.sql.commit()


    def hateHashtag(self, data):
        return self.status_error("Yet, it is not done.");

    def likePost(self, data):
        if check(data, ["pid", "like"]):
            c = self.sql.cursor()
            c.execute("DELETE FROM users_posts_like WHERE uid=? AND pid=?", (self.uid, data["pid"]))
            c.execute("INSERT INTO users_posts_like (uid, pid, like) VALUES (?, ?, ?)", (self.uid, data["pid"], data["like"] == "like"))
            self.sql.commit()
            self.recalcAlarms()
            return self.status_ok() 
        else:
            return self.status_error("Some requred fields are not filled");

    def getAlarms(self, data):
        c = self.sql.cursor()
        c2 = self.sql.cursor()
        #get group of user
        gid = c.execute("SELECT gid FROM groups_users WHERE uid=?", (self.uid,)).next()[0]
        res_posts = []
        print "GID:", gid

        for (time, pid) in c.execute("SELECT time, pid FROM alarms WHERE gid=? OR date((SELECT AVG(finished) FROM posts WHERE pid=alarms.pid))==1", (gid, )):
            post = c2.execute("SELECT pid, content, duration, start, end FROM posts WHERE pid=?", (pid, )).next()
            print "Post:", post

            #likes, dislikes
            post = list(post)
            post.append(c2.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND like", (post[0], )).next()[0])
            post.append(c2.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND NOT like", (post[0], )).next()[0])
            
            p = post

            res_posts.append(
                    {
                        "pid": p[0],
                        "content": p[1],
                        "duration": datetime.datetime.strptime(p[2],"%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                        "start": datetime.datetime.strptime(p[3],"%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                        "end": datetime.datetime.strptime(p[4],"%Y-%m-%d %H:%M:%S").strftime("%H:%M"),
                        "like": p[5],
                        "dislike": p[6],
                        "time": time,
                    }
                    )
        return {"status":"ok", "posts": res_posts}
        
    def getKarma(self, gid, pid, t):
        c = self.sql.cursor()
        c2 = self.sql.cursor()
        k = 0
        for (uid,) in c.execute("SELECT uid FROM groups_users WHERE gid = ?", (gid,)):
            (rt, start, end) = c2.execute("SELECT release_time, start_of_day, end_of_day FROM users WHERE uid=?", (uid,)).next();
            #rt = datetime.datetime.strptime(rt, "%Y-%m-%d %H:%M:%S")
            #start = datetime.datetime.strptime(start, "%Y-%m-%d %H:%M:%S")
            #end = datetime.datetime.strptime(end, "%Y-%m-%d %H:%M:%S")
            if rt <= t and start.time() <= t.time() and t.time() <= end.time():
                k += getLocalKarma(uid, pid)
        return k

    def getLocalKarma(self, uid, pid):
        c = self.sql.cursor()
        return c.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND uid=? AND like", (pid, uid )).next()[0]
        

    def getPosts(self, data):
        c = self.sql.cursor()
        c2 = self.sql.cursor()
        #get group of user
        gid = c.execute("SELECT gid FROM groups_users WHERE uid=?", (self.uid,)).next()[0]
        print "gid: ", gid 
        #get all not finished posts for this group
        posts = c.execute("SELECT pid, content, duration, start, end, theme FROM posts WHERE gid=? AND NOT finished", (gid, ))
        kpost = []
        for post in posts:
            #likes, dislikes
            post = list(post)
            likes = c2.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND like", (post[0], )).next()[0]
            dislikes = c2.execute("SELECT COUNT(*) FROM users_posts_like WHERE pid=? AND NOT like", (post[0], )).next()[0]
            post.append(likes)
            post.append(dislikes)
            print "Post:", post
            lockarma = likes
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
                        "like": p[6],
                        "dislike": p[7],
                        "theme": p[5],
                    }
                    )
        return {"status":"ok", "posts": res_posts}

    def setReleaseTime(self, data):
        c = self.sql.cursor()
        c.execute("UPDATE users SET release_time = datetime('now','+240 minutes') WHERE uid=?", (self.uid, ))
        self.sql.commit()
        self.recalcAlarms()
        return self.status_ok()

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

def DoAllIwant(poststr):
    data = json.loads(poststr);
    res = (RestSystem()).getResponse(data)
    return json.dumps(res)
