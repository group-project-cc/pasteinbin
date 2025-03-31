from flask import Flask

app = Flask(__name__)

# Get rid of this
@app.route('/')
def root():
    return '<h1>Hello World!</h1>'

# Write endpoints here!
# Examples: signup / login / logout / createPaste / getPaste / deletePaste ...
