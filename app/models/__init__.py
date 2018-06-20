from .users import User
from .post import Post

from app.extensions import db
#定义多对多的第三张表
#收藏
collections = db.Table('collections',
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'),primary_key=True),
    db.Column('posts_id', db.Integer, db.ForeignKey('posts.id'),primary_key=True)
)



