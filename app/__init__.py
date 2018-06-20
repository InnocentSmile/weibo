from flask import Flask, render_template
from app.config import config
from app.extensions import config_extensions
from app.views import config_blueprint


def config_errorhandler(app):
    # 如果在蓝本定制，则只针对蓝本的错误有效。
    # 可以使用app_errorhandler定制全局有效的错误显示
    # 定制全局404错误页面
    @app.errorhandler(404)
    def page_not_found(e):
        return render_template('error/404.html',e=e)




# 将创建app的动作封装成一个函数
def create_app(config_name):
    # 创建app实例对象
    app = Flask(__name__)
    # 加载配置
    app.config.from_object(config.get(config_name) or 'default')
    # 执行额外的初始化
    config.get(config_name).init_app(app)


    #设置debug=True,让toolbar生效
    # app.debug=True

    # 加载扩展
    config_extensions(app)

    # 配置蓝本
    config_blueprint(app)

    # 配置全局错误处理
    config_errorhandler(app)

    # 返回app实例对象
    return app