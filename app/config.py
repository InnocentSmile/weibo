import os

# BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
BASE_DIR = os.path.abspath(os.path.dirname(__file__))


# 定义配置基类
class Config:
    # 秘钥
    SECRET_KEY = os.environ.get('SECRET_KEY') or '123456'

    # 数据库公用配置
    # 无警告
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # 自动提交
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True

    # 发邮件 配置
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.qq.com'
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or '1825514258@qq.com'
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or 'lhyjeyaywqfdegeg'
    MAIL_USE_SSL = True
    MAIL_SUPPRESS_SEND = False
    MAIL_PORT = 465
    MAIL_USE_TLS = False


    #文件上传的位置
    MAX_CONTENT_LENGTH = 8 * 1024 * 1024
    UPLOADED_PHOTOS_DEST = os.path.join(BASE_DIR, 'static/uploads')
    # 额外的初始化操作
    @staticmethod
    def init_app(app):
        pass


# 开发环境配置
class DevelopmentConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:pzl123456@localhost/dev-database'


# 测试环境配置
class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:pzl123456@localhost/test-database'


# 生产环境
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = 'mysql://root:pzl123456@localhost/product-database'



# 生成一个字典，用来根据字符串找到对应的配置类。
config = {
    'development': DevelopmentConfig,
    'testing': TestConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}

