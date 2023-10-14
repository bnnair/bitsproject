from flask import Flask, Response, url_for
from waitress import serve

from datetime import datetime
import time
import json

app = Flask(__name__)

@app.route('/sse')
def sse():
    return '''
    <html>
    <head>
    </head>
    <body>
        <div id="event"></div>
        <script type="text/javascript">
        var eventElement = document.getElementById("event");
        var evtSource = new EventSource("/demosse");
        evtSource.onmessage = function(e) {
            eventElement.innerHTML = e.data;
        }
        </script>
    </body>
    </html>
    '''

@app.route('/demosse')
def demosse():
    def temp():
        date = str(datetime.now())
        print(date)
        yield('data: %s\n\n' % date)
        time.sleep(5)
    return Response(temp(), mimetype="text/event-stream")

if __name__ == '__main__':
    serve(app, port=10081)