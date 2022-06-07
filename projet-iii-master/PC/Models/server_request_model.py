"""
This class is in charge of the communication with the server.
"""
import requests
import re

def auth(validURIs):
    
    pattern = re.compile(r'/logs/[1-3]/\d+')
    auth_authorized = False
    
    def decorate(func):
        def wrapper(self, uri, data={}):
        
            for item in validURIs:
                if (uri in item) or pattern.match(uri):
                    auth_authorized = True
                    break
            
            if auth_authorized : 
                auth = (self.user, self.passwd)
            else : 
                auth = None
                
            return func(self, uri, data, auth=auth)
        return wrapper
    return decorate

class Http(object):
    certPath = '../certs/RootCA.crt'
    
    def __init__(self, user = 'admin', passwd = ''):
        self.user = user
        self.passwd = passwd
        self.baseURL = ''
        
    @auth(['/usager/login'])
    def post(self, uri, data={}, auth=None):
        return requests.post(self.baseURL + uri, auth=auth, verify = self.certPath)

    @auth(['/usager/motdepasse'])
    def put(self, uri, data, auth=None):
        return requests.put(self.baseURL + uri, json=data, auth=auth, verify = self.certPath)

    @auth(['/sondage', '/logs/'])
    def get(self, uri, data={}, auth=None):
        """Timeout waits 5 second for a connection and 
        20 seconds to receive data.
        """
        return requests.get(self.baseURL + uri, auth=auth, verify = self.certPath, timeout=(5, 20))
        
    def set_passwd(self, hashedPasswd):
        """Set new password for authentication."""
        self.passwd = hashedPasswd
        
    def set_ip_address(self, ipAdr):
        """Set IP address for requests."""
        self.baseURL = 'https://' + ipAdr + ':443'
