from datetime import datetime
from app.extensions import db


class Post(db.Model):
    __tablename__ = 'posts'
    id = db.Column(db.Integer, primary_key=True)
    #区别是评论还是微博
    rid = db.Column(db.Integer, index=True,nullable=False, default=0)
    content = db.Column(db.Text)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    # 添加关联外键 '表名.字段'
    users_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    #缩略图
    pic=db.Column(db.String(64), default='default.jpg')
    #类别
    category=db.Column(db.String(64), default='科技')
    #访问量
    visitors=db.Column(db.Integer,default=0)

    def __repr__(self):
        return self.content[:20]


