from flask import Flask
from flask import jsonify
from flask import Response
from flask import request
from flask_restx import Resource, Api

import logging
import re

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
api = Api(app)

file1 = open('./kennzeichen.txt', 'r')
Lines = file1.readlines()
file1.close()
app.data = dict()

for line in Lines:
    line = line.upper().rstrip()
    logging.debug(line)
    
    if re.match("^[A-Z][A-Z0-9 -_]+", line):
        key = re.sub(r'\W+', "", line)
        if key in app.data:
            app.data[key] = app.data[key] + " " + line
        else:
            app.data[key] = line

for key, value in app.data.items():
    logging.info(key + ": " + value)

@api.route("/query/<string:kennzeichen>")
@api.doc(params={'kennzeichen': '''
 Kennzeichen, nachdem gesucht wird. Case insensitive. Nicht alphanumerische
 Zeichen werden bei der Suche entfernt
'''}, )
class Kennzeichen(Resource):

    @api.doc(
        responses={
            200: 'Kennzeichen wurde gefunden. Body enthält die genau gespeicherten Kennzeichen.',
            204: 'Kennzeichen wurde nicht gefunden.',
            403: 'If Origin is not set, but required',
        },
        headers= {
            'Origin': 'Origin set by browser to determine if CORS request is allowed.'
        })
    def get(self, kennzeichen):
       
        resp = self.createResponseFromData(kennzeichen)
        self.allowCorsRequest(resp)
        return resp
    
    def createResponseFromData(self, kennzeichen):
        kennzeichenKey = kennzeichen.upper()
        kennzeichenKey = re.sub(r'\W+', "", kennzeichenKey)

        registeredKennzeichen = None
        status = 204
        result = dict()
        
        logging.debug("Query for '%s'" % kennzeichenKey)
        if kennzeichenKey in app.data:            
            registeredKennzeichen = app.data[kennzeichenKey]
            result['kennzeichen'] = registeredKennzeichen

            status = 200
        
        logging.debug("Status %s with %s" % (status, result))
        resp = jsonify(result)
        resp.status = status
        return resp

    def allowCorsRequest(self, resp):

        headers = request.headers    
        if 'Origin' in headers:
            headerOrigin = request.headers['Origin']
            resp.headers['Access-Control-Allow-Origin'] = headerOrigin
        
if __name__ == '__main__':
    app.run(debug=False)