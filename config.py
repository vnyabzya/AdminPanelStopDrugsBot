import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = "powerful secretkey"
    POSTS_PER_PAGE = 20
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TOKEN = os.environ.get('TOKEN')
    LINK = os.environ.get('LINK')
