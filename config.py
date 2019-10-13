import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
    SECRET_KEY = "powerful secretkey"
    POSTS_PER_PAGE = 9
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TOKEN = os.environ.get('TOKEN')
    LINK = os.environ.get('LINK')
    # TOKEN = '948992963:AAFMmH68bLI0nj7hpZsXkfNnhfYVKACcLOQ'
    SQLALCHEMY_DATABASE_URI = 'postgres://amxnmtxqianmev' \
                              ':3163811c5a7fdb992ba3a8384bc69eac1302dbf71e021555ec0c886cf1c8baf3@ec2-54-75-224-168.eu' \
                              '-west-1.compute.amazonaws.com:5432/d2r6bgh60bm8hh'
    # LINK = "https://stopnarko.herokuapp.com"
    REDIS_URL = os.environ.get('REDIS_URL') or 'redis://h' \
                                               ':p7cccf3c208d2383a7edaec3139ea735f184c6ba778de1b66a1e71c130692e6c4' \
                                               '@ec2-34-241-111-4.eu-west-1.compute.amazonaws.com:10349'
