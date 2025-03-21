"""
充电桩监控系统 - 应用初始化模块

这个模块负责初始化Flask应用、数据库连接和其他必要的组件。
"""

import os
from typing import Optional
from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine, text
from app.models.port_status import db, ChargingStation, PortStatus

def create_app(test_config: Optional[dict] = None) -> Flask:
    """
    创建并配置Flask应用实例

    Args:
        test_config: 可选的测试配置字典

    Returns:
        配置好的Flask应用实例
    """
    app = Flask(__name__)
    
    # 配置静态文件
    app.static_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.static_url_path = '/static'
    
    CORS(app)
    
    if test_config is None:
        # 生产环境配置
        app.config.from_mapping(
            SECRET_KEY='dev',
            SQLALCHEMY_TRACK_MODIFICATIONS=False,
            JSON_AS_ASCII=False
        )
    else:
        # 测试环境配置
        app.config.update(test_config)

    # 初始化数据库
    engine = create_engine('mysql+pymysql://root:M040112s040202!@localhost/')
    with engine.connect() as conn:
        # 删除已存在的数据库
        # conn.execute(text("DROP DATABASE IF EXISTS port_status_db"))
        # conn.commit()
        # 创建新数据库
        conn.execute(text("CREATE DATABASE IF NOT EXISTS port_status_db"))
        conn.commit()
    
    # 配置数据库URI并初始化
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:M040112s040202!@localhost/port_status_db'
    db.init_app(app)
    
    # 确保数据库表存在
    with app.app_context():
        db.create_all()
        
        # 创建默认充电桩
        default_station = ChargingStation.query.filter_by(station_id='9313600954').first()
        if not default_station:
            default_station = ChargingStation(
                station_id='9313600954',
                name='信阳学院充电桩',
                is_active=True
            )
            db.session.add(default_station)
            
            # 创建默认端口
            for i in range(1, 5):  # 创建4个端口
                port = PortStatus(
                    station_id='9313600954',
                    port_number=i,
                    status='空闲',
                    voltage=220.0,
                    current=0.0,
                    power=0.0
                )
                db.session.add(port)
            
            db.session.commit()
    
    # 注册蓝图
    from app import routes
    app.register_blueprint(routes.bp)
    
    return app
