import os
import logging

from flask import Flask, session, request
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_babel import Babel, get_locale


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)  # needed for url_for to generate with https

# configure the database, relative to the app instance folder
def get_database_config():
    """Configure database with fallback to SQLite if PostgreSQL fails"""
    database_url = os.environ.get("DATABASE_URL", "sqlite:///church_inventory.db")
    
    # If it's PostgreSQL, try to connect first before using it
    if database_url.startswith("postgresql://"):
        try:
            import psycopg2
            # Parse the connection URL
            from urllib.parse import urlparse
            parsed = urlparse(database_url)
            
            # Try a simple connection test
            test_conn = psycopg2.connect(
                host=parsed.hostname,
                port=parsed.port,
                database=parsed.path[1:],  # Remove leading slash
                user=parsed.username,
                password=parsed.password,
                connect_timeout=10
            )
            test_conn.close()
            
            # If successful, configure PostgreSQL settings
            app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
                "pool_recycle": 300,
                "pool_pre_ping": True,
                "pool_timeout": 20,
                "pool_size": 5,
                "max_overflow": 10,
                "connect_args": {
                    "connect_timeout": 30,
                    "application_name": "church_inventory"
                }
            }
            app.logger.info("PostgreSQL connection test successful")
            return database_url
            
        except Exception as e:
            app.logger.warning(f"PostgreSQL connection failed ({e}), falling back to SQLite")
            
    # Use SQLite as fallback
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {}
    return "sqlite:///church_inventory.db"

app.config["SQLALCHEMY_DATABASE_URI"] = get_database_config()

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

# Configure Babel for internationalization
app.config['LANGUAGES'] = {
    'en': 'English',
    'fr': 'Français',
    'ht': 'Kreyòl Ayisyen'
}
app.config['BABEL_DEFAULT_LOCALE'] = 'en'
app.config['BABEL_DEFAULT_TIMEZONE'] = 'UTC'

# Initialize Babel
def get_locale():
    # Check if user has selected a language
    if 'language' in session:
        return session['language']
    # Check URL parameter
    requested_language = request.args.get('lang')
    if requested_language in app.config['LANGUAGES']:
        session['language'] = requested_language
        return requested_language
    # Default to browser language or English
    return request.accept_languages.best_match(app.config['LANGUAGES'].keys()) or 'en'

babel = Babel(app, locale_selector=get_locale)

# initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    import routes  # noqa: F401

    db.create_all()
    app.logger.info(f"Database initialized successfully: {app.config['SQLALCHEMY_DATABASE_URI']}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
