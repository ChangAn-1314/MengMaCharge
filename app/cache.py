"""
充电桩监控系统 - 缓存模块

这个模块提供缓存服务，用于存储和获取充电桩状态数据。
"""

import os
import json
import logging
from typing import Dict, Any, Optional, Union, List
from datetime import datetime, timedelta
from flask_caching import Cache
from app.config import Config

# 配置日志
logger = logging.getLogger(__name__)

# 初始化缓存
cache = Cache()

def init_cache(app):
    """初始化缓存配置"""
    # 获取环境变量中的缓存类型，默认优先于配置
    cache_type = os.environ.get('CACHE_TYPE')
    
    # 根据环境配置缓存类型
    if os.environ.get('FLASK_ENV') == 'testing' or cache_type == 'SimpleCache':
        # 测试环境或指定SimpleCache时使用简单字典缓存
        config = {
            'CACHE_TYPE': 'SimpleCache',
            'CACHE_DEFAULT_TIMEOUT': Config.CACHE_TIMEOUT
        }
    else:
        # 生产环境使用Redis缓存
        config = {
            'CACHE_TYPE': cache_type or 'RedisCache',
            'CACHE_REDIS_HOST': Config.REDIS_HOST,
            'CACHE_REDIS_PORT': Config.REDIS_PORT,
            'CACHE_REDIS_PASSWORD': Config.REDIS_PASSWORD,
            'CACHE_REDIS_DB': Config.REDIS_DB,
            'CACHE_DEFAULT_TIMEOUT': Config.CACHE_TIMEOUT,
            'CACHE_KEY_PREFIX': 'charging_station:'
        }
    
    # 配置并初始化缓存
    cache.init_app(app, config=config)
    logger.info(f"缓存已初始化，类型: {config['CACHE_TYPE']}")
    return cache

def set_station_status(station_id: str, status_data: Dict[str, Any]) -> bool:
    """存储充电桩状态到缓存
    
    Args:
        station_id: 充电桩ID
        status_data: 充电桩状态数据
        
    Returns:
        bool: 是否成功缓存
    """
    try:
        # 添加时间戳
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'data': status_data
        }
        # 将数据存入缓存
        cache.set(f"station:{station_id}", json.dumps(cache_data))
        logger.debug(f"充电桩 {station_id} 状态已缓存")
        return True
    except Exception as e:
        logger.error(f"缓存充电桩 {station_id} 状态时出错: {str(e)}")
        return False

def get_station_status(station_id: str) -> Optional[Dict[str, Any]]:
    """从缓存获取充电桩状态
    
    Args:
        station_id: 充电桩ID
        
    Returns:
        Optional[Dict[str, Any]]: 充电桩状态数据，如果不存在则返回None
    """
    try:
        # 从缓存获取数据
        cached_data = cache.get(f"station:{station_id}")
        if cached_data:
            # 解析缓存数据
            data = json.loads(cached_data)
            logger.debug(f"从缓存获取到充电桩 {station_id} 状态")
            
            # 验证缓存是否有效
            if is_cache_valid(station_id, data):
                return data['data']
            else:
                logger.debug(f"充电桩 {station_id} 缓存已过期")
                return None
                
        logger.debug(f"缓存中未找到充电桩 {station_id} 状态")
        return None
    except Exception as e:
        logger.error(f"获取充电桩 {station_id} 缓存状态时出错: {str(e)}")
        return None

def is_cache_valid(station_id: str, cached_data: Optional[Dict[str, Any]] = None) -> bool:
    """检查缓存是否有效
    
    Args:
        station_id: 充电桩ID
        cached_data: 已经获取的缓存数据，如果为None则会从缓存中获取
        
    Returns:
        bool: 缓存是否有效
    """
    try:
        # 如果没有提供缓存数据，则从缓存获取
        if cached_data is None:
            cached_data_str = cache.get(f"station:{station_id}")
            if not cached_data_str:
                return False
            cached_data = json.loads(cached_data_str)
        
        # 获取缓存时间戳和当前时间
        timestamp_str = cached_data.get('timestamp')
        if not timestamp_str:
            return False
            
        cache_time = datetime.fromisoformat(timestamp_str)
        current_time = datetime.now()
        
        # 检查缓存是否过期
        cache_valid = (current_time - cache_time) < timedelta(seconds=Config.CACHE_TIMEOUT)
        
        if not cache_valid:
            logger.debug(f"充电桩 {station_id} 缓存已过期，已经过去 {(current_time - cache_time).total_seconds()} 秒")
        
        return cache_valid
    except Exception as e:
        logger.error(f"检查缓存有效性时出错: {str(e)}")
        return False

def invalidate_cache(station_id: str = None) -> bool:
    """使缓存失效
    
    Args:
        station_id: 特定充电桩ID，为None时清空所有缓存
        
    Returns:
        bool: 操作是否成功
    """
    try:
        if station_id:
            # 清除特定充电桩的缓存
            cache.delete(f"station:{station_id}")
            logger.debug(f"已清除充电桩 {station_id} 的缓存")
        else:
            # 清除所有缓存
            cache.clear()
            logger.debug("已清除所有缓存")
        return True
    except Exception as e:
        logger.error(f"清除缓存时出错: {str(e)}")
        return False

def get_cached_stations() -> List[str]:
    """获取所有已缓存的充电桩ID
    
    Returns:
        List[str]: 已缓存的充电桩ID列表
    """
    try:
        # 根据缓存类型选择不同的方式获取所有键
        if Config.FLASK_ENV == 'testing' or cache.config.get('CACHE_TYPE') == 'SimpleCache':
            # 字典缓存直接遍历键
            keys = cache._cache.keys()
        else:
            # Redis缓存使用匹配模式获取键
            keys = cache._read_client.keys(f"{cache.config.get('CACHE_KEY_PREFIX', '')}station:*") 
        
        # 从键中提取充电桩ID
        station_ids = []
        prefix = f"{cache.config.get('CACHE_KEY_PREFIX', '')}station:"
        for key in keys:
            if isinstance(key, bytes):
                key = key.decode('utf-8')
            if key.startswith(prefix):
                station_id = key[len(prefix):]
                station_ids.append(station_id)
                
        return station_ids
    except Exception as e:
        logger.error(f"获取已缓存充电桩列表时出错: {str(e)}")
        return [] 