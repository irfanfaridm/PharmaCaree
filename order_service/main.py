from database import init_db
init_db()
from flask import Flask, request, jsonify, render_template
from flask_graphql import GraphQLView
import graphene
from database import db_session
from services.order.resolves import OrderResolves

app = Flask(__name__)
app.add_url_rule(
    '/graphql',
    view_func=GraphQLView.as_view(
        'graphql',
        schema=graphene.Schema(query=OrderResolves, mutation=OrderResolves),
        graphiql=True # Enable GraphiQL interface for easy testing
    )
)

@app.route('/')
def index():
    return render_template('index.html')

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002) 