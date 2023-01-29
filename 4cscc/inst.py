import urequests

from util import load_config


def get_inst_request_url(access_key=None, bucket_key=None):
    if None in (access_key, bucket_key):
        inst_config = load_config('inst')
    if access_key is None:
        access_key = inst_config['access-key']
    if bucket_key is None:
        bucket_key = inst_config['bucket-key']
    
    return ''.join([f'https://groker.init.st/api/events?',
                    f'accessKey={access_key}&',
                    f'bucketKey={bucket_key}'])


def dict_to_payload(d, host_id=None):
    if host_id is None:
        host_id = load_config('host-id')
    result = []
    for k,v in d.items():
        result.append(f'{host_id}-{k}={v}')
    return '&'.join(result)


def request_inst_url(payload, access_key=None, bucket_key=None):
    inst_base_url = get_inst_request_url(access_key, bucket_key)
    url = f'{inst_base_url}&{payload}'
    
    try:
        response = urequests.get(url)
    except (OSError, ValueError, TypeError) as e:
        print(f'Failed to request url: {url}')
        print('Caught and ignored the following '
              'error while requesting URL:\n '
              f'{e.__class__.__name__}: {str(e)}')
        if 'response' in locals():
            print('Debug note: response variable existed.')
            response.close()
    else:
        if 200 <= int(response.status_code) < 300:
            print(f'Request successful. Sent:\n {payload}')
        else:
            print(f'Request status code:\n {response.status_code}')
            print(f'Request content:\n {response.content}')
        response.close()
