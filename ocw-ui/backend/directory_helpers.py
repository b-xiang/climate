#
#  Licensed to the Apache Software Foundation (ASF) under one or more
#  contributor license agreements.  See the NOTICE file distributed with
#  this work for additional information regarding copyright ownership.
#  The ASF licenses this file to You under the Apache License, Version 2.0
#  (the "License"); you may not use this file except in compliance with
#  the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

''' Endpoints for retrieving directory information from the server. '''

from bottle import Bottle, request, route
import os
import json
import re
import sys

dir_app = Bottle()

PATH_LEADER = "/usr/local/rcmes"

@dir_app.route('/list/<dir_path:path>')
def get_directory_info(dir_path):
    ''''''
    try:
        clean_path = _get_clean_directory_path(PATH_LEADER, dir_path)
        dir_listing = os.listdir(clean_path)
    except:
        # ValueError - dir_path couldn't be 'cleaned'
        # OSError - clean_path is not a directory
        dir_info = []
    else:
        dir_info = []
        for obj in dir_listing:
            # Ignore hidden files
            if obj[0] == '.': continue

            # Create a path to the listed object. If it's a directory add a
            # trailing slash as a visual clue. Then strip out the path leader.
            obj = os.path.join(clean_path, obj)
            if os.path.isdir(obj): obj = obj + '/'
            dir_info.append(obj.replace(PATH_LEADER, ''))

        sorted(dir_info, key=lambda s: s.lower())

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, return_json)
    return return_json

WORK_DIR = "/tmp/rcmet"

@dir_app.route('/getResultDirInfo')
def getResultDirInfo():
    dirPath = WORK_DIR
    dirPath = dirPath.replace('/../', '/')
    dirPath = dirPath.replace('/./', '/')

    if os.path.isdir(dirPath):
        listing = os.listdir(dirPath)
        directories=[d for d in os.listdir(os.getcwd()) if os.path.isdir(d)]
        listingNoHidden = [f for f in listing if f[0] != '.']
        joinedPaths = [os.path.join(dirPath, f) for f in listingNoHidden]
        onlyDirs = [f for f in joinedPaths if os.path.isdir(f)]
        finalPaths = [p.replace(WORK_DIR, '') for p in onlyDirs]
        sorted(finalPaths, key=lambda s: s.lower())
        returnJSON = finalPaths
    else:
        returnJSON = []

    returnJSON = json.dumps(returnJSON)
    if request.query.callback:
        return "%s(%s)" % (request.query.callback, returnJSON)
    else:
        return returnJSON

@dir_app.route('/getResults/<dirPath:path>')
def getResults(dirPath):
    dirPath = WORK_DIR + dirPath
    dirPath = dirPath.replace('/../', '/')
    dirPath = dirPath.replace('/./', '/')

    if os.path.isdir(dirPath):
        listing = os.listdir(dirPath)
        listingNoHidden = [f for f in listing if f[0] != '.']
        joinedPaths = [os.path.join(dirPath, f) for f in listingNoHidden]
        onlyFilesNoDirs = [f for f in joinedPaths if os.path.isfile(f)]
        finalPaths = [p.replace(WORK_DIR, '') for p in onlyFilesNoDirs]
        sorted(finalPaths, key=lambda s: s.lower())
        returnJSON = finalPaths
    else:
        returnJSON = []

    returnJSON = json.dumps(returnJSON)
    if request.query.callback:
        return "%s(%s)" % (request.query.callback, returnJSON)
    else:
        return returnJSON

@dir_app.route('/getPathLeader/')
def getPathLeader():
    returnJSON = {"leader": PATH_LEADER}

    if request.query.callback:
        return "%s(%s)" % (request.query.callback, returnJSON)
    else:
        return returnJSON

def _get_clean_directory_path(path_leader, dir_path):
    ''''''
    # Strip out any .. or . relative directories and remove duplicate slashes
    dir_path = re.sub('/\.\./|/\.\.|/\./|/\.', '/', dir_path)
    dir_path = re.sub('//+', '/', dir_path)

    # Prevents the directory path from being a substring of the path leader.
    # os.path.join('/usr/local/rcmes', '/usr/local') gives '/usr/local'
    # which could allow access to unacceptable paths. This also means that
    if dir_path[0] == '/': dir_path = dir_path[1:]

    os.path.join(path_leader, dir_path)
    if not os.path.isdir(dir_path):
        cur_frame = sys._getframe().f_code
        err = "{}.{}: Create path is not a valid directory {}".format(
            cur_frame.co_filename,
            cur_frame.co_name,
            dir_path
        )
        raise ValueError(err)

    return dir_path
