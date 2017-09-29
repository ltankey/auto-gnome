from flask import Flask, request
from github import Github
import json
import ipaddress
import requests
import sys

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        #gh = Github()
        #print(gh, file=sys.stdout)
        return "OK", 200

    elif request.method == 'POST':
        print(request.headers.get('X-GitHub-Event'), file=sys.stdout)

        # ensure the callback is coming from github
        request_ip = ipaddress.ip_address(u'{0}'.format(request.remote_addr))
        if os.environ.get('GHE_ADDRESS', None):
            hook_blocks = [unicode(os.environ.get('GHE_ADDRESS'))]
        else:
            hook_blocks = requests.get('https://api.github.com/meta').json()[
                'hooks']
        for block in hook_blocks:
            if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
                break  # the remote_addr is within the network range of github.
        else:
            if str(request_ip) != '127.0.0.1':
                abort(403)
                
        # process the callback...
        if request.headers.get('X-GitHub-Event') == "ping":
            return json.dumps({'msg': 'Hi!'})

        payload=json.loads(request.data)
        #print payload
        #
        # if request.headers.get('X-GitHub-Event') != "push":
        #    return json.dumps({'msg': "wrong event type"})
        # no password ATM, only work with public repos
        # TODO: pull credentials from the environment
        gh = Github()
        print(gh, file=sys.stdout)
        return json.dumps({'msg': 'thanks for that'}), 200
    else:
        return "not a supported method", 400

if __name__ == '__main__':
    app.run()
