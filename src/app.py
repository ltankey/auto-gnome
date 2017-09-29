from flask import Flask
app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return "OK", 200
    elif request.method == 'POST':
        print request.headers.get('X-GitHub-Event')
        # ensure the callback is coming from github
        if request.headers.get('X-GitHub-Event') == "ping":
            return json.dumps({'msg': 'Hi!'})

        payload=json.loads(request.data)
        #print payload
        return json.dumps({'msg': 'thanks for that'})
        #if request.headers.get('X-GitHub-Event') != "push":
        #    return json.dumps({'msg': "wrong event type"})
    else:
        return "not a supported method", 400
if __name__ == '__main__':
    app.run()
