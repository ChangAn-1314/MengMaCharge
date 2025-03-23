"""
充电桩监控系统 - 主页蓝图模块

这个模块负责主页面的渲染和展示。
"""

from flask import Blueprint, render_template
from app.services.station_service import get_all_active_stations

# 创建蓝图
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index() -> str:
    """渲染主页，显示所有充电桩的状态"""
    try:
        # 获取所有激活的充电桩
        stations_data = get_all_active_stations()
        return render_template('index.html', stations=stations_data)
    except Exception as e:
        return render_template('index.html', stations=[], error=str(e)) 