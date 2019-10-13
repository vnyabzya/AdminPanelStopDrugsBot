import os
import urllib

import redis
import requests
import telebot
from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_wtf import FlaskForm
from rq import Queue
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from telebot import types
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms import SelectMultipleField, widgets, StringField, SubmitField, BooleanField, PasswordField
from wtforms.validators import DataRequired

from config import Config
from flask_login import LoginManager, UserMixin, current_user, login_user, login_required, logout_user


class UrlShortenTinyurl:
    URL = "http://tinyurl.com/api-create.php"

    def shorten(self, url_long):
        try:
            url = self.URL + "?" \
                  + urllib.parse.urlencode({"url": url_long})
            res = requests.get(url)
            if res.status_code == 200:
                return res.text
            else:
                return None

        except Exception as e:
            raise


app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
TOKEN = app.config.get('TOKEN')
bot = telebot.TeleBot(TOKEN)
migrate = Migrate(app, db)
LINK = app.config.get('LINK')
redis_url = app.config.get('REDIS_URL')
conn = redis.from_url(redis_url)
queue = Queue(connection=conn)
login = LoginManager(app)
login.login_view = 'login'
obj = UrlShortenTinyurl()


@login.user_loader
def load_user(user_id):
    return Admin.query.get(int(user_id))


users__telegram_shops = db.Table('users__telegram_shops',
                                 db.Column('users_id', db.Integer, db.ForeignKey('users.id')),
                                 db.Column('telegram_shops_id', db.Integer, db.ForeignKey('telegram_shops.id')),
                                 db.UniqueConstraint('users_id', 'telegram_shops_id')
                                 )

regions__telegram_shops = db.Table('regions__telegram_shops',
                                   db.Column('regions_id', db.Integer, db.ForeignKey('regions.id')),
                                   db.Column('telegram_shops_id', db.Integer, db.ForeignKey('telegram_shops.id')),
                                   db.UniqueConstraint('regions_id', 'telegram_shops_id')
                                   )


def gen_inline_keyboard(items):
    inline_keyboard = types.InlineKeyboardMarkup(row_width=1)
    button_items = []
    for item in items:
        button_items.append(types.InlineKeyboardButton(item.get('text'), callback_data=item.get('value')))
    inline_keyboard.row(*button_items)
    return inline_keyboard


class Region(db.Model):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True)
    telegram_shops = relationship(
        "TelegramShop",
        secondary=regions__telegram_shops,
        back_populates="regions")


class Admin(UserMixin, db.Model):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, unique=True)
    user = relationship("User", uselist=False, back_populates="admin")
    username = db.Column(db.String(64), index=True, unique=True)
    email = db.Column(db.String(120), index=True, unique=True)
    password_hash = db.Column(db.String(128))
    rule = Column(String)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Image(db.Model):
    __tablename__ = 'images'
    id = Column(Integer, primary_key=True, unique=True)
    photo_id = Column(Text, unique=True)


class User(db.Model):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, unique=True)
    user_name = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    activist = Column(Boolean, default=False)
    create_shops = relationship("Shop", back_populates="user")
    admin = relationship("Admin", back_populates="user")
    admin_id = Column(Integer, ForeignKey('admins.id'))
    inviter = relationship("User", remote_side='User.id', back_populates="invited_users")
    inviter_id = Column(Integer, ForeignKey('users.id'))
    invited_users = relationship("User", back_populates="inviter")
    report_telegram_shops = relationship(
        "TelegramShop",
        secondary=users__telegram_shops,
        back_populates="users_telegram_shops")

    def __init__(self, user):
        self.id = user.id
        self.user_name = user.username
        self.first_name = user.first_name
        self.last_name = user.last_name


class TelegramShop(db.Model):
    __tablename__ = 'telegram_shops'
    id = Column(Integer, primary_key=True)
    telegram_link = Column(String, unique=True)
    shop_id = Column(Integer, ForeignKey('shops.id'))
    shop = relationship("Shop", back_populates="telegram_shop")
    block_id = Column(Integer, ForeignKey('blocks.id'))
    block = relationship("Block", back_populates="telegram_shops")
    hide = Column(Boolean, default=True)
    valid = Column(Boolean, default=True)

    users_telegram_shops = relationship(
        "User",
        secondary=users__telegram_shops,
        back_populates="report_telegram_shops")

    regions = relationship(
        "Region",
        secondary=regions__telegram_shops,
        back_populates="telegram_shops")

    def publish_telegram_shop(self):
        job = queue.enqueue_call(
            func=self.add_and_send_new_link, result_ttl=5000
        )
        return job

    def get_mailto_link(self):
        subject = urllib.parse.quote('Drugs Sales')
        body = urllib.parse.quote(
            'Please block this channel: {} in connection with the distribution and sale of drugs'.format(
                self.telegram_link))
        return "mailto:{}?subject={}&body={}".format(
            'abuse@telegram.org', subject, body
        )

    def add_and_send_new_link(self):
        try:
            short_link = obj.shorten(self.get_mailto_link())
        except Exception as error:
            short_link = None
            print(error)
        for user in User.query.filter(User.activist == True).all():
            try:
                bot.send_message(user.id, '👨‍💻 Друже, просимо залишити скаргу про цю адресу, що використовують нарко'
                                          'зловмисники!\n\nℹ️ Перейдіть за посиланням, натисніть "Поскаржитись" ==> '
                                          'оберіть пункт "Інше" ==> введіть "Drug Sales" ==> '
                                          'натисніть ✅\n"{}"'.format(self.telegram_link))
                if short_link:
                    user.send_message(text="Також Ви можете надіслати скаргу на цей бот/канал/чат/користувача на пошту "
                                           "адміністрації Telegram (додавайте до листа скріншоти, як доказ), "
                                           "для цього натисність <a href='{}'>Відправити лист</a>".format(short_link),
                                      parse_mode="HTML")
                bot.send_message(user.id, text='А ти вже поскаржився?', reply_markup=gen_inline_keyboard(
                    [{'text': 'Так ✅',
                      'value': 'reported_{}'.format(self.id)}]))
            except Exception as error:
                continue


class WebAddress(db.Model):
    __tablename__ = 'web_addresses'
    id = Column(Integer, primary_key=True)
    url_address = Column(String, unique=True)
    shop_id = Column(Integer, ForeignKey('shops.id'))
    shop = relationship("Shop", back_populates="web_address")


class Block(db.Model):
    __tablename__ = 'blocks'
    id = Column(Integer, primary_key=True)
    telegram_shops = relationship("TelegramShop", back_populates="block")
    time_stamp = Column(DateTime, default=func.now())


class Address(db.Model):
    __tablename__ = 'addresses'
    id = Column(Integer, primary_key=True)
    address = Column(Text, unique=True)
    location = relationship("Location", back_populates="addresses")
    location_id = Column(Integer, ForeignKey('locations.id'))
    shop_id = Column(Integer, ForeignKey('shops.id'))
    shop = relationship("Shop", back_populates="address")


class Location(db.Model):
    __tablename__ = 'locations'
    id = Column(Integer, primary_key=True)
    latitude = Column(String, unique=True)
    longitude = Column(String, unique=True)
    addresses = relationship("Address", back_populates="location")


class Shop(db.Model):
    __tablename__ = 'shops'
    id = Column(Integer, primary_key=True)
    checked_by_admin = Column(Boolean, default=False)
    user = relationship("User", back_populates="create_shops")
    user_id = Column(Integer, ForeignKey('users.id'))
    telegram_shop = relationship("TelegramShop", uselist=False, back_populates="shop")
    web_address = relationship("WebAddress", uselist=False, back_populates="shop")
    address = relationship("Address", uselist=False, back_populates="shop")


class MultiCheckboxField(SelectMultipleField):
    widget = widgets.TableWidget()
    option_widget = widgets.CheckboxInput()


class EditTelegramShopForm(FlaskForm):
    telegram_link = StringField('Ссылка на телеграм аккаунт', validators=[DataRequired()])
    regions = MultiCheckboxField('Label', coerce=int)
    checked_by_admin = BooleanField('Проверенно администратором', default=False)
    block = BooleanField('Заблокирован', default=False)
    hide = BooleanField('Скрытый', default=False)
    submit = SubmitField('Сохранить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить пароль')
    submit = SubmitField('Войти')


def get_progress():
    all_count = len(TelegramShop.query.filter(TelegramShop.valid == True).all())
    ready_count = len(Shop.query.filter(Shop.telegram_shop != None, Shop.checked_by_admin == True).all())
    return int(100 * ready_count / all_count)


@app.route('/edit_link/<telegram_shop_id>', methods=['GET', 'POST'])
@login_required
def edit_telegram_shop(telegram_shop_id):
    telegram_shop_obj = TelegramShop.query.get_or_404(telegram_shop_id)
    form = EditTelegramShopForm()
    form.regions.choices = [(region.id, region.name) for region in Region.query.order_by(Region.name).all()]
    if form.validate_on_submit():
        # get our choices again, could technically cache these in a list if we wanted but w/e
        regions = Region.query.order_by(Region.name).all()
        # need a list to hold our choices
        accepted = []
        # looping through the choices, we check the choice ID against what was passed in the form
        for region in regions:
            # when we find a match, we then append the Choice object to our list
            if region.id in form.regions.data:
                accepted.append(region)
        # now all we have to do is update the users choices records
        telegram_shop_obj.regions = accepted
        telegram_shop_obj.telegram_link = form.telegram_link.data
        if telegram_shop_obj.shop:
            telegram_shop_obj.shop.checked_by_admin = form.checked_by_admin.data
        else:
            telegram_shop_obj.shop = Shop(checked_by_admin=form.checked_by_admin.data)
        if form.block.data and not telegram_shop_obj.block:
            telegram_shop_obj.block = Block()
        else:
            telegram_shop_obj.block = None
        telegram_shop_obj = form.hide.data
        try:
            db.session.commit()
            flash('Запись была изменена успешно')
        except:
            flash('Что-то пошло не так', category='danger')

        if 'url' in session:
            return redirect(session['url'])
        else:
            return redirect(url_for('index'))
    else:
        form.telegram_link.data = telegram_shop_obj.telegram_link
        form.regions.data = [region.id for region in telegram_shop_obj.regions]
        form.telegram_link.data = telegram_shop_obj.telegram_link
        if telegram_shop_obj.shop:
            form.checked_by_admin.data = telegram_shop_obj.shop.checked_by_admin
        else:
            form.checked_by_admin.data = False
        form.block.data = False if not telegram_shop_obj.block else True
        form.hide.data = telegram_shop_obj.hide
    return render_template('edit_profile.html', title='Edit Profile',
                           form=form, telegram_shop=telegram_shop_obj, progress=get_progress())


@app.route('/blocked/', methods=['GET', 'POST'])
@login_required
def blocked():
    regions = [dict(region=region.name, count=len(region.telegram_shops)) for region in
               Region.query.order_by(Region.name).all()]
    session['url'] = request.url
    page = request.args.get('page', 1, type=int)
    value = request.args.get('value', True)
    if value:
        telegram_shops = TelegramShop.query.filter(TelegramShop.block != None, TelegramShop.valid == True).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    else:
        telegram_shops = TelegramShop.query.filter(TelegramShop.block == None, TelegramShop.valid == True).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blocked', page=telegram_shops.next_num) \
        if telegram_shops.has_next else None
    prev_url = url_for('blocked', page=telegram_shops.prev_num) \
        if telegram_shops.has_prev else None
    return render_template("index.html", title='Заблокированые', telegram_shops=telegram_shops.items, next_url=next_url,
                           prev_url=prev_url, regions=regions, progress=get_progress())


@app.route('/checked_by_admin/', methods=['GET', 'POST'])
@login_required
def checked_by_admin():
    regions = [dict(region=region.name, count=len(region.telegram_shops)) for region in
               Region.query.order_by(Region.name).all()]
    session['url'] = request.url
    page = request.args.get('page', 1, type=int)
    value = request.args.get('value', True)
    shops = Shop.query.filter(Shop.checked_by_admin == value, Shop.telegram_shop != None).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('checked_by_admin', page=shops.next_num, value=value) \
        if shops.has_next else shops
    prev_url = url_for('checked_by_admin', page=shops.prev_num, value=value) \
        if shops.has_prev else None
    return render_template("index.html", title='Проверены админом',
                           telegram_shops=[item.telegram_shop for item in shops.items], next_url=next_url,
                           prev_url=prev_url, regions=regions, progress=get_progress())


@app.route('/statistic/', methods=['GET', 'POST'])
@login_required
def statistic():
    regions = [dict(region=region.name, count=len(region.telegram_shops)) for region in
               Region.query.order_by(Region.name).all()]
    return render_template("_statistic.html", title='Статистика по регионам', regions=regions)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    regions = [dict(region=region.name, count=len(region.telegram_shops)) for region in
               Region.query.order_by(Region.name).all()]
    session['url'] = request.url
    page = request.args.get('page', 1, type=int)
    telegram_shops = TelegramShop.query(TelegramShop.valid == True).paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=telegram_shops.next_num) \
        if telegram_shops.has_next else None
    prev_url = url_for('index', page=telegram_shops.prev_num) \
        if telegram_shops.has_prev else None
    return render_template("index.html", title='Все записи', telegram_shops=telegram_shops.items, next_url=next_url,
                           prev_url=prev_url, regions=regions, progress=get_progress())


@app.route('/delete/<telegram_id>', methods=['GET', 'POST'])
@login_required
def delete(telegram_id):
    TelegramShop.query.filter(TelegramShop.id == telegram_id).delete()
    try:
        db.session.commit()
        flash('Запись была удалена успешно')
    except:
        flash('Что-то пошло не так', category='danger')
    if 'url' in session:
        return redirect(session['url'])
    else:
        return redirect(url_for('index'))


@app.route('/publish/<telegram_id>', methods=['GET', 'POST'])
@login_required
def publish(telegram_id):
    telegram = TelegramShop.query.filter(TelegramShop.id == telegram_id).first()
    try:
        telegram.publish_telegram_shop()
        flash('Запись была опубликована успешно')
    except:
        flash('Что-то пошло не так', category='danger')
    if 'url' in session:
        return redirect(session['url'])
    else:
        return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        admin = Admin.query.filter_by(username=form.username.data).first()
        if admin is None or not admin.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(admin, remember=form.remember_me.data)
        return redirect(url_for('index'))
    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
