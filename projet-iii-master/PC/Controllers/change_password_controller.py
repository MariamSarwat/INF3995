from PyQt5.QtCore import pyqtSignal, QObject

from Common.error_messages import ErrorMessages
from Common.request_status_code import StatusCodes
from Controllers.base_controller import BaseController
import Controllers.auth as auth

class ChangePasswordController(BaseController, QObject):

    processingFinished = pyqtSignal(bool, ErrorMessages)
    
    def __init__(self):
        super().__init__()

    def set_new_password(self, newPassword):
        """Set new password and return status code of request."""
        hashedPassword = self.encrypt_password(newPassword)
        response = auth.global_http.put(uri='/usager/motdepasse', data={'nouveau': hashedPassword})
        self.treat_response(response, hashedPassword)
    
    def treat_response(self, response, hashedPassword):
        """Treat returned response from server, if invalid return empty list with a corresponding error message."""
        if response.status_code == StatusCodes.OK.value:
            auth.global_http.set_passwd(hashedPassword)
            
        processFinishedSuccessfully = (response.status_code == StatusCodes.OK.value)
        errorMessage = self.get_error_message(response)
                   
        self.processingFinished.emit(processFinishedSuccessfully, errorMessage)
