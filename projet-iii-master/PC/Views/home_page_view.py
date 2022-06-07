"""
This class sets the home page window and calls corresponding controller methods.
"""
from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QSize, QPoint

from Views.base_view import BaseView
from Controllers.home_page_controller import HomePageController 

class HomePageWindow(BaseView):
    
    controller = HomePageController()
    
    def __init__(self, windowPos):
        super().__init__()
        
        """Set basic window parameters."""
        super().set_window_parameters(windowPos,\
        "Outil administratif pour le système BIXI - Page D\'accueil")
        
        """Create buttons (UI)."""
        self.create_change_password_button()
        self.create_poll_results_button()
        self.create_log_message_button()
        self.add_bixi_logo_to_window(QSize(400, 200), QPoint(75, 150))
        self.create_menu()
        
    def create_change_password_button(self):
        """Create change admin password button (send to change password page)."""
        changePasswordButton = QPushButton('Changer le mot de passe du compte', self)
        changePasswordButton.resize(300, 40)
        changePasswordButton.move(550, 160)
        changePasswordButton.clicked.connect(self.handle_change_password)
        
    def create_poll_results_button(self):
        """Create consult poll results button (send to poll results page)."""
        pollResultsButton = QPushButton('Consulter les résultats du sondage', self)
        pollResultsButton.resize(300, 40)
        pollResultsButton.move(550, 230)
        pollResultsButton.clicked.connect(self.handle_poll_results)
        
    def create_log_message_button(self):
        """Create get log messages button (send to consult log messages page)."""
        logMessagesButton = QPushButton('Afficher les messages log des engins', self)
        logMessagesButton.resize(300, 40)
        logMessagesButton.move(550, 300)
        logMessagesButton.clicked.connect(self.handle_log_messages)
        
    def handle_change_password(self):
        """Emit signal to switch to change password page."""
        self.controller.show_change_password_page(self.get_window_position())
        self.close()
    	
    def handle_poll_results(self):
        """Emit signal to switch to poll results page."""
        self.controller.show_poll_results_page(self.get_window_position())
        self.close()
     
    def handle_log_messages(self):
        """Emit signal to switch to log messages page."""
        self.controller.show_log_message_page(self.get_window_position())
        self.close()
        
