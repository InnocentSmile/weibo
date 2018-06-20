from flask_wtf import FlaskForm
from wtforms import TextAreaField, SubmitField,SelectField
from wtforms.validators import Length,DataRequired
from flask_wtf.file import FileField, FileAllowed, FileRequired
from app.extensions import photos
from flask_ckeditor import CKEditorField

leibie=[('科技','科技'),('人文','人文'),('娱乐','娱乐')]
class PostsForm(FlaskForm):
    content = TextAreaField('',
        render_kw={'placeholder': '这一刻的想法...','style':'height:100px'},
        validators=[DataRequired(message='请说点什么吧'),Length(5, 256, message='说话要注意分寸(5~256)')])
    # content = CKEditorField('',
    #     render_kw={'placeholder': '这一刻的想法...','style':'height:100px'},
    #     validators=[DataRequired(message='请说点什么吧'),Length(5, 256, message='说话要注意分寸(5~256)')])
    category =SelectField('类别',choices=leibie)
    pic =FileField('描述图', render_kw={'class': 'btn btn-default'},
                     validators=[FileAllowed(photos, message='只能上传图片'), FileRequired(message='请先选择文件')])
    submit = SubmitField('发布',render_kw={'style':"float: right"})


class CommentForm(FlaskForm):
    content = TextAreaField('',
                            render_kw={'placeholder': '想说点啥...', 'style': 'height:100px'},
                            validators=[DataRequired(message='请说点什么吧'), Length(5, 256, message='说话要注意分寸(5~256)')])
    submit = SubmitField('评论', render_kw={'style': "float: right"})