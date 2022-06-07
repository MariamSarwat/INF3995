"""
This class sets the poll results window and calls corresponding controller
methods.
"""
from PyQt5.QtWidgets import QLabel, QWidget, QScrollArea, QStackedWidget,\
QFormLayout
from PyQt5.QtCore import QThread, pyqtSignal, Qt
from PyQt5.QtGui import QMovie

from Views.base_view import BaseView
from Controllers.poll_results_controller import PollResultsController

class PollResultsWindow(BaseView):

    present_loaded_poll_data = pyqtSignal()

    def __init__(self, windowPos):
        super().__init__()
        """Create UI and working thread."""
        self.init_working_thread()
        self.init_UI(windowPos)

    def init_working_thread(self):
        """Initialise working thread."""
        self.thread = QThread()
        self.controller = PollResultsController()
        self.create_thread(self.controller, self.thread, self.load_poll_data, \
                            self.controller.get_poll_results)

    def start_working_thread(self):
        self.terminate_thread(self.thread)
        self.init_working_thread()

    def init_UI(self, windowPos):
        """Set UI parameters and show loading screen by default."""
        self.set_window_parameters(windowPos, "Page consultation des résultats du sondage")
        self.load = QLabel()

        self.set_scroll_parameters()
        self.set_central_widget_stack()
        self.set_page_layout()

        self.present_loaded_poll_data.connect(self.present_poll_data)
        self.set_loading_status()

    def set_scroll_parameters(self):
        """Create scroll area and set parameters."""
        self.scrollArea = QScrollArea()
        scrollWidget = QWidget()
        self.scrollLayout = QFormLayout(scrollWidget)
        self.scrollArea.setWidget(scrollWidget)
        self.scrollArea.setWidgetResizable(True)

    def set_central_widget_stack(self):
        """Set and add widgets to the window center."""
        self.centralWidget = QStackedWidget()
        self.setCentralWidget(self.centralWidget)
        self.centralWidget.addWidget(self.scrollArea)
        self.centralWidget.addWidget(self.load)

    def create_tool_bar(self):
        """Create tool bar include back (to homepage) and refresh button."""
        super().create_tool_bar()
        self.tools.addAction('&Mettre à jour la page', self.handle_refresh)

    def handle_refresh(self):
        """Retrieve updated poll results from server."""
        self.set_loading_status()
        self.reset_form()
        self.start_working_thread()

    def handle_back(self):
        """Emit signal to switch back to home page."""
        self.controller.show_home_page(self.get_window_position())
        self.close()

    def present_poll_data(self):
        """Present poll data formatted into the form."""
        self.centralWidget.setCurrentWidget(self.scrollArea)

    def set_loading_status(self):
        """Show loading gif while poll results are being prepared to output."""
        self.load.setAlignment(Qt.AlignCenter)
        gif = QMovie('Views/animation/loading.gif')
        self.load.setMovie(gif)
        gif.start()
        self.centralWidget.setCurrentWidget(self.load)

    def load_poll_data(self, pollResults, errorMessage):
        """Load poll results into form."""
        from Common.error_messages import ErrorMessages
        if errorMessage == ErrorMessages.NONE:
            for item in pollResults:
                self.scrollLayout.addRow(QLabel(item))
            self.present_loaded_poll_data.emit()

        else:
            self.handle_error_message(self.controller, errorMessage)

    def reset_form(self):
        """Reset form by removing all rows."""
        rowCount = self.scrollLayout.rowCount()
        for index in range(rowCount):
            self.scrollLayout.removeRow(0)

    def closeEvent(self, event):
        """Terminate all threads when app is exited."""
        self.terminate_thread(self.thread)
