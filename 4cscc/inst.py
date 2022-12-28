import urequests
from util import load_config

def dict_to_payload(d, host_id=None):
    if host_id is None:
        host_id = load_config('host-id')
    result = []
    for k,v in d.items():
        result.append(f'{host_id}-{k}={v}')
    return '&'.join(result)

def request_inst_url(payload, inst_base_url=None):
    if inst_base_url is None:
        inst_config = load_config('inst')
        inst_base_url = inst_config['base-url']
    url = f'{inst_base_url}&{payload}'
    
    try:
        request = urequests.get(url)
    except OSError:
        print(f'Failed to request url: {url}')
    else:
        if 200 <= int(request.status_code) < 300:
            print(f'Request successful. Sent:\n {payload}')
        else:
            print(f'Request status code:\n {request.status_code}')
            print(f'Request content:\n {request.content}')
        request.close()