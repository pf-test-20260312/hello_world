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
PIA_REGIONS_URL = 'https://api.github.com/repos/Lars-/PIA-Servers/git/trees/HEAD?recursive=1'

PROTON_URL = 'https://raw.githubusercontent.com/X4BNet/lists_vpn/main/input/vpn/ips/protonvpn.txt'

TOR_URL = 'https://raw.githubusercontent.com/X4BNet/lists_torexit/main/ipv4.txt'


def get_file_sha(path):
  url = f'https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}'
  resp = requests.get(url, headers=HEADERS, params={'ref': GH_BRANCH})
  if resp.status_code == 404:
    return None
  resp.raise_for_status()
  return resp.json()['sha']

def write_file(path, content):
  sha = get_file_sha(path)
  url = f'https://api.github.com/repos/{GH_OWNER}/{GH_REPO}/contents/{path}'
  content = '\n'.join(content) + '\n'
  message = f'Test update: {path}'
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
  
def get_nord_ips():
    resp = requests.get(NORD_GENERIC_URL).json()
    region_urls = [
        f['download_url']
        for f in resp
        if f['type'] == 'file' and f['name'].endswith('.txt')
    ]

    hostnames = []
    for url in region_urls:
        resp = requests.get(url).text.splitlines()
        hostnames.extend(ln.strip() for ln in resp if ln.strip())

    ips = [
        ip
        for item in hostnames
        for ip in socket.gethostbyname_ex(item)[2]
    ]
    return ips



def get_pia_ips():
    resp = requests.get(PIA_REGIONS_URL).json()['tree']
    ips = [
        item['path'].split('/')[-1].replace('.ovpn', '').replace('-', '.')
        for item in resp
        if item['path'].startswith('regions/') and item['path'].endswith('.ovpn')
    ]
    return ips

def get_tor_ips():
    resp = requests.get(TOR_URL).text.splitlines()
    ips = [
        str(ip)
        for net in resp
        if net
        for ip in ipaddress.ip_network(net)
    ]
    return ips

files_to_update = {
  #'proton.txt': get_proton_ips(),
  #'tor.txt': get_tor_ips(),
  #'pia.txt': get_pia_ips(),
  'nord.txt': get_nord_ips()
}

for file_name, content in files_to_update.items():
    write_file(
      file_name,
      content
    )


