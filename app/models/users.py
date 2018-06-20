from flask import current_app, flash
from werkzeug.security import generate_password_hash, check_password_hash
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature,SignatureExpired
from app.extensions import db, login_manager
from flask_login import UserMixin

from .post import Post


class User(UserMixin,db.Model):
    __tablename__='users'
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(32),nullable=False,unique=True)
    password_hash = db.Column(db.String(128),nullable=False)
    email = db.Column(db.String(64),nullable=False,unique=True)
    #是否激活
    confirm = db.Column(db.Boolean,default=False)

    # 头像
    icon = db.Column(db.String(64), default='default.jpg')
    # 在另一模型中添加一个反向引用
    # 参数1：关联的模型名
    # backref：在关联的模型中动态添加的字段
    # 加载方式：dynamic，不加载，但是提供记录的查询
    # 若使用一对一，添加uselist=Flase
    posts = db.relationship('Post', backref='user', lazy=True)

    # 收藏
    # secondary：指定关系表
    favorites = db.relationship('Post', secondary='collections',
                                backref=db.backref('users', lazy='dynamic'),
                                lazy='dynamic')
    # focus = db.relationship('User', secondary='focus',
    #                             backref=db.backref('focusid', lazy='dynamic'),
    #                             lazy='dynamic')
    #

    def __repr__(self):
        return self.username

    # 密码字段保护
    @property
    def password(self):
        raise AttributeError('密码是不可读属性')

    # 设置密码，加密存储
    @password.setter
    def password(self, password):
        #相当于执行  user.password_hash=password
        self.password_hash = generate_password_hash(password)

        # 生成激活的token
    def generate_activate_token(self):
        # 创建用于生成token的类，需要传递秘钥和有效期expires_in默认=3600,expires_in=60
        s = Serializer(current_app.config['SECRET_KEY'])
        # 生成包含有效信息(必须是字典数据)的token字符串
        return s.dumps({'id': self.id})

    #生成任意的token
    @staticmethod
    def generate_token(dict):
        s = Serializer(current_app.config['SECRET_KEY'])
        # 生成包含有效信息(必须是字典数据)的token字符串
        return s.dumps(dict)
    #检查任意token是否有效,返回真实词典数据
    @staticmethod
    def check_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except SignatureExpired:
            flash('邮件已过期')
            return False
        except BadSignature:
            flash('无效的验证邮箱')
            return False
        return data

    # 账户激活，因为激活时还不知道是哪个用户
    @staticmethod
    def check_activate_token(token):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
            print(data)
        except SignatureExpired:
            flash('激活邮件已过期')
            return False
        except BadSignature:
            flash('无效的激活')
            return False
        user = User.query.get(data.get('id'))
        print(user)
        if not user:
            flash('激活的账户不存在')
            return False
        if not user.confirm:  # 没有激活才需要激活
            user.confirm = True
            db.session.add(user)
        return True

    # 密码的校验
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    #判断是否收藏
    def is_favorites(self,pid):
        #获取微博对象
        post = Post.query.get(pid)
        #判断微博是否在用户收藏列表中
        if post in self.favorites:
            #说明已经收藏
            return True
        else:
            return False

    # 收藏指定帖子
    def add_favorite(self, pid):
        p = Post.query.get(pid)
        self.favorites.append(p)

    # 取消收藏指定帖子
    def cancel_favorite(self, pid):
        p = Post.query.get(pid)
        self.favorites.remove(p)

    # # 判断是否收藏
    # def is_focus(self, uid):
    #     # 获取用户对象
    #     user =User.query.get(uid)
    #     # 判断是否关注对方
    #     if user in self.focus:
    #
    #         return True
    #     else:
    #         return False
    # #关注对方
    # def add_focus(self, uid):
    #     user = User.query.get(uid)
    #     self.favorites.append(user)
    #
    #
    # #取消关注
    # def cancel_focus(self, uid):
    #     user = User.query.get(uid)
    #     self.favorites.remove(user)

# 登录认证的回调，写在user model中
@login_manager.user_loader
def load_user(uid):
    return User.query.get(int(uid))



