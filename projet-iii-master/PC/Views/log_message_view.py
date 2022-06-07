"""
This class sets the log message window and calls corresponding 
controller methods.
"""
from PyQt5.QtWidgets import QTabWidget, QWidget, QFormLayout, QScrollArea,\
QLabel, QStackedWidget
from PyQt5.QtCore import QThread, Qt
from PyQt5.QtGui import QMovie

from Views.base_view import BaseView
from Controllers.log_message_controller import LogMessageController
from Controllers.repeated_timer import RepeatedTimer

class LogMessageWindow(BaseView):
    
    controller = LogMessageController()
    
    def __init__(self, windowPos):
        super().__init__()
        
        """Set basic window parameters."""
        self.create_UI(windowPos)
        self.initialDataReceived = [False, False, False]
        self.connectionErrorInEngin = [False, False, False]
        self.userNotAuthErrorThrown = False
        self.unknownErrorThrown = False
        
        """Initialise working threads and set timer."""
        self.init_working_thread()  
        self.set_loading_status() 
    
    def create_UI(self, windowPos):
        """Create log message window ui."""
        super().set_window_parameters(windowPos,\
        "Page d'affichage des messages log des engins de données")
        self.create_data_engin_tabs()
        self.set_page_layout()
        self.load = QLabel()
        self.set_central_widget_stack()
        
    def load_intial_log_messages(self, index):
        """Once initial log messages are retrieved, remove loading gif, 
        show logs and start timer.
        """ 
        self.initialDataReceived[index] = True
        if self.initial_data_received():
            self.set_tabs_scroll()
            self.centralWidget.setCurrentWidget(self.tabs)
            self.timer = RepeatedTimer(3, self.start_working_thread)
    
    def set_tabs_scroll(self):
        """Set scroll parameter for all tab widgets."""
        self.set_tab_scroll_parameters(self.dataEngin1, "Engin de données #1")
        self.set_tab_scroll_parameters(self.dataEngin2, "Engin de données #2")
        self.set_tab_scroll_parameters(self.dataEngin3, "Engin de données #3")
        
    def set_loading_status(self):
        """Show loading gif while poll results are being prepared to output."""
        self.load.setAlignment(Qt.AlignCenter)
        gif = QMovie('Views/animation/loading.gif')
        self.load.setMovie(gif)
        gif.start()
        self.centralWidget.setCurrentWidget(self.load)
        self.controllerEngin1.initLogLoadFinished.connect(self.load_intial_log_messages)
        self.controllerEngin2.initLogLoadFinished.connect(self.load_intial_log_messages)
        self.controllerEngin3.initLogLoadFinished.connect(self.load_intial_log_messages)
        
    def set_central_widget_stack(self):
        """Set and add widgets to the window center."""
        self.centralWidget = QStackedWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.addWidget(self.tabs)
        self.centralWidget.addWidget(self.load) 
        
    def init_working_thread(self): 
        """Initialise and create working threads, one for each data engin."""
        self.engin1Thread = QThread()
        self.engin2Thread = QThread()
        self.engin3Thread = QThread()
        
        self.controllerEngin1 = LogMessageController(1, self.initialDataReceived[0])
        self.controllerEngin2 = LogMessageController(2, self.initialDataReceived[1])
        self.controllerEngin3 = LogMessageController(3, self.initialDataReceived[2])
        
        self.create_thread(self.controllerEngin1, self.engin1Thread, self.handle_server_response, self.controllerEngin1.get_log_messages)
        self.create_thread(self.controllerEngin2, self.engin2Thread, self.handle_server_response, self.controllerEngin2.get_log_messages)
        self.create_thread(self.controllerEngin3, self.engin3Thread, self.handle_server_response, self.controllerEngin3.get_log_messages)
        
    def start_working_thread(self):
        """Start working threads."""
        self.terminate_all_threads()
        self.init_working_thread()  
        
    def create_data_engin_tabs(self):
        """Create tab for each data engin."""
        self.tabs = QTabWidget(self)
        self.dataEngin1 = QWidget()
        self.dataEngin2 = QWidget()
        self.dataEngin3 = QWidget()
        
        """Set layout of widgets."""
        self.layoutEngin1 = QFormLayout()
        self.layoutEngin2 = QFormLayout()
        self.layoutEngin3 = QFormLayout()
        
        self.dataEngin1.setLayout(self.layoutEngin1)
        self.dataEngin2.setLayout(self.layoutEngin2)
        self.dataEngin3.setLayout(self.layoutEngin3)
        
    def handle_back(self):
    	"""Emit signal to switch back to home page."""
    	self.reset_last_byte()
    	self.controller.show_home_page(self.get_window_position())
    	self.close()
        
    def terminate_all_threads(self):
        """Terminate each engin thread safely."""
        self.terminate_thread(self.engin1Thread)
        self.terminate_thread(self.engin2Thread)
        self.terminate_thread(self.engin3Thread)
        
    def set_tab_scroll_parameters(self, dataEnginTab, enginTabName):
        """Create scroll area and set parameters.""" 
        scrollArea = QScrollArea()
        scrollArea.setWidgetResizable(True)
        scrollArea.setWidget(dataEnginTab)
        maximum = scrollArea.verticalScrollBar().maximum()
        scrollArea.verticalScrollBar().setValue(maximum)
        self.tabs.addTab(scrollArea, enginTabName)
                
    def handle_server_response(self, enginNumber, logMessages, logIsText, errorMessage):
        from Common.error_messages import ErrorMessages
        if errorMessage == ErrorMessages.NONE:
            self.connectionErrorInEngin[enginNumber - 1] = False
            tabLayout = self.get_tab_layout(enginNumber)
            self.set_tab_layout(tabLayout, logMessages, logIsText)
                    
        else:
            self.handle_engin_error_message(enginNumber, errorMessage)
        
    def handle_engin_error_message(self, enginNumber, errorMessage):
        """Handle error response according to type."""
        from Common.error_messages import ErrorMessages
        if errorMessage == ErrorMessages.USER_NOT_AUTHENTICATED:
            if not self.userNotAuthErrorThrown:
                self.userNotAuthErrorThrown = True
                self.send_to_login_handle_error_message(self.controller, errorMessage)
            
        elif errorMessage == ErrorMessages.CONNECTION_ERROR_SERVER:
            if not self.connectionErrorInEngin[enginNumber - 1]:
                self.connectionErrorInEngin[enginNumber - 1] = True
                self.add_connection_error_to_layout(enginNumber)
            
        else:
            if not self.unknownErrorThrown:
                self.unknownErrorThrown = True
                self.send_to_home_page_handle_error_message(errorMessage)
                
    def add_connection_error_to_layout(self, enginNumber):
        """Add connection error message when data engin container is down."""
        layout = self.get_tab_layout(enginNumber)
        errorLabel = QLabel("[engin-" + str(enginNumber) + "] ERROR    Cannot connect to data engin\n")
        errorLabel.setStyleSheet("color : red;")
        layout.addRow(errorLabel)
                        
    def get_tab_layout(self, enginNumber):
        """Return layout corresponding to enginNumber."""
        if(enginNumber == 1):
            return self.layoutEngin1
        elif(enginNumber == 2):
            return self.layoutEngin2
        else:
            return self.layoutEngin3
    
    def set_tab_layout(self, layout, logMessages, logIsText):
        """Set layout of tab depending on data type."""
        for message in logMessages:
            if logIsText:
                label = QLabel(message)
                label.setStyleSheet(self.get_label_style_sheet(message))
            else:
                label = self.convert_image_to_label(message)
            
            layout.addRow(label)
                
    def get_label_style_sheet(self, message):
        """Return style sheet corresponding to log type."""
        if "ERROR" in message:
            return "color : red;"
        elif "WARNING" in message:
            return "color : orange;"
        else:
            return "color : black;"        
        
    def initial_data_received(self):
        """Return True if all initial log messages have been received."""
        return self.initialDataReceived[0] and self.initialDataReceived[1] and self.initialDataReceived[2]
     
    def set_log_page_exited(self):
        """Set logPageExited boolean to True."""
        self.controllerEngin1.logPageExited = True
        self.controllerEngin2.logPageExited = True
        self.controllerEngin3.logPageExited = True
                          
    def closeEvent(self, event):
        """On close event, stop timer and end all threads safely."""
        self.set_log_page_exited()
        if self.initial_data_received():
            self.timer.stop()
        self.terminate_all_threads()
