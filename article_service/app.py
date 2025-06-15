from flask import Flask, render_template, g
from flask_graphql import GraphQLView
import graphene
import sqlite3
import click
from services.article.database import get_db, close_db

app = Flask(__name__)

# Register close_db to be called after each request
app.teardown_appcontext(close_db)

# Add a CLI command to initialize the database
@app.cli.command('init-db')
def init_db_command():
    "Clear existing data and create new tables."
    from services.article.init_db import init_db
    init_db()
    click.echo('Initialized the article database.')

class Article(graphene.ObjectType):
    id = graphene.Int()
    title = graphene.String()
    content = graphene.String()
    author = graphene.String()
    createdAt = graphene.String()
    updatedAt = graphene.String()

class ArticleInput(graphene.InputObjectType):
    title = graphene.String(required=True)
    content = graphene.String(required=True)
    author = graphene.String(required=True)

class CreateArticle(graphene.Mutation):
    class Arguments:
        article_data = ArticleInput(required=True)

    Output = Article

    def mutate(root, info, article_data):
        db = get_db()
        try:
            cursor = db.execute(
                "INSERT INTO articles (title, content, author) VALUES (?, ?, ?)",
                (article_data.title, article_data.content, article_data.author)
            )
            db.commit()
            article_id = cursor.lastrowid
            new_article_row = db.execute(
                "SELECT * FROM articles WHERE id = ?",
                (article_id,)
            ).fetchone()
            # Map snake_case from DB to camelCase for Graphene object
            return Article(
                id=new_article_row['id'],
                title=new_article_row['title'],
                content=new_article_row['content'],
                author=new_article_row['author'],
                createdAt=new_article_row['created_at'],
                updatedAt=new_article_row['updated_at']
            )
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to create article: {e}")
        finally:
            close_db()

class UpdateArticle(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)
        article_data = ArticleInput(required=True)

    Output = Article

    def mutate(root, info, id, article_data):
        db = get_db()
        try:
            db.execute(
                """UPDATE articles 
                   SET title = ?, content = ?, author = ?, 
                       updated_at = CURRENT_TIMESTAMP
                   WHERE id = ?""",
                (article_data.title, article_data.content, article_data.author, id)
            )
            db.commit()
            updated_article_row = db.execute(
                "SELECT * FROM articles WHERE id = ?",
                (id,)
            ).fetchone()
            if updated_article_row:
                # Map snake_case from DB to camelCase for Graphene object
                return Article(
                    id=updated_article_row['id'],
                    title=updated_article_row['title'],
                    content=updated_article_row['content'],
                    author=updated_article_row['author'],
                    createdAt=updated_article_row['created_at'],
                    updatedAt=updated_article_row['updated_at']
                )
            raise Exception("Article not found")
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to update article: {e}")
        finally:
            close_db()

class DeleteArticle(graphene.Mutation):
    class Arguments:
        id = graphene.Int(required=True)

    success = graphene.Boolean()

    def mutate(root, info, id):
        db = get_db()
        try:
            db.execute("DELETE FROM articles WHERE id = ?", (id,))
            db.commit()
            return DeleteArticle(success=True)
        except Exception as e:
            db.rollback()
            raise Exception(f"Failed to delete article: {e}")
        finally:
            close_db()

class Query(graphene.ObjectType):
    articles = graphene.List(Article)
    article = graphene.Field(Article, id=graphene.Int(required=True))

    def resolve_articles(root, info):
        db = get_db()
        articles_rows = db.execute("SELECT * FROM articles ORDER BY created_at DESC").fetchall()
        close_db()
        return [Article(
            id=row['id'],
            title=row['title'],
            content=row['content'],
            author=row['author'],
            createdAt=row['created_at'],
            updatedAt=row['updated_at']
        ) for row in articles_rows]

    def resolve_article(root, info, id):
        db = get_db()
        article_row = db.execute("SELECT * FROM articles WHERE id = ?", (id,)).fetchone()
        close_db()
        if article_row:
            return Article(
                id=article_row['id'],
                title=article_row['title'],
                content=article_row['content'],
                author=article_row['author'],
                createdAt=article_row['created_at'],
                updatedAt=article_row['updated_at']
            )
        return None

class Mutation(graphene.ObjectType):
    create_article = CreateArticle.Field()
    update_article = UpdateArticle.Field()
    delete_article = DeleteArticle.Field()

schema = graphene.Schema(query=Query, mutation=Mutation)

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
    return render_template('index.html')

@app.route('/articles/<int:article_id>')
def article_detail(article_id):
    return render_template('article_detail.html', article_id=article_id)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=True)