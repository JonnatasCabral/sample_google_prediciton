# -*- coding: utf-8 -*-
"""Simple command-line sample for the Google Prediction API
Command-line application that trains on your input data. This sample does
the same thing as the Hello Prediction! example. You might want to run
the setup.sh script to load the sample data to Google Storage.
Usage:
  $ python prediction.py "bucket/object" "model_id" "project_id"
You can also get help on all the command-line flags the program understands
by running:
  $ python prediction.py --help
To get detailed log output run:
  $ python func prediction.py --logging_level=DEBUG
"""

from __future__ import print_function


import argparse
import os
import pprint
import sys
import time


from apiclient import discovery
from apiclient import sample_tools
from oauth2client import client


# Time to wait (in seconds) between successive checks of training status.
SLEEP_TIME = 10


# Declare command-line flags.
argparser = argparse.ArgumentParser(add_help=False)

argparser.add_argument(
    'object_name',
    help='Full Google Storage path of csv data (ex bucket/object)')
argparser.add_argument(
    'model_id',
    help='Model Id of your choosing to name trained model')
argparser.add_argument(
    'project_id',
    help='Project Id of your Google Cloud Project')


def print_header(line):
    '''Format and print header block sized to length of line'''
    header_str = '='
    header_line = header_str * len(line)
    print('\n' + header_line)
    print(line)
    print(header_line)


def autentication(argv):
    service, flags = sample_tools.init(
      argv, 'prediction', 'v1.6', __doc__, __file__, parents=[argparser],
      scope=(
          'https://www.googleapis.com/auth/prediction',
          'https://www.googleapis.com/auth/devstorage.read_only'))
    return service, flags


def train_model(argv):

    service, flags = autentication(argv)
    try:
        # Get access to the Prediction API.
        api = service.trainedmodels()

        # List models.
        print_header('Fetching list of first ten models')
        result = api.list(maxResults=10, project=flags.project_id).execute()
        print('List results:')
        pprint.pprint(result)

        # Start training request on a data set.
        print_header('Submitting model training request')
        body = {'id': flags.model_id, 'storageDataLocation': flags.object_name}
        start = api.insert(body=body, project=flags.project_id).execute()
        print('Training results:')
        pprint.pprint(start)

        # Wait for the training to complete.
        print_header('Waiting for training to complete')
        while True:
            status = api.get(id=flags.model_id, project=flags.project_id).execute()
            state = status['trainingStatus']
            print('Training state: ' + state)
            if state == 'DONE':
                break
            elif state == 'RUNNING':
                time.sleep(SLEEP_TIME)
                continue
            else:
                raise Exception('Training Error: ' + state)

            # Job has completed.
            print('Training completed:')
            pprint.pprint(status)
            # Describe model.
            print_header('Fetching model description')
            result = api.analyze(id=flags.model_id, project=flags.project_id).execute()
            print('Analyze results:')
            pprint.pprint(result)

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run '
               'the application to re-authorize.')


def predict(argv):
    service, flags = autentication(argv)

    try:
            # Get access to the Prediction API.
        api = service.trainedmodels()

        # confusion matriz
        print_header('Fetching model description')
        result = api.analyze(id=flags.model_id, project=flags.project_id).execute()
        print('Analyze results:')
        pprint.pprint(result)

        # Make some predictions using the newly trained model.
        print_header('Making some predictions')
        sample_text = " Sample text to predict"
        body = {'input': {'csvInstance': [sample_text]}}
        result = api.predict(
            body=body, id=flags.model_id, project=flags.project_id).execute()
        print('Prediction results for "%s"...' % sample_text)
        pprint.pprint(result)

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize.')


def del_model(argv):

    service, flags = autentication(argv)

    try:
        # Get access to the Prediction API.
        api = service.trainedmodels()

        # Delete model.
        print_header('Deleting model')
        result = api.delete(id=flags.model_id, project=flags.project_id).execute()
        print('Model deleted.')

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize.')

if __name__ == '__main__':
    if 'train' in sys.argv:
        sys.argv.pop(1)
        train_model(sys.argv)
    elif 'predict' in sys.argv:
        sys.argv.pop(1)
        predict(sys.argv)
    elif 'del' in sys.argv:
        sys.argv.pop(1)
        del_model(sys.argv)
