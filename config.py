# config.py – Software ACUITEE
# Copyright 2021 b<>com. All rights reserved.
# This software is licensed under the Apache License, Version 2.0.
# You may not use this file except in compliance with the license. 
# You may obtain a copy of the license at: 
# http://www.apache.org/licenses/LICENSE-2.0 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, 
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and 
# limitations under the License.

import os

class Config(object):
    SECRET_KEY = os.environ.get('SECRET_KEY') or b'1\x11s\xfa\x83Y]\x9b\xb2\xd2\xff\x82\xe3\xa8F\xad'