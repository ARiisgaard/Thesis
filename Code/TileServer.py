import os.path
from flask import Flask, send_file
from flask_cors import CORS
app = Flask(__name__, static_url_path='/static')
CORS(app)

@app.route('/tiles/<zoom>/<y>/<x>', methods=['GET', 'POST'])
def tiles(zoom, y, x):
    # this is a blank tile, change to whatever you want
    default = os.path.expanduser('~') + '\\Desktop\\Data\\10\\0\\0.tiff' #TODO: I need a black tile
    # filename = os.path.expanduser('~') + '\\Desktop\\Data\\%s\\%s\\%s.tiff' % (zoom, x, y)
    filename = os.path.expanduser('~') + '\\Desktop\\Data\\tiles\\%s\\%s\\%s.tiff' % (zoom, x, y)
    if os.path.isfile(filename):
        return send_file(filename)
    else:
        return send_file(default)


@app.route('/', methods=['GET', 'POST'])
def index():
    return app.send_static_file('index.html')


@app.route("/hello")
def hello():
        return "Hello World!"


if __name__ == '__main__':
    app.run(debug=False, host='localhost', port=8080)
