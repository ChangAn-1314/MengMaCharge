"""
充电桩监控系统 - 数据库初始化脚本

这个脚本用于初始化数据库结构和基础数据。
"""

import os
import sys
import logging
from sqlalchemy.exc import SQLAlchemyError
from app import create_app
from app.models.port_status import db, ChargingStation
from app.repositories.station_repository import StationRepository, PortRepository

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def init_database():
    """初始化数据库结构和基础数据"""
    try:
        # 从环境变量获取配置
        config_name = os.environ.get('FLASK_ENV', 'development')
        logger.info(f"使用配置: {config_name} 初始化数据库")
        
        # 创建应用实例
        app = create_app(config_name)
        
        with app.app_context():
            # 创建所有表
            logger.info("创建数据库表...")
            db.create_all()
            logger.info("数据库表创建完成")
            
            # 检查默认充电桩是否存在
            logger.info("检查默认充电桩...")
            default_station = StationRepository.get_station_by_id('9313600954')
            if not default_station:
                # 创建默认充电桩
                logger.info("创建默认充电桩...")
                station = StationRepository.create_station(
                    station_id='9313600954',
                    name='信阳学院充电桩'
                )
                
                # 创建默认端口
                logger.info("创建默认端口...")
                for i in range(1, 5):
                    PortRepository.create_port(
                        station_id='9313600954',
                        port_number=i,
                        status='空闲',
                        service='充电服务'
                    )
                
                logger.info(f"已创建默认充电桩: {station.name}")
            else:
                logger.info(f"默认充电桩已存在: {default_station.name}")
            
            logger.info("数据库初始化完成！")
            return True
    except SQLAlchemyError as e:
        logger.error(f"数据库错误: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"初始化过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1) 