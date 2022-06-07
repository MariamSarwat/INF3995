"""
This class sets the change password window and calls corresponding 
controller methods.
"""
from PyQt5.QtWidgets import QLabel, QLineEdit
from PyQt5.QtCore import QPoint

from Views.base_view import BaseView
from Controllers.change_password_controller import ChangePasswordController 

class ChangePasswordWindow(BaseView):
    controller = ChangePasswordController()
    
    def __init__(self, windowPos):
        super().__init__()
        
        """Set basic window parameters."""
        super().set_window_parameters(windowPos,\
        "Page changement du mot de passe du compte Admin")
        self.set_page_layout()
        
        """Create page layout."""
        self.create_new_password_line_edit()
        self.create_confirm_new_password_line_edit()
        self.create_button_box(QPoint(600, 284), self.handle_save, self.handle_back)              
        self.create_toggle_button(QPoint(775, 219))
        self.controller.processingFinished.connect(self.handle_server_response)
        
    def create_confirm_new_password_line_edit(self):
        """Create line edit for confirm new password."""
        self.confirmNewPassLabel = QLabel(self)
        self.confirmNewPassLabel.setText('Confirmer nouveau mot de passe :')
        self.confirmNewPassLine = QLineEdit(self)

        self.confirmNewPassLine.move(450, 244)
        self.confirmNewPassLine.resize(300, 32)
        self.confirmNewPassLabel.move(150, 244)
        self.confirmNewPassLabel.resize(300, 32)
        self.confirmNewPassLine.setEchoMode(QLineEdit.Password)
        
    def create_new_password_line_edit(self):
        """Create line edit for new password entry."""
        self.newPassLabel = QLabel(self)
        self.newPassLabel.setText('Nouveau mot de passe :')
        self.newPassLine = QLineEdit(self)
        
        self.newPassLine.move(450, 194)
        self.newPassLine.resize(300, 32)
        self.newPassLabel.move(150, 194)
        self.newPassLabel.resize(300, 32)
        self.newPassLine.setEchoMode(QLineEdit.Password)
    
    def handle_save(self):
        """Handle save of a new password for account. 
        If both inputs are equivalent, new password is set.
        """
        if self.valid_password_entry():
            self.controller.set_new_password(self.newPassLine.text())
        else: 
            self.warning_window('Les mots de passe entrés ne sont pas équivalents ou ils sont vides.')
  
    def handle_server_response(self, finishedSuccesfully, errorMessage):
        """Handle accordingly the response returned by the server."""
        from Common.error_messages import ErrorMessages
        if finishedSuccesfully:
            self.information_window('Le mot de passe a été changé avec succès!')
            self.handle_back()
        else:
            self.handle_error_message(self.controller, errorMessage)
             
    def valid_password_entry(self):
        """Validate passwords entered. 
        Passwords cannot be empty string and have to be equivalent.
        """
        passwordsEqual = (self.newPassLine.text() == self.confirmNewPassLine.text())
        passwordsNotEmptyString = (self.newPassLine.text() != '') and (self.confirmNewPassLine.text() != '')
        return (passwordsEqual and passwordsNotEmptyString) 
        
    def handle_back(self):
    	"""Emit signal to switch back to home page."""
    	self.controller.show_home_page(self.get_window_position())
    	self.close()
   
    def set_echo_mode_toggle_password_action(self, password_shown=False):
        """Set echo mode on password toggle."""   
        lineEditView = QLineEdit.Password if password_shown else QLineEdit.Normal
        self.newPassLine.setEchoMode(lineEditView)
        self.confirmNewPassLine.setEchoMode(lineEditView)
    
    def handle_enter_event(self):
        """Execute when enter event is emitted."""
        self.handle_save()
