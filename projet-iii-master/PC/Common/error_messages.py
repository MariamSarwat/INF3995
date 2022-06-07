"""
This class enumerates all possible error messages.
"""
from enum import Enum

class ErrorMessages(Enum):
    NONE = ''
    USER_NOT_AUTHENTICATED = 'L\'utilisateur n\'est pas authentiqué.'
    BAD_REQUEST = 'Mauvaise requête essayée.' 
    CONNECTION_ERROR_SERVER = 'Erreur de connexion avec le serveur.'
    OTHER = 'Une erreur de type inconnue s\'est produite.'
