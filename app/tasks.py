"""
充电桩监控系统 - 异步任务模块

这个模块负责处理系统中的异步任务，如端口状态更新。
"""

import os
import logging
from typing import Dict, Any, List, Optional
from celery import Celery
from app.config import Config

# 配置日志
logger = logging.getLogger(__name__)

# 创建Celery实例
def make_celery(app_name=__name__):
    """创建Celery实例
    
    Args:
        app_name: 应用名称
        
    Returns:
        Celery: Celery实例
    """
    broker_url = Config.CELERY_BROKER_URL
    result_backend = Config.CELERY_RESULT_BACKEND
    
    celery = Celery(
        app_name,
        broker=broker_url,
        backend=result_backend,
        include=['app.tasks']
    )
    
    # 配置Celery
    celery.conf.update(
        task_serializer='json',
        accept_content=['json'],
        result_serializer='json',
        timezone='Asia/Shanghai',
        enable_utc=True,
        task_track_started=True,
        task_time_limit=Config.CELERY_TASK_TIMEOUT,
        worker_concurrency=Config.CELERY_WORKER_CONCURRENCY,
        task_acks_late=True,  # 任务执行完成后才确认，避免任务丢失
        task_reject_on_worker_lost=True,  # worker意外退出时重新分配任务
        task_default_rate_limit='10/m'  # 默认任务速率限制
    )
    
    return celery

celery = make_celery()

@celery.task(
    name='app.tasks.update_station',
    bind=True,
    max_retries=3,
    retry_backoff=True,
    retry_backoff_max=600,
    rate_limit='5/m'
)
def update_station(self, station_id: str) -> Dict[str, Any]:
    """异步更新充电桩状态
    
    Args:
        self: 任务实例
        station_id: 充电桩ID
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        logger.info(f"开始异步更新充电桩 {station_id} 状态")
        
        # 动态导入，避免循环导入
        from port_status import get_port_status
        from app.repositories.station_repository import PortRepository
        from app.cache import set_station_status
        
        # 获取状态数据
        status_data = get_port_status(station_id)
        
        # 检查是否有错误
        if 'error' in status_data:
            error_msg = status_data.get('error', '未知错误')
            logger.warning(f"获取充电桩 {station_id} 状态返回错误: {error_msg}")
            
            # 决定是否重试
            if "请求超时" in error_msg or "连接错误" in error_msg:
                # 网络错误通常是暂时的，可以重试
                if self.request.retries < self.max_retries:
                    logger.info(f"将在稍后重试获取充电桩 {station_id} 状态")
                    raise self.retry(
                        exc=Exception(error_msg),
                        countdown=2 ** self.request.retries * 10
                    )
            
            return {
                'status': 'error',
                'message': f'获取充电桩状态出错: {error_msg}',
                'data': status_data
            }
        
        # 如果数据有效，则更新
        if status_data and 'ports' in status_data and status_data['ports']:
            # 准备批量更新数据
            ports_data = []
            for port_data in status_data['ports']:
                port_data['station_id'] = station_id
                ports_data.append(port_data)
            
            try:
                # 批量更新数据库
                PortRepository.bulk_update_ports(ports_data)
                
                # 更新缓存
                set_station_status(station_id, status_data)
                
                logger.info(f"充电桩 {station_id} 状态更新完成，共 {len(ports_data)} 个端口")
                return {
                    'status': 'success',
                    'message': f'充电桩 {station_id} 状态已更新',
                    'data': status_data
                }
            except Exception as db_error:
                logger.error(f"更新充电桩 {station_id} 数据库或缓存时出错: {str(db_error)}")
                return {
                    'status': 'error',
                    'message': f'数据库更新出错: {str(db_error)}',
                    'data': status_data
                }
        else:
            logger.warning(f"充电桩 {station_id} 无有效状态数据")
            return {
                'status': 'warning',
                'message': f'充电桩 {station_id} 无有效状态数据',
                'data': status_data
            }
    except Exception as e:
        logger.error(f"更新充电桩 {station_id} 状态时出错: {str(e)}")
        return {
            'status': 'error',
            'message': f'更新充电桩状态出错: {str(e)}',
            'data': None
        }

@celery.task(
    name='app.tasks.batch_update_stations',
    bind=True,
    max_retries=2
)
def batch_update_stations(self, station_ids: List[str]) -> Dict[str, Any]:
    """批量异步更新多个充电桩状态
    
    Args:
        self: 任务实例
        station_ids: 充电桩ID列表
        
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        logger.info(f"开始批量更新充电桩状态，共 {len(station_ids)} 个")
        
        # 限制批处理大小，避免过载
        batch_size = Config.BATCH_UPDATE_SIZE
        results = {}
        
        # 分批处理
        for i in range(0, len(station_ids), batch_size):
            batch = station_ids[i:i+batch_size]
            logger.debug(f"处理批次 {i//batch_size + 1}，共 {len(batch)} 个充电桩")
            
            # 为每个充电桩创建独立的任务
            for station_id in batch:
                task = update_station.delay(station_id)
                results[station_id] = task.id
        
        return {
            'status': 'success',
            'message': f'已提交 {len(station_ids)} 个充电桩的状态更新任务',
            'tasks': results
        }
    except Exception as e:
        logger.error(f"批量更新充电桩状态时出错: {str(e)}")
        # 如果是网络问题或临时错误，尝试重试
        if "连接超时" in str(e) or "服务暂时不可用" in str(e):
            if self.request.retries < self.max_retries:
                logger.info("将在稍后重试批量更新任务")
                raise self.retry(exc=e, countdown=30)
                
        return {
            'status': 'error',
            'message': f'批量更新充电桩状态出错: {str(e)}',
            'tasks': {}
        }

@celery.task(name='app.tasks.refresh_cached_stations')
def refresh_cached_stations() -> Dict[str, Any]:
    """刷新所有已缓存充电桩的状态
    
    Returns:
        Dict[str, Any]: 操作结果
    """
    try:
        # 动态导入，避免循环导入
        from app.cache import get_cached_stations
        
        # 获取所有已缓存的充电桩ID
        station_ids = get_cached_stations()
        
        if station_ids:
            # 提交批量更新任务
            task = batch_update_stations.delay(station_ids)
            logger.info(f"已提交刷新 {len(station_ids)} 个已缓存充电桩的任务: {task.id}")
            return {
                'status': 'success',
                'message': f'已提交刷新 {len(station_ids)} 个已缓存充电桩的任务',
                'task_id': task.id
            }
        else:
            logger.info("没有找到已缓存的充电桩")
            return {
                'status': 'warning',
                'message': '没有找到已缓存的充电桩',
                'task_id': None
            }
    except Exception as e:
        logger.error(f"刷新已缓存充电桩时出错: {str(e)}")
        return {
            'status': 'error',
            'message': f'刷新已缓存充电桩出错: {str(e)}',
            'task_id': None
        } 