"""
充电桩监控系统 - 应用初始化模块

这个模块负责初始化Flask应用、数据库连接和其他必要的组件。
"""

import os
import logging
from typing import Optional
from flask import Flask
from flask_cors import CORS
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from app.models.port_status import db
from app.config import config

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def create_app(config_name: str = None) -> Flask:
    """
    创建并配置Flask应用实例

    Args:
        config_name: 配置名称，默认从环境变量获取

    Returns:
        配置好的Flask应用实例
    """
    if config_name is None:
        config_name = os.environ.get('FLASK_ENV', 'default')
    
    logger.info(f"启动应用，使用配置: {config_name}")
    
    app = Flask(__name__)
    
    # 配置静态文件
    app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.static_url_path = '/static'
    
    # 应用配置
    app.config.from_object(config[config_name])
    # 初始化配置
    if hasattr(config[config_name], 'init_app'):
        config[config_name].init_app(app)
    
    # 跨域支持
    CORS(app)
    
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
            engine = create_engine(db_url)
            with engine.connect() as conn:
                logger.info(f"正在创建数据库 {db_name}...")
                conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {db_name}"))
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
    
    return app
