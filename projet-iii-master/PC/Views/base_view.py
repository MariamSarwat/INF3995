"""
This class regroups common functions used by all views.
"""
from PyQt5.QtWidgets import QToolBar, QMessageBox, QMainWindow, QLabel, \
QPushButton, QDialogButtonBox, QDesktopWidget
from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import QSize, Qt

class BaseView(QMainWindow):

    def __init__(self):
        super().__init__()

    def get_window_position(self):
        """Return window position."""
        return self.pos()

    def screen_center_coordinates(self):
        """Find screen center and place window."""
        self.setFixedSize(1000, 500)
        window = self.frameGeometry()
        centerPoint = QDesktopWidget().availableGeometry().center()
        window.moveCenter(centerPoint)
        return window.topLeft()

    def set_window_parameters(self, windowPos, windowTitle):
        """Set base window parameters."""
        self.setWindowIcon(QIcon('Views/animation/jp_bixi.png'))
        self.setWindowTitle(windowTitle)
        self.setFixedSize(1000, 500)
        self.move(windowPos)

    def create_menu(self):
        """Create menu includes exit application option."""
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def create_tool_bar(self):
        """Create tool bar include back (to homepage) button."""
        self.tools = QToolBar()
        self.addToolBar(self.tools)
        self.tools.addAction('&Retour vers la page d\'accueil', self.handle_back)

    def handle_back(self):
        """Emit signal to switch back to home page."""
        pass

    def set_page_layout(self):
        """Set base window layout."""
        self.create_menu()
        self.create_tool_bar()

    def create_thread(self, worker, threadName, tabLayoutFunction, getDataFunction):
        """Create and start thread."""
        worker.moveToThread(threadName)
        threadName.finished.connect(worker.deleteLater)
        worker.dataReady.connect(tabLayoutFunction)
        threadName.started.connect(getDataFunction)
        threadName.start()

    def terminate_thread(self, enginName):
        """Terminate threads and delete thread instances."""
        if enginName.isRunning():
            enginName.quit()
            enginName.wait()
        del enginName

    def add_bixi_logo_to_window(self, imageSize, imagePosition):
        """Add logo to the home page UI."""
        label = QLabel(self)
        pixmap = QPixmap('Views/animation/bixi_logo.png').scaled(imageSize)
        label.setPixmap(pixmap)
        label.move(imagePosition)
        label.resize(pixmap.width(), pixmap.height())

    def create_toggle_button(self, widgetPosition):
        """Create button to toggle if passwords is visible or not."""
        self.visibleIcon = QIcon("Views/animation/eye_shown.png")
        self.hiddenIcon = QIcon("Views/animation/eye_hidden.png")

        self.togglePasswordButton = QPushButton(self)
        self.togglePasswordButton.clicked.connect(self.on_toggle_password_action)
        self.togglePasswordButton.setIcon(self.visibleIcon)
        self.togglePasswordButton.setIconSize(QSize(40, 40))
        self.togglePasswordButton.move(widgetPosition)
        self.togglePasswordButton.resize(50, 32)
        self.passwordShown = False

    def on_toggle_password_action(self):
        """Toggle echo mode of password fields and sets corresponding icon 
        on toggle button.
        """
        self.set_echo_mode_toggle_password_action(self.passwordShown)
        nextIcon = self.visibleIcon if self.passwordShown else self.hiddenIcon
        self.togglePasswordButton.setIcon(nextIcon)
        self.passwordShown = not self.passwordShown

    def convert_image_to_label(self, binaryImg):
        """Convert binary representation of an image into a QLabel."""
        imageLabel = QLabel()
        pixmap = QPixmap()
        pixmap.loadFromData(binaryImg)
        imageLabel.setPixmap(pixmap.scaled(QSize(540, 380)))
        imageLabel.resize(pixmap.width(), pixmap.height())
        return imageLabel

    def reset_last_byte(self):
        """Resets les last_byte for log messages."""
        import Controllers.auth as auth
        auth.last_byte = [0, 0, 0]

    def set_echo_mode_toggle_password_action(self, passwordShown):
        """Set echno mode on corresponding QLineEdits when password is toggled."""
        pass

    def create_button_box(self, buttonBoxPos, acceptedFunction, rejectedFunction):
        """Create dialog box englobing ok and cancel buttons."""
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)
        self.buttonBox.resize(150, 32)
        self.buttonBox.move(buttonBoxPos)

        self.buttonBox.accepted.connect(acceptedFunction)
        self.buttonBox.rejected.connect(rejectedFunction)

    def keyPressEvent(self, event):
        """Call handle_login when Enter key is pressed."""
        if event.key() == Qt.Key_Return:
            self.handle_enter_event()

    def handle_enter_event(self):
        """Execute when enter event is emitted."""
        pass

    def warning_window(self, message):
        """Create warning message box with specified message."""
        QMessageBox.warning(self, 'Error', message)

    def information_window(self, message):
        """Create information message box with specified message."""
        QMessageBox.information(self, 'Succès', message)

    def error_window(self, message):
        """Create error message box with specified message."""
        QMessageBox.critical(self, 'Error', message, QMessageBox.Close)
    
    def send_to_home_page_handle_error_message(self, errorMessage):
        """Send user to home page when handling a certain server error."""
        self.error_window(errorMessage.value)
        self.handle_back()
    
    def send_to_login_handle_error_message(self, controller, errorMessage):
        """Send user back to the login page when handling a certain server error."""
        self.error_window(errorMessage.value)
        controller.show_login_page(self.get_window_position())
        self.close()
        
    def handle_error_message(self, controller, errorMessage):
        """Handle error response according to type."""
        from Common.error_messages import ErrorMessages
        if errorMessage in (ErrorMessages.USER_NOT_AUTHENTICATED, \
                              ErrorMessages.CONNECTION_ERROR_SERVER):
            self.send_to_login_handle_error_message(controller, errorMessage)

        else:
            self.send_to_home_page_handle_error_message(errorMessage)
