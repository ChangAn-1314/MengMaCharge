"""
充电桩监控系统 - 充电桩数据访问模块

这个模块封装了对充电桩数据的访问操作。
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from app.models.port_status import db, ChargingStation, PortStatus

# 配置日志
logger = logging.getLogger(__name__)

class StationRepository:
    """充电桩数据访问类"""
    
    @staticmethod
    def get_default_station() -> Optional[ChargingStation]:
        """获取默认充电桩"""
        return ChargingStation.query.filter_by(is_active=True).first()
    
    @staticmethod
    def create_station(station_id: str, name: str, is_active: bool = True) -> ChargingStation:
        """创建充电桩
        
        Args:
            station_id: 充电桩ID
            name: 充电桩名称
            is_active: 是否激活
            
        Returns:
            ChargingStation: 创建的充电桩实例
        """
        station = ChargingStation(
            station_id=station_id,
            name=name,
            is_active=is_active
        )
        db.session.add(station)
        db.session.commit()
        logger.info(f"创建充电桩: {station_id}, 名称: {name}")
        return station
    
    @staticmethod
    def get_all_active_stations() -> List[ChargingStation]:
        """获取所有激活的充电桩
        
        Returns:
            List[ChargingStation]: 充电桩列表
        """
        return ChargingStation.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_station_by_id(station_id: str) -> Optional[ChargingStation]:
        """根据ID获取充电桩
        
        Args:
            station_id: 充电桩ID
            
        Returns:
            Optional[ChargingStation]: 充电桩实例或None
        """
        return ChargingStation.query.filter_by(station_id=station_id).first()
    
    @staticmethod
    def get_stations_by_ids(station_ids: List[str]) -> List[ChargingStation]:
        """根据ID列表批量获取充电桩
        
        Args:
            station_ids: 充电桩ID列表
            
        Returns:
            List[ChargingStation]: 充电桩实例列表
        """
        return ChargingStation.query.filter(ChargingStation.station_id.in_(station_ids)).all()


class PortRepository:
    """端口状态数据访问类"""
    
    @staticmethod
    def get_port(station_id: str, port_number: int) -> Optional[PortStatus]:
        """获取端口状态
        
        Args:
            station_id: 充电桩ID
            port_number: 端口号
            
        Returns:
            Optional[PortStatus]: 端口状态实例或None
        """
        return PortStatus.query.filter_by(
            station_id=station_id,
            port_number=port_number
        ).first()
    
    @staticmethod
    def get_ports_by_station(station_id: str) -> List[PortStatus]:
        """获取充电桩的所有端口
        
        Args:
            station_id: 充电桩ID
            
        Returns:
            List[PortStatus]: 端口状态实例列表
        """
        return PortStatus.query.filter_by(station_id=station_id).order_by(PortStatus.port_number).all()
    
    @staticmethod
    def get_ports_by_numbers(station_id: str, port_numbers: List[int]) -> List[PortStatus]:
        """根据端口号列表批量获取端口
        
        Args:
            station_id: 充电桩ID
            port_numbers: 端口号列表
            
        Returns:
            List[PortStatus]: 端口状态实例列表
        """
        return PortStatus.query.filter(
            PortStatus.station_id == station_id,
            PortStatus.port_number.in_(port_numbers)
        ).all()
    
    @staticmethod
    def create_port(station_id: str, port_number: int, status: str = '空闲',
                   service: Optional[str] = None, voltage: float = 0.0,
                   current: float = 0.0, power: float = 0.0) -> PortStatus:
        """创建端口状态
        
        Args:
            station_id: 充电桩ID
            port_number: 端口号
            status: 端口状态
            service: 服务类型
            voltage: 电压
            current: 电流
            power: 功率
            
        Returns:
            PortStatus: 创建的端口状态实例
        """
        port = PortStatus(
            station_id=station_id,
            port_number=port_number,
            status=status,
            service=service,
            voltage=voltage,
            current=current,
            power=power
        )
        db.session.add(port)
        db.session.commit()
        logger.info(f"创建端口: 充电桩 {station_id}, 端口号 {port_number}, 状态 {status}")
        return port
    
    @staticmethod
    def update_port(port: PortStatus, status: str, service: Optional[str] = None,
                   voltage: float = 0.0, current: float = 0.0, power: float = 0.0) -> PortStatus:
        """更新端口状态
        
        Args:
            port: 端口实例
            status: 端口状态
            service: 服务类型
            voltage: 电压
            current: 电流
            power: 功率
            
        Returns:
            PortStatus: 更新后的端口状态实例
        """
        port.status = status
        port.service = service
        port.voltage = voltage
        port.current = current
        port.power = power
        port.timestamp = datetime.now()
        db.session.commit()
        return port
    
    @staticmethod
    def bulk_update_ports(ports_data: List[Dict[str, Any]]) -> None:
        """批量更新端口状态
        
        Args:
            ports_data: 端口状态数据列表，每个字典包含station_id, port, status等字段
        """
        try:
            # 提取所有涉及的充电桩ID和端口号
            station_id_ports = {}
            for port_data in ports_data:
                station_id = port_data.get('station_id')
                port_number = port_data.get('port')
                
                if station_id and port_number:
                    if station_id not in station_id_ports:
                        station_id_ports[station_id] = []
                    station_id_ports[station_id].append(port_number)
            
            # 按充电桩分组查询端口
            all_existing_ports = {}
            for station_id, port_numbers in station_id_ports.items():
                existing_ports = PortRepository.get_ports_by_numbers(station_id, port_numbers)
                # 创建查找键
                for port in existing_ports:
                    key = f"{station_id}_{port.port_number}"
                    all_existing_ports[key] = port
            
            # 更新或创建端口
            current_time = datetime.now()
            for port_data in ports_data:
                station_id = port_data.get('station_id')
                port_number = port_data.get('port')
                
                if not station_id or not port_number:
                    logger.warning(f"端口数据缺少必要信息: {port_data}")
                    continue
                
                # 查找键
                key = f"{station_id}_{port_number}"
                port = all_existing_ports.get(key)
                
                if port:
                    # 更新现有端口
                    port.status = port_data.get('status', '空闲')
                    port.service = port_data.get('service', port.service)
                    port.voltage = port_data.get('voltage', port.voltage)
                    port.current = port_data.get('current', port.current)
                    port.power = port_data.get('power', port.power)
                    port.timestamp = current_time
                else:
                    # 创建新端口
                    port = PortStatus(
                        station_id=station_id,
                        port_number=port_number,
                        status=port_data.get('status', '空闲'),
                        service=port_data.get('service', '充电服务'),
                        voltage=port_data.get('voltage', 0.0),
                        current=port_data.get('current', 0.0),
                        power=port_data.get('power', 0.0),
                        timestamp=current_time
                    )
                    db.session.add(port)
            
            # 一次性提交所有更改
            db.session.commit()
            logger.info(f"批量更新完成，共处理 {len(ports_data)} 个端口数据")
        except Exception as e:
            logger.error(f"批量更新端口状态时出错: {str(e)}")
            db.session.rollback()
            raise
    
    @staticmethod
    def commit():
        """提交所有挂起的更改"""
        db.session.commit() 