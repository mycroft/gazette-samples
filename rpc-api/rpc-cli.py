#!/usr/bin/env python

import requests
from requests.auth import HTTPBasicAuth
import json
import sys

class RpcCli:
    """
        Port is 8332 for mainnet, 18332 for testnet
    """
    def __init__(self, username, password, hostname='localhost', port=8332):
        self.username = username
        self.password = password
        self.hostname = hostname
        self.port = port

    def run(self, method='help', params=[]):
        url = "http://%s:%d" % (self.hostname, self.port)
        auth = HTTPBasicAuth(self.username, self.password)
        headers = {'content-type': 'application/json'}

        payload = {
            "method": method,
            "params": params,
            "jsonrpc": "1.0",
            "id": "curltext",
        }

        response = requests.post(
            url, data=json.dumps(payload), headers=headers, auth=auth)

        if response.status_code != 200:
           print(response.reason)
           return None

        result = response.json()['result']
        return self.prettyfy(result)

    def prettyfy(self, content):
        return json.dumps(content, indent=4, sort_keys=True)

    def value(self, content):
        return json.loads(content)

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: %s <command> [param1] [param2] ..." % (sys.argv[0]))
        print("Help: %s help" % (sys.argv[0]))
        sys.exit(0)

    use_json = False
    idx = 1

    cli = RpcCli("rpc", "1yC70vJ8-NPQ9LwFgNMf0VRxiKWavTwVLIPUetZ2kBQ=", port=18332)

    while len(sys.argv) > idx and sys.argv[idx][0] == '-':
        flag = sys.argv[idx][1:].lower()
        if flag == "json":
            use_json = True
        else:
            print("Unknown flag: %s" % flag)
            sys.exit(1)

        idx += 1

    resp = cli.run(sys.argv[idx], sys.argv[idx+1:])

    if use_json:
        print(resp)
    else:
        print(cli.value(resp))

