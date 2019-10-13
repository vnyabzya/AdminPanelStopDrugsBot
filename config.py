import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgres://amxnmtxqianmev:3163811c5a7fdb992ba3a8384bc69eac1302dbf71e021555ec0c886cf1c8baf3@ec2-54-75-224-168.eu-west-1.compute.amazonaws.com:5432/d2r6bgh60bm8hh'
    SECRET_KEY = "powerful secretkey"
    POSTS_PER_PAGE = 20
    SQLALCHEMY_TRACK_MODIFICATIONS = True
    TOKEN = os.environ.get('TOKEN')
    LINK = os.environ.get('LINK')