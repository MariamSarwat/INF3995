import pandas as pd
import numpy as np

from src import db
from src.utils import Times

# NOTE!  secondQuery should be execute AFTER firstQuery has been used by Panda.
# Otherwise, the data get deleted for no apparent reason

def getdataframe(station, time):

    if station == "toutes":
        matches = {
            Times.PerDay         : lambda x: dataByDayAll(),
            Times.PerHours       : lambda x: dataByHourAll(),
            Times.PerDayOfWeek   : lambda x: dataByWeekdayAll(),
            Times.PerTemperature : lambda x: dataByTemperatureAll(),
        }
    else:
        matches = {
            Times.PerDay         : dataByDayStation,
            Times.PerHours       : dataByHourStation,
            Times.PerDayOfWeek   : dataByWeekdayStation,
            Times.PerTemperature : dataByTemperatureStation,
        }

    actual  = None
    average = None

    for key in matches:
        if time == key.value:
            actual, average = matches[key](station)
            break
    if actual['COUNT(BIXIDATA.Station)'].isnull().all():
        return pd.DataFrame()
    if average.empty:
        actual['Average']=np.nan
        actual=actual.rename(columns={'COUNT(BIXIDATA.Station)':'Actual'})
        return actual
    actual, average = renameColumns(actual, average)
    return mergeTables(actual, average, time)

def mergeTables(actual, average, time):

    matches = {
        Times.PerDay         : ["Day", "Month"],
        Times.PerHours       : ["Hour"],
        Times.PerDayOfWeek   : ["Weekday"],
        Times.PerTemperature : ["Temperature"]
    }

    result = None

    for key in matches:
        if time == key.value:
            result = pd.merge(actual, average, on=matches[key])
            break

    return result

def renameColumns(actual, average):

    average = average.rename(columns={'COUNT(BIXIDATA.Station)':'Average'})
    actual  = actual.rename(columns={'COUNT(BIXIDATA.Station)':'Actual'})

    return actual, average

def dataByDayAll():

    # pylint: disable=line-too-long
    firstQuery  = "SELECT COUNT(BIXIDATA.Station),[Year],[Month],[Day] FROM BIXIDATA WHERE Year<2017 GROUP BY Month, Day, Year"
    secondQuery = "SELECT COUNT(BIXIDATA.Station),[Year],[Month],[Day] FROM BIXIDATA WHERE Year=2017 GROUP BY Month, Day"

    average = db.make_json_from_sql(firstQuery)
    average = pd.DataFrame(average)
    average = average.groupby(['Month','Day'])['COUNT(BIXIDATA.Station)'].mean().reset_index()

    actual = db.make_json_from_sql(secondQuery)
    actual = pd.DataFrame(actual)

    return actual, average

def dataByHourAll():

    # pylint: disable=line-too-long
    firstQuery  = "SELECT COUNT(BIXIDATA.Station), BIXIDATA.Hour FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year<2017 GROUP BY BIXIDATA.Hour"
    average     = db.make_json_from_sql(firstQuery)
    average     = pd.DataFrame(average)

    secondQuery = "SELECT COUNT(BIXIDATA.Station), BIXIDATA.Hour FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year=2017 GROUP BY BIXIDATA.Hour"
    actual      = db.make_json_from_sql(secondQuery)
    actual      = pd.DataFrame(actual)

    average['COUNT(BIXIDATA.Station)'] /= 3

    return actual, average

def dataByWeekdayAll():

    # pylint: disable=line-too-long
    firstQuery  = "SELECT COUNT(BIXIDATA.Station), BIXIDATA.Weekday FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year<2017 GROUP BY BIXIDATA.Weekday"
    average     = db.make_json_from_sql(firstQuery)
    average     = pd.DataFrame(average)

    secondQuery = "SELECT COUNT(BIXIDATA.Station), BIXIDATA.Weekday FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year=2017 GROUP BY BIXIDATA.Weekday"
    actual      = db.make_json_from_sql(secondQuery)
    actual      = pd.DataFrame(actual)

    average['COUNT(BIXIDATA.Station)'] /= 3

    return actual, average

def dataByTemperatureAll():

    # pylint: disable=line-too-long
    firstQuery  = "SELECT COUNT(BIXIDATA.Station), BIXIDATA.Temperature FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year<2017 GROUP BY BIXIDATA.Temperature "
    average     = db.make_json_from_sql(firstQuery)
    average     = pd.DataFrame(average)
    average     = average.round({'Temperature': 0})
    average     = average.groupby(['Temperature'])['COUNT(BIXIDATA.Station)'].sum().reset_index()

    average['COUNT(BIXIDATA.Station)'] /= 3
    average['Temperature'] -= 273.15

    secondQuery = "SELECT COUNT(BIXIDATA.Station), BIXIDATA.Temperature FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year=2017 GROUP BY BIXIDATA.Temperature "
    actual      = db.make_json_from_sql(secondQuery)
    actual      = pd.DataFrame(actual)
    actual      = actual.round({'Temperature': 0})
    actual      = actual.groupby(['Temperature'])['COUNT(BIXIDATA.Station)'].sum().reset_index()

    actual['Temperature'] -= 273.15
    temperature=dataTemperatureFor2018()
    actual=pd.concat([actual, temperature], axis=1, ignore_index=False)
    return actual, average

def dataByDayStation(station):

    # pylint: disable=line-too-long
    firstQuery  = db.execute("SELECT COUNT(BIXIDATA.Station),[Year],[Month],[Day] FROM BIXIDATA WHERE Year<2017 AND Station=? GROUP BY Month, Day, Year", [station])
    cols        = [column[0] for column in firstQuery.description]
    average     = pd.DataFrame.from_records(data = firstQuery.fetchall(), columns=cols)

    secondQuery = db.execute("SELECT COUNT(BIXIDATA.Station),[Year],[Month],[Day] FROM BIXIDATA WHERE Year=2017 AND Station=? GROUP BY Month, Day", [station])
    cols2       = [column[0] for column in secondQuery.description]
    actual      = pd.DataFrame.from_records(data = secondQuery.fetchall(), columns=cols2)
    if average.empty:
        return actual, average
    average=average.groupby(['Month','Day'])['COUNT(BIXIDATA.Station)'].mean().reset_index()
    return actual, average

def dataByHourStation(station):

    # pylint: disable=line-too-long
    firstQuery  = db.execute("SELECT COUNT(BIXIDATA.Station), BIXIDATA.Hour FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year<2017 AND Station=? GROUP BY BIXIDATA.Hour", [station])
    cols        = [column[0] for column in firstQuery.description]
    average     = pd.DataFrame.from_records(data = firstQuery.fetchall(), columns=cols)

    secondQuery = db.execute("SELECT COUNT(BIXIDATA.Station), BIXIDATA.Hour FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year=2017 AND Station=? GROUP BY BIXIDATA.Hour", [station])
    cols2       = [column[0] for column in secondQuery.description]
    actual      = pd.DataFrame.from_records(data = secondQuery.fetchall(), columns=cols2)
    if average.empty:
        return actual, average
    average['COUNT(BIXIDATA.Station)'] /= 3
    return actual, average

def dataByWeekdayStation(station):

    # pylint: disable=line-too-long
    firstQuery  = db.execute("SELECT COUNT(BIXIDATA.Station), BIXIDATA.Weekday FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year<2017 AND Station=? GROUP BY BIXIDATA.Weekday", [station])
    cols        = [column[0] for column in firstQuery.description]
    average     = pd.DataFrame.from_records(data = firstQuery.fetchall(), columns=cols)

    secondQuery = db.execute("SELECT COUNT(BIXIDATA.Station), BIXIDATA.Weekday FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year=2017 AND Station=? GROUP BY BIXIDATA.Weekday", [station])
    cols2       = [column[0] for column in secondQuery.description]
    actual      = pd.DataFrame.from_records(data = secondQuery.fetchall(), columns=cols2)
    if average.empty:
        return actual, average
    average['COUNT(BIXIDATA.Station)'] /= 3
    return actual, average

def dataByTemperatureStation(station):

    # pylint: disable=line-too-long
    firstQuery  = db.execute("SELECT COUNT(BIXIDATA.Station), BIXIDATA.Temperature FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year<2017 AND Station=? GROUP BY BIXIDATA.Temperature", [station])
    cols        = [column[0] for column in firstQuery.description]
    average     = pd.DataFrame.from_records(data = firstQuery.fetchall(), columns=cols)
    average     = average.round({'Temperature': 0})
    average     = average.groupby(['Temperature'])['COUNT(BIXIDATA.Station)'].sum().reset_index()

    secondQuery = db.execute("SELECT COUNT(BIXIDATA.Station), BIXIDATA.Temperature FROM BIXIDATA INNER JOIN DATES ON BIXIDATA.Month=DATES.Month AND BIXIDATA.Day=DATES.Day WHERE BIXIDATA.Year=2017 AND Station=? GROUP BY BIXIDATA.Temperature", [station])
    cols2       = [column[0] for column in secondQuery.description]
    actual      = pd.DataFrame.from_records(data = secondQuery.fetchall(), columns=cols2)
    actual      = actual.round({'Temperature': 0})
    actual      = actual.groupby(['Temperature'])['COUNT(BIXIDATA.Station)'].sum().reset_index()

    actual['Temperature'] -= 273.15
    temperature=dataTemperatureFor2018()
    actual=pd.concat([actual, temperature], axis=1, ignore_index=False)
    if average.empty:
        return actual, average
    average['COUNT(BIXIDATA.Station)'] /= 3
    average['Temperature'] -= 273.15
    return actual, average

def dataTemperatureFor2018():

    # pylint: disable=line-too-long
    thirdQuery="SELECT Temp2018 FROM TEMPERATURE INNER JOIN DATES ON TEMPERATURE.Month=DATES.Month AND TEMPERATURE.Day=DATES.Day"
    temperature=db.make_json_from_sql(thirdQuery)
    temperature=pd.DataFrame(temperature)
    temperature= temperature.round({'Temp2018': 0})
    temperature= temperature.drop_duplicates()
    temperature=temperature.sort_values(by='Temp2018',ascending=True)
    temperature.drop(temperature.index[:5], inplace=True)
    temperature=temperature.reset_index()
    temperature=temperature.drop(columns='index')
    return temperature
