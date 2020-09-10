from os import environ, path
from dotenv import load_dotenv


basedir = path.dirname(path.abspath(__file__))
load_dotenv(path.join(basedir, '.env'), verbose=True)

class Config:
    FLASK_DEBUG = environ.get('FLASK_DEBUG')
    FLASK_APP = environ.get('FLASK_APP')
    FLASK_ENV = environ.get("FLASK_ENV")
    SECRET_KEY = environ.get("SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = environ.get('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    MAIL_SERVER = environ.get('MAIL_SERVER')
    MAIL_PORT = 465
    MAIL_USE_SSL = True
    MAIL_USERNAME = environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = environ.get('MAIL_PASSWORD')
    CKEDITOR_HEIGHT = environ.get('CKEDITOR_HEIGHT') or 500
    CKEDITOR_FILE_UPLOADER = 'upload'
    CKEDITOR_IMAGE_PATH = path.join(basedir, 'images')
    CKEDITOR_SERVE_LOCAL = False
    

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'