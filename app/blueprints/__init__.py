"""
充电桩监控系统 - 蓝图包初始化模块

这个模块负责初始化和导出所有蓝图。
"""

from app.blueprints.main import main_bp
from app.blueprints.api import api_bp

# 导出所有蓝图，方便应用初始化时注册
all_blueprints = [main_bp, api_bp] 