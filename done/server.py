import logging
import platform
import sys
import requests

from datetime import timedelta
import requests_cache

__VERSION__ = '0.2.3'

#requests_cache.install_cache(expire_after=timedelta(hours=1))
        
def version():
    return __VERSION__

def get_manubot_user_agent():
    """
    Return a User-Agent string for web request headers to help services
    identify requests as coming from Manubot.
    """
    contact_email = 'contact@manubot.org'
    return (
        f'manubot/{version()} '
        f'({platform.system()}; Python/{sys.version_info.major}.{sys.version_info.minor}) '
        f'<{contact_email}>')



def server_response(url: str, header={}, user_agent=get_manubot_user_agent()):
    """Generic function to call servers."""
    if user_agent:
        header['User-Agent'] = get_manubot_user_agent()
    return requests.get(url, headers=header)





#def 
#
#    try:
#        return response.json()
#    except Exception as error: #FIXME: intercept specific errors
#        logging.error(['Invalid response', response.url, response.text])
#        raise error
#        
#        
#
#
#def server_response(url: str, header={}, user_agent=get_manubot_user_agent()):
#    """Generic function to call servers."""
#    if user_agent:
#        header['User-Agent'] = get_manubot_user_agent()
#    response = requests.get(url, headers=header)
#    try:
#        return response.json()
#    except Exception as error: #FIXME: intercept specific errors
#        logging.error(['Invalid response', response.url, response.text])
#        raise error