from enum import Enum

class Times(Enum):
    PerHours       = 'parheure'
    PerDayOfWeek   = 'parjourdelasemaine'
    PerMonth       = 'parmois'
    PerDay         = 'parjour'
    PerTemperature = 'partemperature'


def format_date(year, month, day):
    return f"{int(year)}-{int(month)}-{int(day)}"
