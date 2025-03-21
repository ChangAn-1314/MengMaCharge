from flask import jsonify
from app.models.port_status import db, ChargingStation

def get_all_stations():
    try:
        stations = ChargingStation.query.filter_by(is_active=True).all()
        return jsonify([station.to_dict() for station in stations]), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def add_station(station_id, name=None):
    try:
        station = ChargingStation(
            station_id=station_id,
            name=name or f"充电桩 {station_id}"
        )
        db.session.add(station)
        db.session.commit()
        return jsonify(station.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def delete_station(station_id):
    try:
        station = ChargingStation.query.filter_by(station_id=station_id).first()
        if station:
            station.is_active = False
            db.session.commit()
            return jsonify({'message': '充电桩已停用'}), 200
        return jsonify({'error': '充电桩不存在'}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500
