"""
充电桩监控系统 - 充电桩服务模块

这个模块提供充电桩状态管理相关的服务功能。
"""

from typing import Dict, Any, List
from datetime import datetime, timedelta
from app.models.port_status import ChargingStation
from app.repositories.station_repository import StationRepository, PortRepository
from app.config import Config
from port_status import get_port_status

# 状态缓存
status_cache: Dict[str, tuple] = {}
# 缓存过期时间（秒）
CACHE_TIMEOUT = Config.CACHE_TIMEOUT

def get_default_station() -> ChargingStation:
    """获取或创建默认充电桩"""
    station = StationRepository.get_default_station()
    if not station:
        station = StationRepository.create_station(
            station_id='9313600954',
            name='信阳学院充电桩'
        )
        
        # 创建默认端口
        for i in range(1, 5):  # 创建4个端口
            PortRepository.create_port(
                station_id='9313600954',
                port_number=i,
                status='空闲',
                service='充电服务',
                voltage=220.0,
                current=0.0
            )
    
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
                PortRepository.update_or_create_port(station.station_id, port_data)
            # 更新缓存
            status_cache[station.station_id] = (datetime.now(), status_data)
    except Exception as e:
        print(f"更新充电桩状态时出错: {str(e)}")

def get_all_active_stations() -> List[Dict[str, Any]]:
    """获取所有激活的充电桩，并更新它们的状态
    
    Returns:
        List[Dict[str, Any]]: 包含所有充电桩数据的列表
    """
    try:
        # 获取所有激活的充电桩
        stations = StationRepository.get_all_active_stations()
        
        # 更新并获取所有充电桩状态
        stations_data = []
        for station in stations:
            update_station_status(station)
            stations_data.append(station.to_dict())
        
        return stations_data
    except Exception as e:
        print(f"获取充电桩列表时出错: {str(e)}")
        return [] 