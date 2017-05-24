# Copyright 2014 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You
# may not use this file except in compliance with the License. A copy of
# the License is located at
#
# http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is
# distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF
# ANY KIND, either express or implied. See the License for the specific
# language governing permissions and limitations under the License.

import unittest
from unittest.mock import Mock, MagicMock, patch

import botocore
import botocore.exceptions

from ebcli.lib import aws


class TestAws(unittest.TestCase):

    def setUp(self):
        self.response_data = {
            'ResponseMetadata': {
                    'HTTPStatusCode': 500
            },
            'Error': {
                    'Message': '500 Internal Server Error'
            }
        }

    def test_user_agent(self):
        aws.set_region('us-east-1')
        client = aws._get_client('elasticbeanstalk')
        user_agent = client._endpoint._user_agent
        self.assertTrue(user_agent.startswith('eb-cli'))


    def test_handle_response_code__500x_code__max_attempts_reached(self):
        aggregated_response_message = [r"""Received 5XX error during attempt #11
   500 Internal Server Error
"""]

        with self.assertRaises(aws.MaxRetriesError) as context_manager:
            aws._handle_response_code(self.response_data, 11, aggregated_response_message)
 
        self.assertEqual(context_manager.exception.message,
               "Max retries exceeded for service error (5XX)\n" + ('\n').join(aggregated_response_message))


    @patch('ebcli.lib.aws.LOG')
    def test_handle_response_code__500x_code__max_attempts_not_reached(self, LOG):
        aggregated_response_message = []

        LOG.debug.assert_called_with_once(
             "{'Error': {'Message': '500 Internal Server Error'}, 'ResponseMetadata': {'HTTPStatusCode': 500}}")
        LOG.debug.assert_called_with_once('API call finished, status = 500')
        LOG.debug.assert_called_with_once('Received 5xx error')

        aws._handle_response_code(self.response_data, 10, aggregated_response_message)

    def test_make_api_call__failure__status_code_5xx(self):
        self.maxDiff = None
        expected_response = {'500'}

        operation = MagicMock()
        operation.side_effect = botocore.exceptions.ClientError(self.response_data, 'some_operation')

        aws._set_operation = MagicMock(return_value=operation)
        aws._get_delay = MagicMock(return_value=0)

        with self.assertRaises(aws.MaxRetriesError) as cm:
            aws.make_api_call('some_service', 'some_operation')

        exception_message = r"""Max retries exceeded for service error (5XX)
Received 5XX error during attempt #1
   500 Internal Server Error

Received 5XX error during attempt #2
   500 Internal Server Error

Received 5XX error during attempt #3
   500 Internal Server Error

Received 5XX error during attempt #4
   500 Internal Server Error

Received 5XX error during attempt #5
   500 Internal Server Error

Received 5XX error during attempt #6
   500 Internal Server Error

Received 5XX error during attempt #7
   500 Internal Server Error

Received 5XX error during attempt #8
   500 Internal Server Error

Received 5XX error during attempt #9
   500 Internal Server Error

Received 5XX error during attempt #10
   500 Internal Server Error

Received 5XX error during attempt #11
   500 Internal Server Error
"""

        self.assertEqual(
            exception_message,
            str(cm.exception)
        )