"""
充电桩监控系统 - 充电桩数据访问模块

这个模块封装了对充电桩数据的访问操作。
"""

from typing import Dict, Any, List, Optional
from app.models.port_status import db, ChargingStation, PortStatus

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
        return port
    
    @staticmethod
    def update_port(port: PortStatus, port_data: Dict[str, Any]) -> None:
        """更新端口状态
        
        Args:
            port: 端口状态实例
            port_data: 端口状态数据
        """
        port.status = port_data.get('status', port.status)
        port.service = port_data.get('service', port.service)
        port.voltage = port_data.get('voltage', port.voltage)
        port.current = port_data.get('current', port.current)
        db.session.commit()
    
    @staticmethod
    def update_or_create_port(station_id: str, port_data: Dict[str, Any]) -> PortStatus:
        """更新或创建端口状态
        
        Args:
            station_id: 充电桩ID
            port_data: 端口状态数据
            
        Returns:
            PortStatus: 更新或创建的端口状态实例
        """
        port = PortRepository.get_port(station_id, port_data['port'])
        
        if not port:
            port = PortStatus(
                station_id=station_id,
                port_number=port_data['port']
            )
            db.session.add(port)
        
        port.status = port_data['status']
        port.service = port_data.get('service', '充电服务')
        port.voltage = port_data.get('voltage', 0.0)
        port.current = port_data.get('current', 0.0)
        
        db.session.commit()
        return port 