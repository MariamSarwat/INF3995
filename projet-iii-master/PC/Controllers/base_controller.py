import hashlib

class BaseController:
    def __init__(self):
        super().__init__()

    def show_home_page(self, windowPos):
        """Show home page window."""
        from Views.home_page_view import HomePageWindow
        self.homePageWindow = HomePageWindow(windowPos)
        self.homePageWindow.show()
        
    def show_log_message_page(self, windowPos):
        """Show log message page window."""
        from Views.log_message_view import LogMessageWindow
        self.logMessageWindow = LogMessageWindow(windowPos)
        self.logMessageWindow.show()
        
    def show_change_password_page(self, windowPos):
        """Show change admin password page window."""
        from Views.change_password_view import ChangePasswordWindow
        self.changePasswordWindow = ChangePasswordWindow(windowPos)
        self.changePasswordWindow.show()
        
    def show_poll_results_page(self, windowPos):
        """Show poll results page window."""
        from Views.poll_results_view import PollResultsWindow
        self.pollResultsWindow = PollResultsWindow(windowPos)
        self.pollResultsWindow.show()
    
    def show_login_page(self, windowPos):
        """Show poll results page window."""
        from Views.login_view import LoginWindow
        self.reset_auth()
        self.loginWindow = LoginWindow(windowPos)
        self.loginWindow.show()
    
    def reset_auth(self):
        """Reset Authentication variables."""
        import Controllers.auth as auth
        from Models.server_request_model import Http
        auth.global_http = Http()
        auth.last_byte = [0, 0, 0]
        
    def get_error_message(self, response):
        """Return error message corresponding to response status code."""
        from Common.request_status_code import StatusCodes
        from Common.error_messages import ErrorMessages
        if response.status_code == StatusCodes.OK.value:
            return ErrorMessages.NONE
            
        elif response.status_code == StatusCodes.NO_CONTENT_TO_RETURN.value:
            return ErrorMessages.NONE
                
        elif response.status_code == StatusCodes.BAD_REQUEST.value: 
            return ErrorMessages.BAD_REQUEST
            
        elif response.status_code == StatusCodes.USER_NOT_AUTHENTICATED.value:
            return ErrorMessages.USER_NOT_AUTHENTICATED
        
        elif response.status_code == StatusCodes.CONNECTION_ERROR.value:
            return ErrorMessages.CONNECTION_ERROR_SERVER
            
        else:
            return ErrorMessages.OTHER
                
    def encrypt_password(self, hashString):
        """Encrypt password with SHA256."""
        shaSignature = hashlib.sha256(hashString.encode()).hexdigest()
        return shaSignature

