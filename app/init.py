import os
from flask import Flask


def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'your-secret-key')

    from app.blog.routes import blog_bp
    app.register_blueprint(blog_bp)

    return app
