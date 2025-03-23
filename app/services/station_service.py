"""
充电桩监控系统 - 充电桩服务模块

这个模块提供充电桩状态管理相关的服务功能。
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.port_status import ChargingStation
from app.repositories.station_repository import StationRepository, PortRepository
from app.config import Config
from app.cache import get_station_status, set_station_status, is_cache_valid
from port_status import get_port_status

# 配置日志
logger = logging.getLogger(__name__)

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
    # 使用新的缓存系统检查缓存是否有效
    return not is_cache_valid(station_id)

def update_station_status(station: ChargingStation, use_async: bool = None) -> None:
    """更新充电桩状态
    
    Args:
        station: 充电桩实例
        use_async: 是否使用异步处理，默认根据配置决定
    """
    # 检查缓存
    if not should_update_status(station.station_id):
        logger.debug(f"从缓存获取充电桩 {station.station_id} 状态")
        return
    
    # 如果未指定是否异步，则使用配置
    if use_async is None:
        use_async = Config.ENABLE_ASYNC
    
    # 根据是否异步决定处理方式
    if use_async:
        logger.info(f"异步更新充电桩 {station.station_id} 状态")
        # 导入任务模块并调用异步任务
        from app.tasks import update_station as update_station_task
        update_station_task.delay(station.station_id)
    else:
        logger.info(f"同步更新充电桩 {station.station_id} 状态")
        update_station_sync(station)

def update_station_sync(station: ChargingStation) -> None:
    """同步更新充电桩状态
    
    Args:
        station: 充电桩实例
    """
    try:
        # 从API获取最新状态
        status_data = get_port_status(station.station_id)
        if status_data and 'ports' in status_data:
            # 批量更新数据库中的端口状态
            update_ports_batch(station.station_id, status_data['ports'])
            
            # 更新缓存
            set_station_status(station.station_id, status_data)
    except Exception as e:
        logger.error(f"更新充电桩状态时出错: {str(e)}")

def update_ports_batch(station_id: str, ports_data: List[Dict[str, Any]]) -> None:
    """批量更新端口状态
    
    Args:
        station_id: 充电桩ID
        ports_data: 端口状态数据列表
    """
    # 预先获取所有端口，减少查询次数
    port_numbers = [port_data['port'] for port_data in ports_data]
    existing_ports = PortRepository.get_ports_by_numbers(station_id, port_numbers)
    
    # 创建端口号到端口对象的映射
    port_map = {port.port_number: port for port in existing_ports}
    
    # 准备批量更新
    for port_data in ports_data:
        port_number = port_data['port']
        port = port_map.get(port_number)
        
        if not port:
            # 创建新端口
            PortRepository.create_port(
                station_id=station_id,
                port_number=port_number,
                status=port_data['status'],
                service=port_data.get('service', '充电服务'),
                voltage=port_data.get('voltage', 0.0),
                current=port_data.get('current', 0.0)
            )
        else:
            # 更新现有端口
            port.status = port_data['status']
            port.service = port_data.get('service', '充电服务')
            port.voltage = port_data.get('voltage', 0.0)
            port.current = port_data.get('current', 0.0)
            port.timestamp = datetime.now()
    
    # 统一提交所有更改，减少数据库操作次数
    PortRepository.commit()

def get_all_active_stations() -> List[Dict[str, Any]]:
    """获取所有激活的充电桩，并更新它们的状态
    
    Returns:
        List[Dict[str, Any]]: 包含所有充电桩数据的列表
    """
    try:
        # 获取所有激活的充电桩
        stations = StationRepository.get_all_active_stations()
        
        # 如果启用异步处理，提交异步任务批量更新
        if Config.ENABLE_ASYNC and stations:
            from app.tasks import batch_update_stations
            station_ids = [station.station_id for station in stations]
            batch_update_stations.delay(station_ids)
        else:
            # 同步更新每个充电桩
            for station in stations:
                update_station_status(station, use_async=False)
        
        # 更新并获取所有充电桩状态
        stations_data = []
        for station in stations:
            # 检查缓存中是否有数据
            cached_status = get_station_status(station.station_id)
            if cached_status:
                # 使用缓存数据构建响应
                stations_data.append({
                    'station_id': station.station_id,
                    'name': station.name,
                    'ports': cached_status.get('ports', [])
                })
            else:
                # 回退到数据库查询
                stations_data.append(station.to_dict())
        
        return stations_data
    except Exception as e:
        logger.error(f"获取充电桩列表时出错: {str(e)}")
        return []

def get_station_by_id(station_id: str) -> Optional[Dict[str, Any]]:
    """根据ID获取充电桩状态
    
    Args:
        station_id: 充电桩ID
        
    Returns:
        Optional[Dict[str, Any]]: 充电桩数据，如果不存在则返回None
    """
    try:
        # 尝试从缓存获取
        cached_status = get_station_status(station_id)
        if cached_status:
            # 获取充电桩基本信息
            station = StationRepository.get_station_by_id(station_id)
            if station:
                return {
                    'station_id': station.station_id,
                    'name': station.name,
                    'ports': cached_status.get('ports', [])
                }
        
        # 如果缓存没有，则获取实时数据
        station = StationRepository.get_station_by_id(station_id)
        if station:
            update_station_status(station)
            return station.to_dict()
        
        return None
    except Exception as e:
        logger.error(f"获取充电桩 {station_id} 信息时出错: {str(e)}")
        return None 