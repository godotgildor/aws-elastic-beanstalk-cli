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

import glob


def find_language_type():
    # Docker could be any language, so we need to check for docker first
    if smells_of_docker():
        return 'Docker'

    if smells_of_python():
        return 'Python'
    if smells_of_ruby():
        return 'Ruby'
    if smells_of_php():
        return 'PHP'
    if smells_of_node_js():
        return 'Node.js'
    if smells_of_iis():
        return 'IIS'
    if smells_of_tomcat():
        return 'Tomcat'

    return None


def smells_of_docker():
    """
    True if the current directory has a docker file
    'Dockerfile' should exist in the root directory
    """
    return _contains_file_types('Dockerfile')


def smells_of_python():
    """
    True if directory has a .py file or a requirements.txt file
    """
    return _contains_file_types('*.py', 'requirements.txt')


def smells_of_ruby():
    """
    True if directory has a .rb file or a Gemfile
    """
    return _contains_file_types('*.rb', 'Gemfile')


def smells_of_php():
    """
    True if directory has a .php file
    """
    return _contains_file_types('*.php')


def smells_of_node_js():
    """
    JS files are too comon in web apps, so instead we just look for the package.json file
    True is directory has a package.json file
    """
    return _contains_file_types('package.json')


def smells_of_iis():
    """
    True if directory contains a systemInfo.xml
    """
    return _contains_file_types('systemInfo.xml')


def smells_of_tomcat():
    """
    True of directory has a jsp file or a WEB-INF directory
    """
    return _contains_file_types('*.jsp', 'WEB-INF')


def _get_file_list(*args):
    lst = []
    for a in args:
        lst = lst + glob.glob(a)
    return lst


def _contains_file_types(*args):
    lst = _get_file_list(*args)
    if lst:  # if not empty
        return True
    else:
        return False