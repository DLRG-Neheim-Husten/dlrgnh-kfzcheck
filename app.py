from flask import Flask

app = Flask(__name__)

file1 = open('kennzeichen.txt', 'r')
Lines = file1.readlines()
file1.close()
s = set(())

for line in Lines:
    s.add(line)

@app.route("/")
def hello_world():
    kennzeichen = request.args.get('kennzeichen')
    return kennzeichen is not None and kennzeichen in s
