import os
import requests
import ipaddress

# FIXME: use a cache

def gh_event_source_is_valid(ip_str):
    request_ip = ipaddress.ip_address(u'{0}'.format(ip_str))
    # TODO: consider only doing this id DEBUG==True ???
    if str(request_ip) == '127.0.0.1':
        return True
    
    # TODO: cache the hook_blocks
    hook_blocks = requests.get('https://api.github.com/meta').json()['hooks']
    for block in hook_blocks:
        if ipaddress.ip_address(request_ip) in ipaddress.ip_network(block):
            return True
    return False


if __name__ == "__main__":
    print("TODO: make tests suite")

            
