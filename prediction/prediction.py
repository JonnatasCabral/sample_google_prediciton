#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2014 Google Inc. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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
  $ python prediction.py --logging_level=DEBUG
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


def trainmodel(argv):
    # If you previously ran this app with an earlier version of the API
    # or if you change the list of scopes below, revoke your app's permission
    # here: https://accounts.google.com/IssuedAuthSubTokens
    # Then re-run the app to re-authorize it.
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
            break
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

        # Make some predictions using the newly trained model.
        print_header('Making some predictions')
        sample_text = "  Julgado improcedente o pedido   Ante o exposto e por tudo mais que nos autos consta, JULGO IMPROCEDENTE o pedido constante da inicial, uma vez que o(a) autor(a) não conseguiu provar os fatos constitutivos de seu direito.Custas e honorários sucumbenciais pela parte autora, estes a base de 10% (dez por cento) sobre o valor da causa, observado o disposto no art. 12 da Lei 1.060/50.P.R.I.Após o trânsito em julgado, dê-se baixa na distribuição e arquive-se, observadas as formalidades legais, caso nada seja requestado." 
        body = {'input': {'csvInstance': [sample_text]}}
        result = api.predict(
            body=body, id=flags.model_id, project=flags.project_id).execute()
        print('Prediction results for "%s"...' % sample_text)
        pprint.pprint(result)

    except client.AccessTokenRefreshError:
        print ('The credentials have been revoked or expired, please re-run'
               'the application to re-authorize.')


def delmodel(argv):

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
    trainmodel(sys.argv)
