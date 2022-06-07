"""
This class enumerates all possible http response status codes.
"""

from enum import Enum

class StatusCodes(Enum):
    OK = 200
    NO_CONTENT_TO_RETURN = 204
    USER_NOT_AUTHENTICATED = 401
    BAD_REQUEST = 400 
    USER_NOT_AUTHORISED = 403
    CONNECTION_ERROR = 404
