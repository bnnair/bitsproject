from flask import Flask, render_template
from flask_sse import sse
import time

app = Flask(__name__)

# Import the Redis client
import redis

# Define the Redis connection
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

app = Flask(__name__)
app.config["REDIS_URL"] = "redis://localhost/O"
app.register_blueprint(sse, url_prefix='/stream')

@app.route('/test-redis')
def test_redis_connection():
    try:
        # Check if the Redis server is reachable
        redis_client.ping()
        return "Redis connection is working."
    except redis.ConnectionError:
        return "Failed to connect to Redis server."


@app.route('/')
def index():
    return render_template("collection.html")

@app.route('/hello')
def publish_hello():
    while True:
        sse.publish({"message": "Hello!"}, type='greeting')
        time.sleep(50)
        # return "Message sent!"

if __name__ == '__main__':
    app.run(debug=True)
