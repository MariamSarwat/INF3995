"""
This class retrieves log messages for each data engin and treats response 
in order to append it in corresponding UI.
"""
import base64
from PyQt5.QtCore import pyqtSignal, QObject
from requests import Response

from Common.request_status_code import StatusCodes
from Common.error_messages import ErrorMessages
from Controllers.base_controller import BaseController
import Controllers.auth as auth

class LogMessageController(BaseController, QObject):
    dataReady = pyqtSignal(int, list, bool, ErrorMessages)
    initLogLoadFinished = pyqtSignal(int)
    logPageExited = False
    
    def __init__(self, enginNumber=0, inital_data_received=False):
        super().__init__()
        self.enginNumber = enginNumber
        self.inital_data_received = inital_data_received
    
    def get_log_messages(self):
        """Return log messages retrived from data engins."""
        while not self.logPageExited:
            try:
                lastByte = str(auth.last_byte[self.enginNumber - 1])
                enginNumber = str(self.enginNumber)
                response = auth.global_http.get(uri='/logs/' + enginNumber + '/' + lastByte)
            except :
                response = Response()
                response.status_code = 404
                
            self.treat_response(response)
            if not response.status_code == StatusCodes.OK.value:
                break
             
    def treat_response(self, response):
        """Treat returned response from server, if invalid return empty     
        list.
        """     
        errorMessage = self.get_error_message(response)

        if response.status_code == StatusCodes.OK.value:
            (logMessages, isText) = self.parse_json(response)
        else:
            (logMessages, isText) = ([], False)
                
        self.dataReady.emit(self.enginNumber, logMessages, isText, errorMessage)
        
        if response.status_code in (StatusCodes.NO_CONTENT_TO_RETURN.value, StatusCodes.CONNECTION_ERROR.value): 
            if not self.inital_data_received:
                self.initLogLoadFinished.emit(self.enginNumber - 1)
           
    def extract_graph_data(self, logMessages):
        """Treat graph data. Decode into binary."""
        raw_pngs = []
        for item in logMessages:
            byteRep = bytes(item.split("bixi-graph: ")[1], "ascii")
            raw_pngs.append(base64.b64decode(byteRep))
        return raw_pngs
        
    def parse_json(self, response):
        """Parse returned json and return list of polling results. 
        In case of error, return empty list.
        """
        logMessages = response.json()        
        auth.last_byte[self.enginNumber - 1] += logMessages['nbrOctets']

        if bool(logMessages['texte']):
            return (logMessages['blocks'], bool(logMessages['texte']))
        else:
            return (self.extract_graph_data(logMessages['blocks']), bool(logMessages['texte']))
           
