import sys
import unittest

from unittest.mock import patch
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QLabel
from Common import error_messages
from Views import login_view, home_page_view, log_message_view, change_password_view, poll_results_view

app = QApplication(sys.argv)

class LoginWindowTest(unittest.TestCase):
    '''Test the login window GUI'''
    def setUp(self):
        """Create the LoginWindow"""
        self.window = login_view.LoginWindow()

    def test_username_input(self):
        """Test username input is read only."""
        self.assertTrue(self.window.usernameLine.isReadOnly())

    def test_password_input(self):
        """Test password line edit."""
        self.window.passwordLine.clear()
        QTest.keyClicks(self.window.passwordLine, 'password')
        self.assertEqual(self.window.passwordLine.text(), 'password')

    @patch('Views.login_view.LoginWindow.is_login_valid', return_value=(True, error_messages.ErrorMessages.NONE))
    @patch('Views.login_view.LoginWindow.get_window_position', return_value=QPoint(0, 0))
    @patch('Views.login_view.LoginWindow.controller.show_home_page')
    def test_ok_button_with_valid_password(self, show_home_page, get_window_position, is_login_valid):
        """Test ok button with a valid password."""
        okWidget = self.window.buttonBox.button(self.window.buttonBox.Ok)
        QTest.mouseClick(okWidget, Qt.LeftButton)
        self.assertTrue(okWidget.clicked)
        self.assertTrue(get_window_position.called)

    def test_cancel_button(self):
        """Test cancel button."""
        cancelWidget = self.window.buttonBox.button(self.window.buttonBox.Cancel)
        QTest.mouseClick(cancelWidget, Qt.LeftButton)
        self.assertTrue(cancelWidget.clicked)

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.window

class HomePageWindowTest(unittest.TestCase):
    '''Test the home page window GUI'''
    @patch('Views.home_page_view.HomePageWindow.add_bixi_logo_to_window')
    def setUp(self, add_bixi_logo_to_window):
        """Create the HomePageWindow"""
        self.window = home_page_view.HomePageWindow(QPoint(0, 0))

    @patch('PyQt5.QtWidgets.QMainWindow.close')
    @patch('Views.home_page_view.HomePageWindow.get_window_position', return_value=QPoint(0, 0))
    @patch('Views.home_page_view.HomePageWindow.controller.show_change_password_page')
    def test_change_password_button(self, show_change_password_page, get_window_position, close):
        """Test change password button."""
        self.window.handle_change_password()
        self.assertEqual(get_window_position.call_count, 1)
        self.assertTrue(close.called)
        self.assertTrue(show_change_password_page.called)

    @patch('PyQt5.QtWidgets.QMainWindow.close')
    @patch('Views.home_page_view.HomePageWindow.get_window_position', return_value=QPoint(0, 0))
    @patch('Views.home_page_view.HomePageWindow.controller.show_log_message_page')
    def test_log_message_button(self, show_log_message_page, get_window_position, close):
        """Test show log messages button."""
        self.window.handle_log_messages()
        self.assertEqual(get_window_position.call_count, 1)
        self.assertTrue(close.called)
        self.assertTrue(show_log_message_page.called)

    @patch('PyQt5.QtWidgets.QMainWindow.close')
    @patch('Views.home_page_view.HomePageWindow.get_window_position', return_value=QPoint(0, 0))
    @patch('Views.home_page_view.HomePageWindow.controller.show_poll_results_page')
    def test_poll_results_button(self, show_poll_results_page, get_window_position, close):
        """Test show poll results button."""
        self.window.handle_poll_results()
        self.assertEqual(get_window_position.call_count, 1)
        self.assertTrue(close.called)
        self.assertTrue(show_poll_results_page.called)

    def test_get_position(self):
        """Test checks if position returned by get_window_position is (200, 200)."""
        self.window.move(200, 200)
        position = self.window.get_window_position()
        self.assertEqual(position, QPoint(200,200))

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.window

class LogMessageWindowTest(unittest.TestCase):
    '''Test the log message page window GUI'''
    @patch('Views.log_message_view.LogMessageWindow.init_working_thread')
    @patch('Views.log_message_view.LogMessageWindow.start_working_thread')
    @patch('Views.log_message_view.LogMessageWindow.set_loading_status')
    def setUp(self, set_loading_status, RepeatedTimer, init_working_thread):
        """Create the LogMessageWindow"""
        self.window = log_message_view.LogMessageWindow(QPoint(0, 0))
    
    @patch('Views.log_message_view.LogMessageWindow.set_log_page_exited')
    @patch('Views.log_message_view.LogMessageWindow.terminate_all_threads')
    @patch('Views.log_message_view.LogMessageWindow.initial_data_received', return_value=False)
    def test_close_event(self, initial_data_received, terminate_all_threads, set_log_page_exited):
        """Test if on close event, the corresponding functions are called."""
        self.window.close()
        self.assertTrue(terminate_all_threads.called)
        self.assertTrue(set_log_page_exited.called)
    
    @patch('Views.log_message_view.LogMessageWindow.send_to_home_page_handle_error_message')
    def test_handle_engin_error_message_other(self, send_to_home_page_handle_error_message):
        """Test if else is called."""
        from Common.error_messages import ErrorMessages
        self.window.handle_engin_error_message(2, ErrorMessages.OTHER)
        self.assertTrue(self.window.unknownErrorThrown)
        self.assertTrue(send_to_home_page_handle_error_message.called)
    
    @patch('Views.log_message_view.LogMessageWindow.send_to_login_handle_error_message')
    def test_handle_engin_error_message_user_not_auth(self, send_to_login_handle_error_message):
        """Test if handle error message sets userNotAuth boolean and calls send_to_login_handle_error_message function."""
        from Common.error_messages import ErrorMessages
        self.window.handle_engin_error_message(2, ErrorMessages.USER_NOT_AUTHENTICATED)
        self.assertTrue(self.window.userNotAuthErrorThrown)
        self.assertTrue(send_to_login_handle_error_message.called)
    
    @patch('Views.log_message_view.LogMessageWindow.add_connection_error_to_layout')
    def test_handle_engin_error_message_connection_error(self, add_connection_error_to_layout):
        """Test if handle error message sets connection error boolean and calls add_connection_error_to_layout function."""
        from Common.error_messages import ErrorMessages
        self.window.handle_engin_error_message(2, ErrorMessages.CONNECTION_ERROR_SERVER)
        self.assertTrue(self.window.connectionErrorInEngin[1])
        self.assertTrue(add_connection_error_to_layout.called) 
    
    @patch('Views.log_message_view.LogMessageWindow.set_tab_layout')
    def test_handle_server_response(self, set_tab_layout):
        """Test if handle server response sets connection error boolean and calls set_tab_layout function."""
        from Common.error_messages import ErrorMessages
        self.window.handle_server_response(2, [], '', ErrorMessages.NONE)
        self.assertFalse(self.window.connectionErrorInEngin[1])
        self.assertTrue(set_tab_layout.called)          
            
    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.window

class ChangePasswordWindowTest(unittest.TestCase):
    '''Test the home page window GUI'''
    def setUp(self):
        """Create the ChangePasswordWindow"""
        self.window = change_password_view.ChangePasswordWindow(QPoint(0, 0))

    def test_new_pass_input(self):
        """Test if new password line edit is set to \'password\'."""
        self.window.newPassLine.clear()
        QTest.keyClicks(self.window.newPassLine, 'password')
        self.assertEqual(self.window.newPassLine.text(), 'password')

    def test_confirm_new_pass_input(self):
        """Test if confirm new password line edit is set to \'confirm123\'."""
        self.window.confirmNewPassLine.clear()
        QTest.keyClicks(self.window.confirmNewPassLine, 'confirm123')
        self.assertEqual(self.window.confirmNewPassLine.text(), 'confirm123')

    @patch('PyQt5.QtWidgets.QMainWindow.close')
    @patch('Views.change_password_view.ChangePasswordWindow.get_window_position', return_value=QPoint(0, 0))
    @patch('Views.change_password_view.ChangePasswordWindow.controller.show_home_page')
    def test_back_button_calls_show_home_page(self, show_home_page, get_window_position, close):
        """Test verifies if back tool calls the show home page controller function."""
        backWidget = self.window.tools.actions()[0].trigger()
        self.assertEqual(get_window_position.call_count, 1)
        self.assertTrue(close.called)
        self.assertTrue(show_home_page.called)

    def test_valid_password_entry_with_equal_passwords(self):
        """Test verifies if should valid_password_entry returns true."""
        self.window.confirmNewPassLine.clear()
        QTest.keyClicks(self.window.confirmNewPassLine, 'password')
        self.window.newPassLine.clear()
        QTest.keyClicks(self.window.newPassLine, 'password')
        validPass = self.window.valid_password_entry()
        self.assertTrue(validPass)

    def test_valid_password_entry_with_empty_passwords(self):
        """Test verifies if valid_password_entry returns false."""
        self.window.confirmNewPassLine.clear()
        QTest.keyClicks(self.window.confirmNewPassLine, '')
        self.window.newPassLine.clear()
        QTest.keyClicks(self.window.newPassLine, '')
        validPass = self.window.valid_password_entry()
        self.assertFalse(validPass)

    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.window

class PollResultsWindowTest(unittest.TestCase):
    '''Test the poll results page window GUI'''
    @patch('Views.poll_results_view.PollResultsWindow.init_working_thread')
    def setUp(self, init_working_thread):
        """Create the PollResultsWindow"""
        self.window = poll_results_view.PollResultsWindow(QPoint(0, 0))

    def test_reset_form(self):
        """Test checks if reset form removes all rows (so rowCount should be 0)."""
        self.window.scrollLayout.addRow(QLabel("this is row 1"))
        self.window.scrollLayout.addRow(QLabel("this is row 2"))
        self.assertEqual(self.window.scrollLayout.rowCount(), 2)
        self.window.reset_form()
        self.assertEqual(self.window.scrollLayout.rowCount(), 0)
    
    def test_load_poll_data(self):
        """Test if load poll data sets window layout."""
        from Common.error_messages import ErrorMessages
        self.window.load_poll_data(['1', '2'], ErrorMessages.NONE)
        self.assertEqual(self.window.scrollLayout.rowCount(), 2)    
        
    def tearDown(self):
        '''Deletes the reference owned by self'''
        del self.window
