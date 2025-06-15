from flask import Flask, render_template, request, jsonify
from flask_graphql import GraphQLView
from flask_cors import CORS
from schema import schema
from database import init_db


app = Flask(__name__, template_folder='frontend')
CORS(app)

@app.before_request
def log_request_info():
    if request.path == '/graphql' and request.method == 'POST':
        print(f"[payment_service] Menerima POST request ke /graphql:")
        print(f"[payment_service] Headers: {request.headers}")
        print(f"[payment_service] Data: {request.get_data()}")

@app.errorhandler(400)
def bad_request_error(e):
    print(f"[payment_service] ERROR 400 Bad Request: {e}")
    print(f"[payment_service] Request data: {request.get_data()}")
    import traceback; traceback.print_exc()
    return jsonify({"errors": [{"message": str(e)}]}), 400

@app.errorhandler(500)
def internal_server_error(e):
    print(f"[payment_service] ERROR 500 Internal Server Error: {e}")
    return jsonify({"errors": [{"message": "Internal Server Error"}]}), 500

app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True
    )
)

@app.route('/')
def index():
    orders = []
    return render_template('index.html', orders=orders)

if __name__ == '__main__':
    init_db()
    app.run(debug=True, host='0.0.0.0', port=5003) 