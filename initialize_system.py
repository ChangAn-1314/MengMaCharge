"""
充电桩监控系统 - 系统初始化脚本

这个脚本用于初始化整个系统，包括创建.env文件、初始化数据库等。
"""

import os
import sys
import logging
from pathlib import Path
from app.init_db import init_database

# 配置日志
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def check_env_file():
    """检查.env文件是否存在，不存在则从模板创建"""
    env_file = Path('.env')
    env_example = Path('.env.example')
    
    if not env_file.exists():
        logger.info(".env文件不存在，从模板创建...")
        if env_example.exists():
            with open(env_example, 'r') as f:
                template = f.read()
            
            # 提示用户配置
            logger.info("请输入数据库配置信息：")
            db_user = input("数据库用户名 [root]: ") or "root"
            db_password = input("数据库密码: ")
            db_host = input("数据库主机 [localhost]: ") or "localhost"
            db_name = input("数据库名称 [port_status_db]: ") or "port_status_db"
            
            # 更新模板
            template = template.replace('DB_USER=root', f'DB_USER={db_user}')
            template = template.replace('DB_PASSWORD=your_password_here', f'DB_PASSWORD={db_password}')
            template = template.replace('DB_HOST=localhost', f'DB_HOST={db_host}')
            template = template.replace('DB_NAME=port_status_db', f'DB_NAME={db_name}')
            
            # 写入.env文件
            with open(env_file, 'w') as f:
                f.write(template)
                
            logger.info(".env文件已创建")
            
            # 设置环境变量，确保当前进程能读取
            os.environ['DB_USER'] = db_user
            os.environ['DB_PASSWORD'] = db_password
            os.environ['DB_HOST'] = db_host
            os.environ['DB_NAME'] = db_name
            
            return True
        else:
            logger.error(".env.example模板文件不存在，无法创建.env文件")
            return False
    else:
        logger.info(".env文件已存在")
        return True

def initialize_system():
    """初始化整个系统"""
    try:
        logger.info("开始初始化充电桩监控系统...")
        
        # 检查和创建.env文件
        if not check_env_file():
            return False
        
        # 初始化数据库
        logger.info("初始化数据库...")
        if not init_database():
            return False
        
        logger.info("系统初始化完成！")
        return True
    except Exception as e:
        logger.error(f"初始化过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = initialize_system()
    sys.exit(0 if success else 1) 