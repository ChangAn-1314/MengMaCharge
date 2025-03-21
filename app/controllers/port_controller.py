from flask import jsonify
from app.models.port_status import db, PortStatus
from datetime import datetime
import sys
import os

# Add parent directory to path to import get_port_status
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from port_status import get_port_status

def update_port_status():
    try:
        # Get latest status from the API
        status_data = get_port_status()
        
        # Update database with new status
        for port in status_data['ports']:
            port_status = PortStatus.query.filter_by(
                device_id=status_data['device_id'],
                port_number=port['port']
            ).first()
            
            if not port_status:
                port_status = PortStatus(
                    device_id=status_data['device_id'],
                    port_number=port['port']
                )
                db.session.add(port_status)
            
            port_status.status = port['status']
            port_status.service = port['service']
            port_status.voltage = port['voltage']
            port_status.current = port['current']
            port_status.timestamp = datetime.utcnow()
        
        db.session.commit()
        return jsonify(status_data), 200
    
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_latest_status():
    try:
        ports = PortStatus.query.order_by(PortStatus.timestamp.desc()).all()
        return jsonify([port.to_dict() for port in ports]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
