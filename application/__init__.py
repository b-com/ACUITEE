# __init__.py – Software ACUITEE
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

from flask import Flask
from flask_session import Session
from config import Config
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
app.config.from_object(Config)

from application import routes 
