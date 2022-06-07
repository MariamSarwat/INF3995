"""
This class verifies if login is valid.
"""
import Controllers.auth as auth
from Controllers.base_controller import BaseController
from Common.request_status_code import StatusCodes

class LoginController(BaseController):
    def __init__(self):
        super().__init__()
        
    def validate_login(self, password, ipAdr):
        """Validate entered password."""
        self.set_auth_parameters(password, ipAdr)
        
        response = auth.global_http.post(uri='/usager/login')
        loginValid = (response.status_code == StatusCodes.OK.value)
        errorMessage = self.get_error_message(response)
        
        return (loginValid, errorMessage)   
    
    def set_auth_parameters(self, password, ipAdr):
        """Set Authentication parameters."""
        auth.global_http.set_ip_address(ipAdr) 
        hashedPassword = self.encrypt_password(password)
        auth.global_http.set_passwd(hashedPassword)
