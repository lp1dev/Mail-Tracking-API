#!/usr/bin/python3
from flask import Flask, request, send_file, jsonify
from time import time
from hashlib import md5
from base64 import b64encode, b64decode
import json

host="lp1.eu"
port=6666
debug=True
encoding="UTF-8"
output_file="data.json"
log_file = "tracker.log"
image_file = "signature.png"

mailApi = Flask(__name__)

def log(entry):
    with open(log_file, "a+") as f:
        string = "%s-- %s-- %s-- %s\n" %(entry['host'], entry['opened'], entry['data'], entry['UA'])
        f.write(string)

def get_data():
    try:
        with open(output_file, "r") as f:
            try:
                raw = f.read()
                f.close()
                return json.loads(raw)
            except ValueError as e:
                if debug:
                    print(e)
                return []
    except FileNotFoundError as e:
        return []

def generate_token(data):
    now = time()
    entry = {"created": str(now), "data":data}
    id = add_entry(entry)
    return b64encode(str(id).encode(encoding))

def add_entry(entry):
    data = get_data()
    entry['id'] = len(data)
    data.append(entry)
    write_data(data)
    return entry['id']

def write_data(data):
    with open(output_file, "w") as f:
        f.write(json.dumps(data))

@mailApi.route("/token/<data>")
def get_token(data):
    return generate_token(data)

@mailApi.route("/image/<id>")
def get_image(id):
    try:
        id = id.split(".")[0]
        id = int(b64decode(id).decode(encoding))
        entries = get_data()
        if id < len(entries):
            entries[id]['opened'] = str(time())
            entries[id]['UA'] = request.headers['User-Agent']
            entries[id]['host'] = request.remote_addr
            log(entries[id])
        write_data(entries)
    except ValueError as e:
        if debug:
            print(e)
    return send_file(image_file, mimetype="image/png")

def main():
    mailApi.run(host=host, port=port, threaded=True, debug=debug)
    return 0

if __name__ == "__main__":
    main()
