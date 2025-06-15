from flask import Flask, render_template, request, jsonify
from flask_graphql import GraphQLView
from schema import schema
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

tracking_data = []

@app.route('/tracking', methods=['POST'])
def tracking():
    data = request.json
    print("Received tracking data:", data)
    tracking_data.append(data)
    return jsonify({"message": "Tracking received"}), 200

@app.route('/api/tracking', methods=['GET'])
def get_tracking():
    return jsonify(tracking_data)

# Add GraphQL endpoint
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=schema,
        graphiql=True  # Enable GraphiQL interface
    )
)

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, port=5004) 