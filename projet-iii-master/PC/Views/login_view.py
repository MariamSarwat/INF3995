"""
This class sets the login window and calls corresponding controller methods.
"""
from PyQt5.QtWidgets import QLabel, QLineEdit
from PyQt5.QtGui import QRegExpValidator
from PyQt5.QtCore import QSize, QPoint, QRegExp

from requests.exceptions import ConnectionError
from Views.base_view import BaseView
from Controllers.login_controller import LoginController

class LoginWindow(BaseView): 
    
    controller = LoginController()
    
    def __init__(self, windowPos=QPoint(0, 0)): 
        super().__init__() 
        
        """Set basic window parameters."""
        if windowPos == QPoint(0, 0):
            windowPos = self.screen_center_coordinates()
        super().set_window_parameters(windowPos, "Outil administratif pour le système BIXI") 
        
        """Create UI."""
        self.create_login_line_edits()   
        self.create_ip_address_line_edit()
        self.create_button_box(QPoint(550, 344), self.handle_login, self.close)
        self.create_toggle_button(QPoint(700, 244))
        self.add_bixi_logo_to_window(QSize(200, 100), QPoint(400, 50))
        
    def handle_login(self): 
        """Handle login, if valid password go to homepage, 
        else throw warning.
        """
        from Common.error_messages import ErrorMessages
        try: 
            (loginValid, errorMessage) = self.is_login_valid()
            if loginValid:
                self.controller.show_home_page(self.get_window_position())
                self.close()
            else:
                if errorMessage == ErrorMessages.CONNECTION_ERROR_SERVER:
                    self.error_window(errorMessage.value)
                else:
                    self.warning_window('Le mot de passe entré est incorrect')            
        except ConnectionError:
            self.error_window('Erreur de connexion avec le serveur')
    
    def is_login_valid(self):
        """Verify password entered by user."""
        return self.controller.validate_login(self.passwordLine.text(), self.ipAdrLine.text())      
    
    def create_login_line_edits(self): 
        """Create login inputs (username and password fields)."""
        """Set username field."""
        self.usernameLabel = QLabel(self)
        self.usernameLabel.setText('Nom d\'utilisateur :')
        self.usernameLine = QLineEdit(self) 
        
        self.usernameLine.move(450, 194)
        self.usernameLine.resize(250, 32)
        self.usernameLabel.move(250, 194)
        self.usernameLabel.resize(150, 32)
        
        self.usernameLine.setText('Admin')
        self.usernameLine.setReadOnly(True)
        
        """Set password field."""
        self.passwordLabel = QLabel(self)
        self.passwordLabel.setText('Mot de passe :')
        self.passwordLine = QLineEdit(self) 
        
        self.passwordLine.move(450, 244)
        self.passwordLine.resize(250, 32)
        self.passwordLabel.move(250, 244)
        self.passwordLabel.resize(150, 32)

        self.passwordLine.setPlaceholderText('SVP, entrez votre mot de passe')
        self.passwordLine.setEchoMode(QLineEdit.Password)
       
    def create_ip_address_line_edit(self):
        """Create IPv4 addresse input field for the web server."""
        self.ipAdrLabel = QLabel(self)
        self.ipAdrLabel.setText('Adresse IPv4 du serveur web :')
        self.ipAdrLine = QLineEdit(self) 
        
        self.ipAdrLine.move(450, 294)
        self.ipAdrLine.resize(250, 32)
        self.ipAdrLabel.move(250, 294)
        self.ipAdrLabel.resize(150, 32)
        
        self.ipAdrLine.setValidator(self.ipv4_validator())
        self.ipAdrLine.setInputMask("000.000.000.000")
        
        """Default IPv4 server address."""
        self.ipAdrLine.setText('172.105.99.131')

    def ipv4_validator(self):
        """Validate Ipv4 address specified."""
        ipRange = "(([ 0]+)|([ 0]*[0-9] *)|([0-9][0-9] )|([ 0][0-9][0-9])|(1[0-9][0-9])|([2][0-4][0-9])|(25[0-5]))"
        
        ipRegex = QRegExp("^" + ipRange + "\\." + ipRange + "\\." + ipRange + "\\." + ipRange + "$")
        return QRegExpValidator(ipRegex)
        
    def set_echo_mode_toggle_password_action(self, password_shown=False):
        """Set echo mode for password line edit."""
        lineEditView = QLineEdit.Password if password_shown else QLineEdit.Normal
        self.passwordLine.setEchoMode(lineEditView)      
    
    def handle_enter_event(self):
        """Execute when enter event is emitted."""
        self.handle_login()
