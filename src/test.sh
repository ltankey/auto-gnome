#!/bin/bash
# change this to the endpoint you want to test
#DEV_ENDPOINT=https://4ntcp396gj.execute-api.us-east-1.amazonaws.com/dev
DEV_ENDPOINT=127.0.0.1:5000

curl -H "Content-Type: application/json" -X POST -d '{"foo":"xyz","bar":"abc", "contents_url":"https://api.github.com/repos/bugflow/gh-ticket-gnome/contents/{+path}"}' $DEV_ENDPOINT
