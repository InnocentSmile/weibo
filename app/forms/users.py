from flask_login import current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, FileField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from flask_wtf.file import FileField, FileAllowed, FileRequired

from app.models import User
from app.extensions import photos


class RegisterForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired(message='请填写用户名'), Length(4, 20, message='长度在4到20个字符之间')])
    email = StringField('邮箱(务必填写正确,否则无法激活登录)', validators=[DataRequired(message='请填写邮箱'), Email(message='请填写正确的邮箱格式')])
    password = PasswordField('密码', validators=[DataRequired(message='请填写密码'), Length(8, 20, message='密码长度在8到20之间'),
                                               EqualTo('confirm', message='密码不一致')])
    confirm = PasswordField('密码确认')
    submit = SubmitField('注册')

    # 检验username是否存在
    def validate_username(self, field):
        user = User.query.filter_by(username=field.data).first()
        if user:
            raise ValidationError('用户名已存在')

    # 校验邮箱是否已存在
    def validate_email(self, field):
        user = User.query.filter_by(email=field.data).first()
        if user:
            raise ValidationError('邮箱已存在')


# 定义登录的form表单
class LoginForm(FlaskForm):
    username = StringField('用户名或邮箱', validators=[DataRequired(message='用户名不能为空')])
    password = PasswordField('密码', validators=[DataRequired(message='密码不能为空')])
    remember = BooleanField('记住我',default=True)
    submit = SubmitField('登录')


# 定义修改密码的表单
class UserPasswordForm(FlaskForm):
    oldpwd = PasswordField('原密码', validators=[DataRequired(message='原密码不能为空')])
    newpwd = PasswordField('新密码', validators=[DataRequired(message='请填写新密码'), Length(8, 20, message='密码长度在8到20之间'),
                                              EqualTo('confirm', message='密码不一致')])
    confirm = PasswordField('密码确认')
    submit = SubmitField('注册')

    # 校验原密码是否正确
    def validate_oldpwd(self, field):
        # 获取真实user对象
        user = current_user._get_current_object()
        if not user.verify_password(field.data):
            raise ValidationError('原密码错误')

    # 校验新老密码不能一致
    def validate_newpwd(self, field):
        # 获取真实user对象
        user = current_user._get_current_object()
        if user.verify_password(field.data):
            raise ValidationError('新旧密码不能一样')


# 添加头像表单
class IconForm(FlaskForm):
    icon = FileField('头像', render_kw={'class': 'btn btn-default'},
                     validators=[FileAllowed(photos, message='只能上传图片'), FileRequired(message='请先选择文件')])
    submit = SubmitField('修改')


# 填写新邮箱来修改邮箱
class EmailForm(FlaskForm):
    email = StringField('新邮箱(务必填写正确,否则无法收到修改邮件)',
                        validators=[DataRequired(message='请填写新邮箱'), Email(message='请填写正确的邮箱格式')])
    submit = SubmitField('提交')


# 用来提交用户名或邮箱来重置密码
class EUForm(FlaskForm):
    username = StringField('用户名或有效的邮箱', validators=[DataRequired(message='用户名不能为空')])
    submit = SubmitField('下一步',render_kw={'style':"float: right"})

# 用来提交验证码
class AuthCodeForm(FlaskForm):
    authcode = StringField('验证码', validators=[DataRequired(message='验证码不能为空')])
    submit = SubmitField('提交',render_kw={'style':"float: right"})


#重置密码
class ResetPwdForm(FlaskForm):
    password = PasswordField('新密码', validators=[DataRequired(message='请填写密码'), Length(8, 20, message='密码长度在8到20之间'),
                                               EqualTo('confirm', message='密码不一致')])
    confirm = PasswordField('密码确认')
    submit = SubmitField('确定',render_kw={'style':"float: right"})