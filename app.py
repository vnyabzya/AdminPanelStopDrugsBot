from flask import Flask, request, render_template, url_for, redirect, flash, session
from flask_wtf import FlaskForm
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, func, Text
from sqlalchemy.orm import relationship
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from wtforms import SelectMultipleField, widgets, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

from config import Config

app = Flask(__name__)
app.config.from_object(Config)
db = SQLAlchemy(app)
migrate = Migrate(app, db)
TOKEN = app.config.get('TOKEN')
LINK = app.config.get('LINK')

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


class Region(db.Model):
    __tablename__ = 'regions'
    id = Column(Integer, primary_key=True, unique=True)
    name = Column(String, unique=True)
    telegram_shops = relationship(
        "TelegramShop",
        secondary=regions__telegram_shops,
        back_populates="regions")


class Admin(db.Model):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True, unique=True)
    users = relationship("User", back_populates="admin")
    rule = Column(String)


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
    admin = relationship("Admin", back_populates="users")
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

    users_telegram_shops = relationship(
        "User",
        secondary=users__telegram_shops,
        back_populates="report_telegram_shops")

    regions = relationship(
        "Region",
        secondary=regions__telegram_shops,
        back_populates="telegram_shops")


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


@app.route('/edit_link/<telegram_shop_id>', methods=['GET', 'POST'])
def edit_telegram_shop(telegram_shop_id):
    telegram_shop_obj = TelegramShop.query.get_or_404(telegram_shop_id)
    form = EditTelegramShopForm()
    form.regions.choices = [(region.id, region.name) for region in Region.query.all()]
    if form.validate_on_submit():
        # get our choices again, could technically cache these in a list if we wanted but w/e
        regions = Region.query.all()
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
                           form=form, telegram_shop=telegram_shop_obj)


@app.route('/blocked/', methods=['GET', 'POST'])
def blocked():
    session['url'] = request.url
    page = request.args.get('page', 1, type=int)
    value = request.args.get('value', True)
    if value:
        telegram_shops = TelegramShop.query.filter(TelegramShop.block != None).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    else:
        telegram_shops = TelegramShop.query.filter(TelegramShop.block == None).paginate(
            page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('blocked', page=telegram_shops.next_num) \
        if telegram_shops.has_next else None
    prev_url = url_for('blocked', page=telegram_shops.prev_num) \
        if telegram_shops.has_prev else None
    return render_template("index.html", title='Заблокированые', telegram_shops=telegram_shops.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/checked_by_admin/', methods=['GET', 'POST'])
def checked_by_admin():
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
                           prev_url=prev_url)


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    session['url'] = request.url
    page = request.args.get('page', 1, type=int)
    telegram_shops = TelegramShop.query.paginate(
        page, app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('index', page=telegram_shops.next_num) \
        if telegram_shops.has_next else None
    prev_url = url_for('index', page=telegram_shops.prev_num) \
        if telegram_shops.has_prev else None
    return render_template("index.html", title='Все записи', telegram_shops=telegram_shops.items, next_url=next_url,
                           prev_url=prev_url)


@app.route('/delete/<telegram_id>', methods=['GET', 'POST'])
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


if __name__ == '__main__':
    app.run(host='192.168.1.6')
