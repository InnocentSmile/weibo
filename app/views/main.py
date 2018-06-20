import os

from PIL import Image
from flask import Blueprint, render_template, current_app, redirect, url_for, flash, request, render_template_string
from flask_login import current_user
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer

from app.extensions import db, photos
from app.forms import PostsForm
from app.models import Post


# 创建蓝本对象
main = Blueprint('main', __name__)


# 生成随机的字符串
def random_string(length=32):
    import random
    import string
    base_str = string.ascii_letters + string.digits
    return ''.join(random.choice(base_str) for _ in range(length))


# 视图函数
@main.route('/',methods=['GET', 'POST'])
# @cache.cached(timeout=90,key_prefix='post')
def pzl():
    print('从数据库中加载')
    form = PostsForm()
    next=request.args.get('next')
    if next:
        form.content.data = next
    if form.validate_on_submit():
        # 判断用户是否登录
        if current_user.is_authenticated:
            suffix = os.path.splitext(form.pic.data.filename)[1]
            filename = random_string() + suffix
            # 保存文件
            photos.save(form.pic.data, name=filename)

            # 拼接完整的路径名
            pathname = os.path.join(current_app.config['UPLOADED_PHOTOS_DEST'], filename)
            # 生成缩略图
            img = Image.open(pathname)
            # 重新设置尺寸
            img.thumbnail((128, 128))
            # 重新保存
            img.save(pathname)

            p = Post(content=form.content.data,category=form.category.data,users_id = current_user.id,pic=filename)
            db.session.add(p)
            form.content.data=''
            flash('发布成功')
            return redirect(url_for('main.pzl'))
        else:
            flash('登录后才能发布微博哦')
            return redirect(url_for('users.login',next=form.content.data))
    # posts = Post.query.filter_by(rid=0).order_by(Post.timestamp.desc()).all()
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(rid=0).\
        order_by(Post.timestamp.desc()).paginate(page, per_page=3,error_out=False)
    posts=pagination.items
    return render_template('common/index.html',form=form,posts=posts,pagination=pagination)

# 视图函数
@main.route('/index/')
def index():
    s = Serializer(current_app.config['SECRET_KEY'])
    return s.dumps({'id':250})

@main.route('/load/<s>/')
def load_serializer(s):
    se = Serializer(current_app.config['SECRET_KEY'])
    data = se.loads(s)
    return str(data)


#搜索功能
@main.route('/search/')
def search():
    search=request.args.get('search')

    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(rid=0). \
        filter(Post.content.like('%'+search+'%')).order_by(Post.timestamp.desc()).paginate(page, per_page=3,error_out=False)
    posts=pagination.items
    return render_template('common/search.html',posts=posts,pagination=pagination,search=search)


#显示符合条件类别的帖子
@main.route('/show/')
def show():
    category=request.args.get('category')
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(rid=0). \
        filter(Post.category==category).order_by(Post.timestamp.desc()).paginate(page, per_page=3,error_out=False)
    posts=pagination.items
    return render_template('common/search.html',posts=posts,pagination=pagination,category=category)

#根据访问量排行
@main.route('/hot/')
def hot():
    page = request.args.get('page', 1, type=int)
    pagination = Post.query.filter_by(rid=0). \
        order_by(Post.visitors.desc()).order_by(Post.timestamp.desc()).paginate(page, per_page=3, error_out=False)
    posts = pagination.items
    return render_template('common/hot.html',posts=posts,pagination=pagination)


#测试缓存
@main.route('/user/')
def user():
    addr = request.remote_addr
    #生成缓存的key
    key = addr +'user'
    result = cache.get(key)
    #判断缓存中是否有值
    if result:
        #从缓存中加载数据
        print('从缓存中加载数据')
        return result
    result = render_template_string('<h1>今天也不能休息</h1>')
    print(addr,'数据库中加载数据')
    #设置到缓存中
    cache.set(key,result,timeout=90)
    return result


