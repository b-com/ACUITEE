# main.py – Software ACUITEE
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

from application import app
from gevent.pywsgi import WSGIServer

# for production deployment, use gevent server
if __name__ == '__main__':
    cert_file = app.config['CERT_FILE']
    key_file = app.config['KEY_FILE']
    print('Serving on 5000...')
    if cert_file == '' or key_file == '':
        WSGIServer(('0.0.0.0', 5000), app).serve_forever()
    else:
        WSGIServer(('0.0.0.0', 5000), app, certfile=cert_file, keyfile=key_file).serve_forever()
    