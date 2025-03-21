"""
充电桩监控系统 - 路由模块

这个模块定义了Web应用的所有路由，包括页面渲染和API接口。
"""

from typing import Dict, List, Tuple, Union
from datetime import datetime, timedelta
from flask import Blueprint, render_template, jsonify
from app.models.port_status import ChargingStation, PortStatus, db
from port_status import get_port_status

# 创建蓝图
bp = Blueprint('main', __name__)

# 状态缓存
status_cache = {}
# 缓存过期时间（秒）
CACHE_TIMEOUT = 5

def get_default_station() -> ChargingStation:
    """获取或创建默认充电桩"""
    station = ChargingStation.query.filter_by(is_active=True).first()
    if not station:
        station = ChargingStation(
            station_id='9313600954',
            name='信阳学院充电桩',
            is_active=True
        )
        db.session.add(station)
        db.session.commit()
    return station

def should_update_status(station_id: str) -> bool:
    """检查是否需要更新状态
    
    Args:
        station_id: 充电桩ID
        
    Returns:
        bool: 是否需要更新
    """
    if station_id not in status_cache:
        return True
        
    last_update, _ = status_cache[station_id]
    return datetime.now() - last_update > timedelta(seconds=CACHE_TIMEOUT)

def update_station_status(station: ChargingStation) -> None:
    """更新充电桩状态
    
    Args:
        station: 充电桩实例
    """
    # 检查缓存
    if not should_update_status(station.station_id):
        return
        
    try:
        # 从API获取最新状态
        status_data = get_port_status(station.station_id)
        if status_data and 'ports' in status_data:
            # 更新数据库中的端口状态
            for port_data in status_data['ports']:
                PortStatus.update_port_status(station.station_id, port_data)
            # 更新缓存
            status_cache[station.station_id] = (datetime.now(), status_data)
    except Exception:
        pass

@bp.route('/')
def index() -> str:
    """渲染主页，显示所有充电桩的状态"""
    try:
        # 获取所有激活的充电桩
        stations = ChargingStation.query.filter_by(is_active=True).all()
        
        # 更新并获取所有充电桩状态
        stations_data = []
        for station in stations:
            update_station_status(station)
            stations_data.append(station.to_dict())
        
        return render_template('index.html', stations=stations_data)
    except Exception as e:
        return render_template('index.html', stations=[], error=str(e))

@bp.route('/api/ports')
def get_ports() -> Tuple[Dict[str, Union[List, str]], int]:
    """获取默认充电桩的端口状态API"""
    try:
        station = get_default_station()
        update_station_status(station)
        return jsonify({"ports": [port.to_dict() for port in station.ports]}), 200
    except Exception as e:
        return jsonify({'error': str(e), 'ports': []}), 500

@bp.route('/api/stations')
def get_stations() -> Tuple[Dict[str, Union[List, str]], int]:
    """获取所有充电桩状态的API"""
    try:
        stations = ChargingStation.query.filter_by(is_active=True).all()
        stations_data = []
        for station in stations:
            update_station_status(station)
            stations_data.append(station.to_dict())
        
        return jsonify({'stations': stations_data}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
