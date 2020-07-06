from os import environ, path
from dotenv import load_dotenv


basedir = path.dirname(path.abspath(__file__))
load_dotenv(path.join(basedir, '.env'), verbose=True)

class Config:
    FLASK_DEBUG = environ.get('FLASK_DEBUG') or True
    FLASK_APP = environ.get('FLASK_APP') or 'run.py'
    FLASK_ENV = environ.get("FLASK_ENV") or 'development'
    SECRET_KEY = environ.get("SECRET_KEY") or 'a weird key'
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHMEY_DATABASE_URI') or 'sqlite:///site.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = environ.get('SQLALCHMEY_TRACK_MODIFICATIONS') or False
    CKEDITOR_HEIGHT = environ.get('CKEDITOR_HEIGHT') or 500
    CKEDITOR_FILE_UPLOADER = 'upload'
    CKEDITOR_IMAGE_PATH = path.join(basedir, 'images')
    CKEDITOR_SERVE_LOCAL = False
    

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'