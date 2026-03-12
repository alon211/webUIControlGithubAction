"""
Flask 应用工厂模块
"""
import os
import logging
from pathlib import Path
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy

# 初始化数据库扩展
db = SQLAlchemy()

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def create_app(config=None):
    """Flask 应用工厂函数"""
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')

    # 获取项目根目录
    basedir = Path(__file__).parent.parent

    # 默认配置
    app.config.update(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'dev-secret-key'),
        SQLALCHEMY_DATABASE_URI=os.environ.get('DATABASE_URI', f'sqlite:///{basedir}/data/app.db'),
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        DOWNLOAD_DIR=os.environ.get('DOWNLOAD_DIR', str(basedir / 'data' / 'downloads')),
    )

    if config:
        app.config.update(config)

    # 确保目录存在
    _ensure_directories(app)

    # 初始化数据库
    db.init_app(app)

    # 注册路由
    _register_routes(app)
    _register_error_handlers(app)

    logger.info('Flask 应用创建成功')
    return app


def _ensure_directories(app):
    """确保必要的目录存在"""
    for directory in ['data', 'logs', app.config.get('DOWNLOAD_DIR', 'data/downloads')]:
        Path(directory).mkdir(parents=True, exist_ok=True)


def _register_routes(app):
    """注册所有路由蓝图"""
    from app.routes.config import config_bp
    from app.routes.files import files_bp
    from app.routes.workflows import workflows_bp
    app.register_blueprint(config_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(workflows_bp)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/api/health')
    def health():
        return {'status': 'healthy'}


def _register_error_handlers(app):
    """注册错误处理器"""
    @app.errorhandler(404)
    def not_found(error):
        return {'error': 'Not found'}, 404

    @app.errorhandler(Exception)
    def handle_exception(error):
        logger.exception(f'未处理的异常: {error}')
        return {'error': str(error)}, 500
