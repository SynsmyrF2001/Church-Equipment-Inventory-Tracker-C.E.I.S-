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
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///church_inventory.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

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

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
