"""
充电桩监控系统 - 数据模型模块

这个模块定义了系统使用的模型。
"""

from datetime import datetime
from typing import Dict, Any, List
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ChargingStation(db.Model):
    """充电桩模型
    
    Attributes:
        id: 主键
        station_id: 充电桩ID
        name: 充电桩名称
        is_active: 是否激活
        ports: 关联的端口状态记录
    """
    __tablename__ = 'charging_stations'
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(20), unique=True, nullable=False, index=True, comment='充电桩ID')
    name = db.Column(db.String(50), nullable=True, comment='充电桩名称')
    is_active = db.Column(db.Boolean, default=True, nullable=False, index=True, comment='是否激活')
    
    # 关联端口状态
    ports = db.relationship('PortStatus', backref='station', lazy=True,
                          order_by='PortStatus.port_number')

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'station_id': self.station_id,
            'name': self.name,
            'ports': [port.to_dict() for port in self.ports]
        }

    @staticmethod
    def get_active_stations() -> List['ChargingStation']:
        """获取所有激活的充电桩"""
        return ChargingStation.query.filter_by(is_active=True).all()

class PortStatus(db.Model):
    """端口状态模型
    
    Attributes:
        id: 主键
        station_id: 关联的充电桩ID
        port_number: 端口号
        status: 端口状态（空闲/占用）
        service: 服务类型
        voltage: 电压
        current: 电流
        timestamp: 状态更新时间
    """
    __tablename__ = 'port_status'
    
    # 添加复合索引
    __table_args__ = (
        db.Index('idx_station_port', 'station_id', 'port_number'),
        db.Index('idx_station_timestamp', 'station_id', 'timestamp'),
    )
    
    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(20), db.ForeignKey('charging_stations.station_id'), 
                         nullable=False, comment='充电桩ID')
    port_number = db.Column(db.Integer, nullable=False, comment='端口号')
    status = db.Column(db.String(10), nullable=False, comment='端口状态')
    service = db.Column(db.String(50), comment='服务类型')
    voltage = db.Column(db.Float, comment='电压')
    current = db.Column(db.Float, comment='电流')
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, 
                        onupdate=datetime.utcnow, comment='状态更新时间')

    def to_dict(self) -> Dict[str, Any]:
        """将模型转换为字典"""
        return {
            'port': self.port_number,  # 注意：这里改为'port'以匹配API格式
            'status': self.status,
            'service': self.service,
            'voltage': self.voltage,
            'current': self.current,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None
        }

    @staticmethod
    def update_port_status(station_id: str, port_data: Dict[str, Any]) -> None:
        """更新端口状态
        
        Args:
            station_id: 充电桩ID
            port_data: 端口状态数据
        """
        port = PortStatus.query.filter_by(
            station_id=station_id,
            port_number=port_data['port']
        ).first()
        
        if not port:
            port = PortStatus(
                station_id=station_id,
                port_number=port_data['port']
            )
            db.session.add(port)
        
        port.status = port_data['status']
        port.service = port_data['service']
        port.voltage = port_data['voltage']
        port.current = port_data['current']
        port.timestamp = datetime.now()
        
        db.session.commit()
