import os

import time
from PIL import Image
from flask import Blueprint, flash, render_template, redirect, url_for, current_app, request, jsonify
from sqlalchemy import or_

from app.extensions import db
from app.forms import RegisterForm, LoginForm, UserPasswordForm, IconForm, EmailForm, EUForm, AuthCodeForm, \
    ResetPwdForm, CommentForm
from app.models import User, Post
from app.email import send_mail
from flask_login import login_user, logout_user, current_user
from app.extensions import photos

users = Blueprint('users', __name__)


@users.route('/register/', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data,
                    email=form.email.data)
        db.session.add(user)
        db.session.commit()
        # 发激活邮件
        # 生成一个token，令牌，包含失效，包含用户信息()
        token = user.generate_activate_token()
        send_mail([user.email], '激活邮件', 'email/activate', username=user.username, token=token)
        flash('注册成功')
        return redirect(url_for('users.login'))

    return render_template('users/register.html', form=form)


# 激活
@users.route('/activate/<token>/')
def activate(token):
    if User.check_activate_token(token):
        flash('账户已激活')
        return redirect(url_for('main.pzl'))
    else:
        flash('激活失败')
        return redirect(url_for('main.pzl'))


# 用户登录
@users.route('/login/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        user = User.query.filter(or_(User.username == username, User.email == username)).first()
        if not user:
            flash('用户名或密码错误')
        elif not user.confirm:
            flash('用户未被激活,请先激活在登录')
        elif not user.verify_password(form.password.data):
            flash('用户名或密码错误')
        else:
            login_user(user, remember=form.remember.data)
            flash('登录成功')
            return redirect(url_for('main.pzl', next=request.args.get('next')))
    return render_template('users/login.html', form=form)


@users.route('/logout/')
def logout():
    logout_user()
    return redirect(url_for('main.pzl'))


# 展示用户个人信息
@users.route('/profile/')
def profile():
    return render_template('users/profile.html')


@users.route('/change_password/', methods=['GET', 'POST'])
def change_password():
    form = UserPasswordForm()
    if form.validate_on_submit():
        newpwd = form.newpwd.data
        user = current_user._get_current_object()
        user.password = newpwd
        db.session.add(user)
        # 退出登录
        logout_user()
        flash('密码修改成功，请重新登录')
        return redirect(url_for('users.login'))
    return render_template('users/change_password.html', form=form)


# 生成随机的字符串
def random_string(length=32):
    import random
    import string
    base_str = string.ascii_letters + string.digits
    return ''.join(random.choice(base_str) for _ in range(length))


@users.route('/reset_password/', methods=['GET', 'POST'])
def reset_password():
    form1 = EUForm()
    global authcode
    authcode = random_string(length=6)
    if form1.validate_on_submit():
        global Uname
        username = form1.username.data
        Uname = username
        user = User.query.filter(or_(User.username == username, User.email == username)).first()
        # print(user.email)
        if user:
            send_mail([user.email], '验证码邮件', 'email/authcode', username=user.username, authcode=authcode)
            flash('验证码邮件已发送,注意查收')
            return redirect(url_for('users.reset_password2'))
        else:
            flash('请输入正确的用户名或邮箱')
    return render_template('users/reset_password.html', form1=form1)


@users.route('/reset_password2/', methods=['GET', 'POST'])
def reset_password2():
    form2 = AuthCodeForm()
    if form2.validate_on_submit():
        if authcode == form2.authcode.data:
            return redirect(url_for('users.reset_password3'))
        else:
            flash('验证码错误！')
    return render_template('users/reset_password2.html', form2=form2)


@users.route('/reset_password3/', methods=['GET', 'POST'])
def reset_password3():
    form3 = ResetPwdForm()
    user = User.query.filter(or_(User.username == Uname, User.email == Uname)).first()
    print(user)
    if form3.validate_on_submit():
        newpwd = form3.password.data
        if not user.verify_password(newpwd):
            user.password = newpwd
            db.session.add(user)
        logout_user()
        return redirect(url_for('users.reset_password4'))
    return render_template('users/reset_password3.html', form3=form3)


@users.route('/reset_password4/')
def reset_password4():
    return render_template('users/reset_password4.html')


@users.route('/edit_icon/', methods=['GET', 'POST'])
def edit_icon():
    form = IconForm()
    if form.validate_on_submit():
        # 生成随机文件名
        suffix = os.path.splitext(form.icon.data.filename)[1]
        filename = random_string() + suffix
        # 保存文件
        photos.save(form.icon.data, name=filename)

        # 拼接完整的路径名
        pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
        # 生成缩略图
        img = Image.open(pathname)
        # 重新设置尺寸
        img.thumbnail((128, 128))
        # 重新保存
        img.save(pathname)

        # 删除原来的头像，默认的除外
        if current_user.icon != 'default.jpg':
            os.remove(os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], current_user.icon))
        # 保存修改到数据库
        current_user.icon = filename
        db.session.add(current_user)
        flash('头像修改成功')
    return render_template('users/edit_icon.html', form=form)


# 修改邮箱
@users.route('/change_email/', methods=['GET', 'POST'])
def change_email():
    form = EmailForm()
    if form.validate_on_submit():
        newemail = form.email.data
        infoDict = {'user_id': current_user.id, 'newemail': newemail}
        token = User.generate_token(infoDict)
        send_mail([newemail], '修改邮箱邮件', 'email/change_email', username=current_user.username, token=token)
        flash('邮件已发送，注意查收')
        form.email.data = ''
    return render_template('users/change_email.html', form=form)


@users.route('/success_change_email/<token>/')
def success_change_email(token):
    data = User.check_token(token)
    if data:
        user = User.query.get(data['user_id'])
        if user.email != data['newemail']:
            user.email = data['newemail']
            db.session.add(user)
        flash('邮箱修改成功,请查看个人信息')
        return redirect(url_for('main.pzl'))
    else:
        flash('邮件已失效,请重新发送')
        return redirect(url_for('users.change_email'))


# 收藏功能
@users.route('/collect/<int:pid>/')
def collect(pid):
    # 收藏逻辑
    if current_user.is_favorites(pid):
        # 已收藏，则取消收藏
        current_user.cancel_favorite(pid)
    else:
        current_user.add_favorite(pid)
    return jsonify({'result': 'ok'})

# 关注功能
@users.route('/focus/<int:uid>/')
def focus(uid):
    # # 关注逻辑
    # if current_user.is_focus(uid):
    #     # 已关注，则取消关注
    #     current_user.cancel_focus(uid)
    # else:
    #     current_user.add_focus(uid)
    return jsonify({'result': 'ok'})



# 帖子详情页有评论表单和显示评论
@users.route('/comment/<int:pid>/', methods=['GET', 'POST'])
def comment(pid):
    form = CommentForm()
    post = Post.query.get(pid)
    post.visitors += 1
    db.session.add(post)
    if form.validate_on_submit():
        # 判断用户是否登录
        if current_user.is_authenticated:
            p = Post(content=form.content.data, users_id=current_user.id, rid=pid)
            db.session.add(p)
            form.content.data = ''
            flash('评论成功')

        else:
            flash('登录后才能发布评论哦')
            return redirect(url_for('users.login'))
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(rid=pid). \
        order_by(Post.timestamp.desc()).paginate(page, per_page=3, error_out=False)
    comments = pagination.items
    return render_template('common/comment.html', form=form, post=post, pagination=pagination, comments=comments)

#显示我发过的的微博
@users.route('/myposts/')
def myposts():
    page = request.args.get('page', 1, type=int)
    # print(current_user.posts,type(current_user.posts))
    pagination = Post.query.filter_by(rid=0,users_id=current_user.id). \
        order_by(Post.timestamp.desc()).paginate(page, per_page=3, error_out=False)
    posts = pagination.items
    return render_template('common/mypost.html',posts=posts, pagination=pagination)


#显示我收藏过得的微博
@users.route('/myfavorites/')
def myfavorites():
    page = request.args.get('page', 1, type=int)
    print(current_user.favorites,type(current_user.favorites))
    # pagination = Post.query.filter_by(rid=0, users_id=current_user.id). \
    #     order_by(Post.timestamp.desc()).paginate(page, per_page=3, error_out=False)
    pagination = current_user.favorites. \
        order_by(Post.timestamp.desc()).paginate(page, per_page=3, error_out=False)
    posts = pagination.items
    return render_template('common/myfavorites.html', posts=posts, pagination=pagination)


#展示被点击用户头像跳转到该用户的用户发的帖子和用户信息
@users.route('/udetail/<int:uid>/')
def udetail(uid):
    user=User.query.get(uid)
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(users_id=user.id). \
        order_by(Post.timestamp.desc()).paginate(page, per_page=3, error_out=False)
    posts = pagination.items
    return render_template('common/udetail.html', user=user,posts=posts, pagination=pagination)



