import base64
import datetime
import io
import logging

import matplotlib.pyplot as plt

import numpy as np

import pandas as pd

import pydot

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.tree import export_graphviz

from src.utils import Times, format_date

def getprediction(data, dates, time):

    plt.style.use('fivethirtyeight')
    if len(data.Average.value_counts()) == 0:
        data=data.drop(columns=['Average'])
        data, data_list, labels= features_and_targets(data)

        # Split the data into training and testing sets
        # pylint: disable=line-too-long
        if time == Times.PerDayOfWeek.value:
            train_data, test_data, train_labels, test_labels = train_test_split(data,
                                                                                labels,
                                                                                test_size = 0.70, random_state = 42)
        else:
            train_data, test_data, train_labels, test_labels = train_test_split(data,
                                                                                labels,
                                                                                test_size = 0.25, random_state=42)
        predictions= predictionByTrainModelWithoutAverage(train_data, test_data,train_labels)
    else:
        data, data_list, labels= features_and_targets(data)

        # Split the data into training and testing sets
        # pylint: disable=line-too-long
        if time == Times.PerDayOfWeek.value:
            train_data, test_data, train_labels, test_labels = train_test_split(data,
                                                                                labels,
                                                                                test_size=0.70, random_state=42)
        else:
            train_data, test_data, train_labels, test_labels = train_test_split(data,
                                                                                labels,
                                                                                test_size = 0.25, random_state=42)

        predictions = predictionByTrainModel(train_data, test_data, train_labels, test_labels, data_list)
    test_dates = get_test_dates(data_list, time,test_data)

    # Dataframes with true values and predictions
    # pylint: disable=line-too-long
    actual_data      = pd.DataFrame(data={'temps' : dates,      'actuel'     : labels})
    predictions_data = pd.DataFrame(data={'temps' : test_dates, 'prediction' : predictions})

    result = pd.merge(predictions_data, actual_data, how='outer', on='temps')
    result = result.sort_values(by=['temps'])
    result = result.interpolate()
    result = result.round(1)

    predictions_data = result.drop(columns=['actuel'])
    predictions_data = predictions_data.sort_values(by=['temps'])

    thunk = create_plot(actual_data, predictions_data)

    return result, thunk

def features_and_targets(data):

    # One-hot encode to convert categorial viables to numerical representation
    data = pd.get_dummies(data)

    # Labels are the values we want to predict
    labels = np.array(data['Actual'])

    # Remove the labels from the data
    data = data.drop('Actual', axis = 1)

    # Saving feature names for later use
    data_list = list(data.columns)

    # Convert to numpy array
    data = np.array(data)

    return data, data_list, labels

def create_plot(actual_data, predictions_data):

    # Plot the predicted values
    plt.plot(actual_data['temps'],
             actual_data['actuel'],
             'b-',
             label='actuel')

    plt.plot(predictions_data['temps'],
             predictions_data['prediction'],
             'ko',
             label='prediction',
             alpha=0.8)

    plt.xticks(rotation = '60')
    plt.legend()

    # Graph labels
    plt.xlabel('Temps')
    plt.ylabel('Nombre de departs')
    plt.title('Valeur actuelles et predites')
    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format="png")

    thunk = lambda: logging.info("bixi-graph: %s",
                                 base64.b64encode(buf.getbuffer())
                                 .decode("utf-8"))
    thunk()

    plt.close()

    return thunk

def get_test_dates(data_list, time, test_data):

    if time == Times.PerDay.value:
        months = test_data[:, data_list.index('Month')]
        days   = test_data[:, data_list.index('Day')]
        years  = test_data[:, data_list.index('Year')]

        test_dates = [format_date(year, month, day)
                      for year, month, day
                      in zip(years, months, days)]

        test_dates = [datetime.datetime.strptime(date, '%Y-%m-%d')
                      for date
                      in test_dates]

    elif time == Times.PerHours.value:
        test_dates = test_data[:, data_list.index('Hour')]
        test_dates = test_dates.astype(np.int)

    elif time == Times.PerDayOfWeek.value:
        test_dates = test_data[:, data_list.index('Weekday')]
        test_dates = test_dates.astype(np.int)

    elif time == Times.PerTemperature.value:
        test_dates = test_data[:, data_list.index('Temperature')]
        test_dates = test_dates.astype(np.int)

    return test_dates

def predictionByTrainModelWithoutAverage(train_data, test_data,
                                         train_labels):
    # Instantiate model
    rf = RandomForestRegressor(n_estimators= 1000, random_state=42)
    # Train the model on training data
    rf.fit(train_data, train_labels)
    predictions = rf.predict(test_data)
    return predictions

def predictionByTrainModel(train_data, test_data,
                           train_labels, _test_labels,
                           data_list):
    # Instantiate model
    rf = RandomForestRegressor(n_estimators= 1000, random_state=42)

    # Train the model on training data
    rf.fit(train_data, train_labels)

    predictions = rf.predict(test_data)

    # Pull out one tree from the forest
    tree = rf.estimators_[5]

    # Export the image to a dot file
    export_graphviz(tree,
                    out_file='tree.dot',
                    feature_names=data_list,
                    rounded=True,
                    precision=1)

    # Use dot file to create a graph
    (graph, ) = pydot.graph_from_dot_file('tree.dot')

    # Write graph to a png file
    graph.write_png('tree.png')

    # Limit depth of tree to 2 levels
    rf_small = RandomForestRegressor(n_estimators=10,
                                     max_depth=3,
                                     random_state=42)

    rf_small.fit(train_data, train_labels)

    # Extract the small tree
    tree_small = rf_small.estimators_[5]

    # Save the tree as a png image
    export_graphviz(tree_small,
                    out_file='small_tree.dot',
                    feature_names=data_list,
                    rounded=True,
                    precision=1)

    (graph, ) = pydot.graph_from_dot_file('small_tree.dot')

    graph.write_png('small_tree.png')

    # New random forest with only the two most important variables
    rf_most_important = RandomForestRegressor(n_estimators=1000,
                                              random_state=42)

    # Extract the two most important data
    important_indices = [data_list.index('Average')]
    train_important   = train_data[:, important_indices]
    test_important    = test_data[:, important_indices]

    # Train the random forest
    rf_most_important.fit(train_important, train_labels)

    # Make predictions
    predictions = rf_most_important.predict(test_important)

    return predictions
