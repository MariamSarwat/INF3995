"""
This class retrieves and treats poll data from server.
"""
from PyQt5.QtCore import pyqtSignal, QObject

from Common.error_messages import ErrorMessages
from Common.request_status_code import StatusCodes
from Controllers.base_controller import BaseController
import Controllers.auth as auth

class PollResultsController(BaseController, QObject):
    
    dataReady = pyqtSignal(list, ErrorMessages)

    def __init__(self):
        super().__init__()
        
    def get_poll_results(self):
        """Return list of polling results retrieved from server."""
        response = auth.global_http.get(uri='/sondage')
        self.treat_response(response)
        
    def treat_response(self, response):
        """Treat returned response from server, if invalid return empty
        list with a corresponding error message.
        """
        errorMessage = self.get_error_message(response)
        if response.status_code == StatusCodes.OK.value:
            parsedPollResults = self.parse_json(response)
        else:
            parsedPollResults = []
            
        self.dataReady.emit(parsedPollResults, errorMessage)
            
    def parse_json(self, response):
        """Parse returned json and return list of polling results. 
        In case of error, return empty list.
        """
        pollResults = response.json()
        parsedResults = []
        introString = "Il y a, en ce moment, " + str(len(pollResults)) + " résultats qui ont été enregistrés. \n" 
        parsedResults.append(introString)
        for result in pollResults:
            name = result['prenom'] + " " + result['nom'] + " \n"
            email = "    courriel : " + result['courriel'] + "\n"
            age = "    âge         : " + str(result['age']) + "\n"
            interested = "    intêret   : " + str(result['interet']) + "\n"
            resultToString = name + email + age + interested
            parsedResults.append(resultToString)
        return parsedResults      
