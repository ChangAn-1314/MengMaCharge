"""
充电桩监控系统 - 应用初始化模块

这个模块负责创建和配置Flask应用实例。
"""

import os
import logging
from typing import Optional
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from logging.handlers import RotatingFileHandler
from app.models.port_status import db
from app.config import config
from app.cache import init_cache

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def setup_logging(app):
    """配置应用日志系统"""
    log_level = getattr(logging, app.config.get('LOG_LEVEL', 'INFO'))
    app.logger.setLevel(log_level)
    
    # 如果配置了日志文件，则添加文件处理器
    log_file = app.config.get('LOG_FILE')
    if log_file:
        file_handler = RotatingFileHandler(
            log_file, 
            maxBytes=10485760,  # 10MB
            backupCount=5
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
        ))
        file_handler.setLevel(log_level)
        app.logger.addHandler(file_handler)
    
    # 开发环境记录更详细的日志
    if app.debug:
        app.logger.info('充电桩监控系统启动于调试模式')
    else:
        app.logger.info('充电桩监控系统启动于生产模式')

def create_app(config_name: str = None) -> Flask:
    """创建并配置Flask应用
    
    Args:
        config_name: 配置名称，如 'development', 'production', 'testing'
        
    Returns:
        Flask: 配置好的Flask应用实例
    """
    # 默认使用开发环境配置
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'development')
    
    # 创建Flask应用
    app = Flask(__name__)
    
    # 从配置类加载配置
    app.config.from_object(config[config_name])
    
    # 设置日志系统
    setup_logging(app)
    
    # 获取数据库配置
    if config_name != 'testing':  # 测试环境使用内存数据库，不需要创建
        db_config = config[config_name]
        db_user = db_config.DB_USER
        db_password = db_config.DB_PASSWORD
        db_host = db_config.DB_HOST
        db_name = db_config.DB_NAME
        
        # 确保数据库存在
        db_url = f"mysql+pymysql://{db_user}:{db_password}@{db_host}"
        logger.info(f"正在连接数据库 {db_host}...")
        
        try:
            # 配置连接池
            engine = create_engine(
                db_url, 
                pool_size=db_config.SQLALCHEMY_POOL_SIZE,
                pool_timeout=db_config.SQLALCHEMY_POOL_TIMEOUT,
                pool_recycle=db_config.SQLALCHEMY_POOL_RECYCLE,
                max_overflow=db_config.SQLALCHEMY_MAX_OVERFLOW
            )
            with engine.connect() as conn:
                logger.info(f"正在创建数据库 {db_name}...")
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci"))
                conn.commit()
                logger.info(f"数据库 {db_name} 已准备好")
        except SQLAlchemyError as e:
            logger.error(f"数据库连接错误: {str(e)}")
            logger.error(f"请检查数据库配置是否正确，用户名: {db_user}, 主机: {db_host}")
            # 在开发环境抛出错误，方便调试
            if config_name == 'development':
                raise
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册所有蓝图
    from app.blueprints import all_blueprints
    for blueprint in all_blueprints:
        app.register_blueprint(blueprint)
    
    # 初始化缓存系统
    with app.app_context():
        init_cache(app)
    
    # 注册命令
    register_commands(app)
    
    return app

def register_commands(app):
    """注册CLI命令"""
    
    @app.cli.command('init-db')
    def init_db_command():
        """初始化数据库命令"""
        from app.init_db import init_database
        if init_database():
            logger.info("数据库初始化成功")
        else:
            logger.error("数据库初始化失败")
    
    @app.cli.command('test-connection')
    def test_connection_command():
        """测试数据库连接命令"""
        try:
            # 执行简单查询测试连接
            result = db.session.execute(text("SELECT 1")).fetchone()
            if result:
                logger.info("数据库连接测试成功")
            else:
                logger.error("数据库连接测试失败: 无返回结果")
        except Exception as e:
            logger.error(f"数据库连接测试失败: {str(e)}")
    
    @app.cli.command('run-celery')
    def run_celery_command():
        """启动Celery工作进程命令"""
        import subprocess
        subprocess.run(["python", "celery_worker.py"])
        
    @app.cli.command('create-station')
    def create_station_command():
        """创建默认充电桩命令"""
        from app.services.station_service import get_default_station
        station = get_default_station()
        logger.info(f"已创建默认充电桩: {station.station_id} - {station.name}")
