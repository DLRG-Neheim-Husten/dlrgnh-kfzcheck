from flask import Flask
from flask import Response
from flask import jsonify
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
        })
    def get(self, kennzeichen):
        queryKennzeichen = kennzeichen.upper()
        queryKennzeichen = re.sub(r'\W+', "", queryKennzeichen)
        
        registeredKennzeichen = None
        status = 204
        result = dict()
        
        logging.debug("Query for '%s'" % queryKennzeichen)
        if queryKennzeichen in app.data:            
            registeredKennzeichen = app.data[queryKennzeichen]
            result['kennzeichen'] = registeredKennzeichen

            status = 200
        
        logging.debug("Status %s with %s" % (status, result))
        return result, status
        #return Response(result, status=status, mimetype='application/json')
        

if __name__ == '__main__':
    app.run(debug=False)