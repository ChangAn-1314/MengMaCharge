"""
充电桩监控系统 - API蓝图模块

这个模块负责提供RESTful API接口。
"""

from typing import Dict, List, Tuple, Union
from flask import Blueprint, jsonify
from app.services.station_service import get_default_station, update_station_status, get_all_active_stations

# 创建蓝图
api_bp = Blueprint('api', __name__, url_prefix='/api')

@api_bp.route('/ports')
def get_ports() -> Tuple[Dict[str, Union[List, str]], int]:
    """获取默认充电桩的端口状态API"""
    try:
        station = get_default_station()
        update_station_status(station)
        return jsonify({"ports": [port.to_dict() for port in station.ports]}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'ports': []}), 500

@api_bp.route('/stations')
def get_stations() -> Tuple[Dict[str, Union[List, str]], int]:
    """获取所有充电桩状态的API"""
    try:
        stations_data = get_all_active_stations()
        return jsonify({'stations': stations_data}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'stations': []}), 500 