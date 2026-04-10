from flask import Flask
from backend.api.routes import router_bp

app = Flask(__name__, template_folder='templates', static_folder='static')
app.register_blueprint(router_bp)

@app.route('/')
def index():
    return "Epidemic Router API is live."

if __name__ == '__main__':
    app.run(debug=True, port=5000)