import sys
import unittest

from unittest.mock import patch, Mock
from PyQt5.QtTest import QTest, QSignalSpy
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtWidgets import QApplication, QMessageBox, QPushButton, QLabel

from Controllers import login_controller, home_page_controller, log_message_controller, change_password_controller, poll_results_controller

from Views import poll_results_view

import Controllers.auth

app = QApplication(sys.argv)

class LoginControllerTest(unittest.TestCase):
    '''Test the login controller'''

    def setUp(self):
        """Create the LoginController"""
        self.controller = login_controller.LoginController()

    def test_returns_true_if_password_valid(self):
        """Test returns true if the inputed password is valid."""
        with patch('Controllers.auth.global_http.post') as mock_request:
            mock_request.return_value.status_code = 200
            (passwordValid, errorMessage) = self.controller.validate_login('hello', '00.00.00.00')
            self.assertTrue(passwordValid)

    def test_returns_false_if_password_is_not_valid(self):
        """Test returns false if the password inputed is invalid."""
        with patch('Controllers.auth.global_http.post') as mock_request:
            mock_request.return_value.status_code = 403
            (passwordValid, errorMessage) = self.controller.validate_login('hello', '00.00.00.00')
            self.assertFalse(passwordValid)

    def tearDown(self):
        del self.controller

class PollResultsControllerTest(unittest.TestCase):
    '''Test the poll results controller'''

    def setUp(self):
        """Create the PollResultsController"""
        self.controller = poll_results_controller.PollResultsController()
        
    def poll_results(self, results):
        self.pollResults = results

    @patch('PyQt5.QtWidgets.QMainWindow.show')
    def test_sets_position_and_shows_home_page_view(self, show):
        """Test returns true if home page position is set to (0,0) and window is shown."""
        self.controller.show_home_page(QPoint(0, 0))
        self.assertEqual(self.controller.homePageWindow.pos(), QPoint(0, 0))
        self.assertTrue(show.called)

    def test_returns_empty_list_if_request_is_invalid(self):
        """Test returns true if the get_poll_result with an invalid status code returns an empty list."""
        with patch('Controllers.auth.global_http.get') as mock_request:
            mock_request(uri='/sondage')
            mock_request.return_value.status_code = 400
            self.controller.dataReady.connect(self.poll_results)
            self.controller.get_poll_results()

            self.assertEqual(self.pollResults, [])

    def test_returns_parsed_json_if_request_is_valid(self):
        """Test returns true if get_poll_results returns a list of length 3 containing the output list."""
        with patch('Controllers.auth.global_http.get') as mock_request:
            mock_request.return_value = Mock(status_code=200,
                    json=lambda : [{
                    'courriel': 'test1@toto.ca',
                    'prenom': 'S',
                    'nom': 'M',
                    'age': 89,
                    'interet': True,
                    }, {
                    'courriel': 'test2@jsjs.com',
                    'prenom': 'K',
                    'nom': 'D',
                    'age': 1,
                    'interet': False,
                    }, {
                    'courriel': 'test3@asdas.com',
                    'prenom': 'W',
                    'nom': 'H',
                    'age': 1,
                    'interet': True,
                    }])
            self.controller.dataReady.connect(self.poll_results)
            self.controller.get_poll_results()
            self.pollResults.pop(0)
            self.assertEqual(len(self.pollResults), 3)
            self.assertEqual(self.pollResults,
['S M \n    courriel : test1@toto.ca\n    âge         : 89\n    intêret   : True\n',
'K D \n    courriel : test2@jsjs.com\n    âge         : 1\n    intêret   : False\n',
'W H \n    courriel : test3@asdas.com\n    âge         : 1\n    intêret   : True\n'])

class LogMessageControllerTest(unittest.TestCase):
    '''Test the log message controller'''

    def setUp(self):
        """Create the LogMessageController"""
        self.controller = log_message_controller.LogMessageController(enginNumber=1)
    
    def log_messages(self, enginNbr, results, dataType, errorMsg):
        self.logMessages = results
        
    @patch('PyQt5.QtWidgets.QMainWindow.show')
    def test_sets_position_and_shows_home_page_view(self, show):
        """Test returns true if home page position is set to (0,0) and window is shown."""
        self.controller.show_home_page(QPoint(0, 0))
        self.assertEqual(self.controller.homePageWindow.pos(), QPoint(0, 0))
        self.assertTrue(show.called)
        
    def test_extract_graph_data(self):
        """Test that base64 decoding works."""
        logData = self.controller.extract_graph_data(['bixi-graph: Zg=='])
        self.assertEqual(logData, [b'f'])
        
    def test_parse_json(self):
        """Test that parse json returns data array."""
        with patch('Controllers.auth.global_http.get') as response:
            response = Mock(status_code=200,
                    json=lambda : {
                    'nbrOctets': 30,
                    'texte': True,
                    'blocks': ['engin1']
                    })
            (logMessages, dataType) = self.controller.parse_json(response)
            self.assertEqual(logMessages, ['engin1'])

class ChangePasswordControllerTest(unittest.TestCase):
    '''Test the home page controller'''

    def setUp(self):
        """Create the ChangePasswordController"""
        self.controller = change_password_controller.ChangePasswordController()

    @patch('PyQt5.QtWidgets.QMainWindow.show')
    def test_sets_position_and_shows_home_page_view(self, show):
        """Test returns true if home page position is set to (0,0) and window is shown."""
        self.controller.show_home_page(QPoint(0, 0))
        self.assertEqual(self.controller.homePageWindow.pos(), QPoint(0, 0))
        self.assertTrue(show.called)
