from threading import Thread
from .extensions import mail
from flask import current_app, render_template
from flask_mail import Message


def async_send_mail(app, msg):
    with app.app_context():
        mail.send(msg)


# 异步发送邮件
def send_mail(to, subject, template, **kwargs):
    # 通过current_app这个代理对象，获取真正的app对象
    app = current_app._get_current_object()
    msg = Message(subject=subject, recipients=to, sender=app.config['MAIL_USERNAME'])
    msg.html = render_template(template + '.html', **kwargs)
    msg.body = render_template(template + '.txt', **kwargs)

    thr = Thread(target=async_send_mail, args=[app, msg])
    # 启动线程
    thr.start()