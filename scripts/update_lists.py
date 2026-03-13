import os
import socket
import ipaddress
import requests
import base64

GITHUB_TOKEN = os.environ['GITHUB_TOKEN']
HEADERS = {'Authorization': f'token {GITHUB_TOKEN}'}

GH_OWNER = 'pf-test-20260312'
GH_REPO = 'hello_world'
GH_BRANCH = 'main'

NORD_GENERIC_URL = 'https://api.github.com/repos/ip-address-list/nordvpn/contents/generic'
PIA_REGIONS_URL = 'https://api.github.com/repos/Lars-/PIA-Servers/contents/regions'
PROTON_URL = 'https://raw.githubusercontent.com/X4BNet/lists_vpn/main/input/vpn/ips/protonvpn.txt'
TOR_URL = 'https://raw.githubusercontent.com/X4BNet/lists_torexit/main/ipv4.txt'


def write_file(path, content, message):
  sha = get_file_sha(path)
  url = f'https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}'
  payload = {
    'message': message,
    'content': base64.b64encode(content.encode()).decode(),
    'branch': GH_BRANCH
  }
  if sha:
    payload['sha'] = sha
  resp = requests.put(url, headers=HEADERS, json=payload)
  resp.raise_for_status()
  print(f'Wrote: {path}')

def get_proton_ips():
    resp = requests.get(PROTON_URL).text.splitlines()
    ips = [
        str(ip)
        for net in resp
        if net
        for ip in ipaddress.ip_network(net)
    ]
  return ips


write_file(
  'proton.txt',
  '\n'.join(get_proton_ips()) + '\n',
  'Test update: proton.txt'
)
