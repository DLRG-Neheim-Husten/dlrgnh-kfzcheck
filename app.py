from flask import Flask
from flask import jsonify
from flask import Response
from flask import request
from flask_restx import Resource, Api

import logging
import re

CORS_CHECK_ENABLED = False

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


AZURE_PAGE = 'https://kfzcheck-dlrgnh.azurewebsites.net/'

allowedCorsDomains = set(())
allowedCorsDomains.add('https://neheim.dlrg.de')
allowedCorsDomains.add(AZURE_PAGE)
allowedCorsDomains.add('https://localhost')
allowedCorsDomains.add('http://localhost')

class AccessForbiddenException(Exception):
    pass

@app.errorhandler(AccessForbiddenException)
def handle_exception(err):
    response = {
        'message': err.message
    }

    return jsonify(response), 403

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

        try:
            headerOrigin = self.loadValidatedOriginForCorsRequest()
        except AccessForbiddenException as err:  
            return Response(err, 403)

        resp = self.createResponseFromData(kennzeichen)
        if headerOrigin is None:
            resp.headers['Access-Control-Allow-Origin'] = 'https://*'            
        else:
            resp.headers['Access-Control-Allow-Origin'] = headerOrigin
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

    def loadValidatedOriginForCorsRequest(self):

        headers = request.headers
        
        if CORS_CHECK_ENABLED:
            
            if 'Origin' not in headers:
                raise AccessForbiddenException("Missing 'Origin' header in request")

            headerOrigin = request.headers['Origin']

            if headerOrigin.empty() or headerOrigin not in allowedCorsDomains:
                raise AccessForbiddenException("'Origin' not in %s" % str(allowedCorsDomains))
        else:
            if 'Origin' not in headers:
                return None
            else:
                headerOrigin = request.headers['Origin']

        return headerOrigin

if __name__ == '__main__':
    app.run(debug=False)