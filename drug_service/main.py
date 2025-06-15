import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.drug.resolves import drug_query, drug_mutation
from database import initialize_drug_database, init_db # Import fungsi inisialisasi

from flask import Flask, send_file, request, jsonify, send_from_directory
from ariadne import load_schema_from_path, make_executable_schema, graphql_sync

app = Flask(__name__, static_folder='.')

# Panggil inisialisasi database saat aplikasi dimulai
initialize_drug_database()
init_db()

# Load GraphQL schema
schema_path = "schema.graphql" # Sesuaikan jika nama/lokasi file skema berbeda
type_defs = load_schema_from_path(schema_path)

# Create executable schema
schema = make_executable_schema(type_defs, drug_query, drug_mutation)

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

# GraphQL endpoint (POST for query/mutation)
@app.route("/graphql", methods=["POST"])
def graphql_server():
    data = request.get_json()
    success, result = graphql_sync(
        schema,
        data,
        context_value=request,
        debug=app.debug
    )
    status_code = 200 if success else 400
    return jsonify(result), status_code

# GraphQL Playground (GET for interactive interface)
@app.route("/graphql", methods=["GET"])
def graphql_playground():
    # Note: For production, you might want to disable or secure this.
    # return GraphQLPlaygroundHTML(endpoint="/graphql"), 200 # If you prefer the built-in playground
    return send_from_directory(app.static_folder, 'playground.html')

if __name__ == '__main__':
    print("Attempting to run Flask app for drug_service...")
    app.run(debug=True, host='0.0.0.0', port=5005) 