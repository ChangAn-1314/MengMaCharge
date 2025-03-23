"""
充电桩监控系统 - 外部API模块

这个模块负责与充电桩API通信，获取端口状态数据。
"""

import hashlib
import hmac
import json
import time
import os
import requests
import urllib3
from datetime import datetime
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from typing import Dict, Any, Optional, List
from dotenv import load_dotenv
import logging
import random

# 配置日志
logger = logging.getLogger(__name__)

# 加载环境变量（确保在导入Config前加载）
load_dotenv(dotenv_path=os.path.join(os.path.dirname(os.path.abspath(__file__)), '.env'))

# 导入配置
from app.config import Config

# 禁用不安全请求警告
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# 创建会话对象
session = requests.Session()

# 配置重试策略
retry_strategy = Retry(
    total=3,  # 最多重试3次
    backoff_factor=0.5,  # 重试间隔
    status_forcelist=[429, 500, 502, 503, 504],  # 需要重试的HTTP状态码
    allowed_methods=["GET", "POST"]  # 允许重试的请求方法
)

# 配置连接池
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=20,  # 连接池大小
    pool_maxsize=20  # 最大连接数
)

# 将连接池配置应用到会话
session.mount("http://", adapter)
session.mount("https://", adapter)

# 定义自定义错误类
class PortStatusError(Exception):
    """端口状态获取错误"""
    pass

def get_signature(secret_key: str, params: Dict[str, Any], method: str, timestamp: str) -> str:
    """生成接口签名
    
    Args:
        secret_key: 密钥
        params: 请求参数
        method: 请求方法
        timestamp: 时间戳
    
    Returns:
        str: 签名字符串
    """
    # 参数按字典顺序排序并拼接
    sorted_params = sorted(params.items())
    param_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
    
    # 拼接签名字符串
    string_to_sign = f"{method}&{param_str}&{timestamp}"
    
    # 使用HMAC-SHA1算法生成签名
    signature = hmac.new(
        secret_key.encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha1
    ).hexdigest()
    
    return signature

# 从配置获取API参数
secret_key = Config.API_SECRET_KEY or "tquO0s2pGW8cXzR7Qu5QgO7Gtv8u7JAH"
appid = Config.API_APPID
appcommid = Config.API_APPCOMMID
token = Config.API_TOKEN or "AppletUser:d57aed571109778f5056496c6580792b"

# 充电桩型号与端口数量映射配置
STATION_PORT_CONFIG = {
    # 默认充电桩配置，使用默认值
    "default": {
        "port_count": int(os.environ.get('DEFAULT_PORT_COUNT', '12')),
        "service_name": "充电服务"
    },
    # 93系列充电桩默认配置
    "93": {
        "port_count": 12,
        "service_name": "快速充电服务"
    },
    # 92系列充电桩默认配置
    "92": {
        "port_count": 12,
        "service_name": "标准充电服务"
    },
    # 特定型号充电桩配置
    "9313600954": {
        "port_count": 12,
        "service_name": "高速充电服务"
    },
    "9313601769": {
        "port_count": 12,
        "service_name": "高速充电服务"
    },
    "9241001156": {
        "port_count": 12,
        "service_name": "商用充电服务"
    }
}

# 添加模拟数据生成函数
def generate_mock_port_data(eq_num: str, port_count: Optional[int] = None) -> Dict[str, Any]:
    """生成模拟的充电桩端口数据
    
    Args:
        eq_num: 充电桩编号
        port_count: 端口数量，如果为None则根据充电桩型号自动选择
        
    Returns:
        dict: 模拟的充电桩端口状态数据
    """
    # 确定端口数量和服务名称
    if port_count is None:
        # 首先检查是否有针对特定充电桩ID的配置
        if eq_num in STATION_PORT_CONFIG:
            config = STATION_PORT_CONFIG[eq_num]
        # 检查充电桩系列配置（前两位数字）
        elif eq_num[:2] in STATION_PORT_CONFIG:
            config = STATION_PORT_CONFIG[eq_num[:2]]
        # 使用默认配置
        else:
            config = STATION_PORT_CONFIG["default"]
        
        port_count = config["port_count"]
        service_name = config["service_name"]
    else:
        service_name = "充电服务"
    
    logger.debug(f"为充电桩 {eq_num} 生成 {port_count} 个模拟端口")
    
    ports = []
    for i in range(1, port_count + 1):
        # 随机生成状态：60%概率空闲，40%概率占用
        status = "空闲" if random.random() < 0.6 else "占用"
        voltage = 220.0 if status == "占用" else 0.0
        current = random.uniform(8.0, 12.0) if status == "占用" else 0.0
        
        port_data = {
            "port": i,
            "status": status,
            "service": service_name,
            "voltage": voltage,
            "current": current,
            "timestamp": datetime.now().isoformat()
        }
        ports.append(port_data)
    
    return {
        "device_id": eq_num,
        "ports": ports
    }

# 添加是否使用模拟数据的标志（从配置或环境变量获取）
USE_MOCK_DATA = os.environ.get('USE_MOCK_DATA', 'false').lower() == 'true'

def get_port_status(eq_num: Optional[str] = None) -> Dict[str, Any]:
    """获取充电桩端口状态
    
    Args:
        eq_num (str, optional): 充电桩编号. 如果未提供，将返回空列表
    
    Returns:
        dict: 包含设备ID和端口状态列表的字典
    """
    if not eq_num:
        logger.warning("未提供充电桩编号")
        return {
            "device_id": "",
            "ports": []
        }
    
    # 如果设置为使用模拟数据，则直接返回模拟数据
    if USE_MOCK_DATA:
        logger.info(f"使用模拟数据 - 充电桩 {eq_num}")
        return generate_mock_port_data(eq_num)
    
    try:
        logger.debug(f"开始获取充电桩 {eq_num} 状态数据")
        
        # 使用动态时间戳
        timestamp = str(int(int(time.time()) * 1000))
        
        # 构造请求参数
        params = {"pno": eq_num}
        method = "GET"
        url = "https://app.mamcharge.com/device/detail"
        
        # 生成签名
        signature = get_signature(secret_key, params, method, timestamp)
        
        # 设置请求头
        headers = {
            "Host": "app.mamcharge.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 MicroMessenger/7.0.20.1781(0x6700143B) NetType/WIFI MiniProgramEnv/Windows WindowsWechat/WMPF WindowsWechat(0x63090c11)XWEB/11581",
            "client": "wechat",
            "Content-Type": "application/json",
            "timestamp": timestamp,
            "signature": signature,
            "appcommid": appcommid,
            "appid": appid,
            "forcecheck": "1",
            "token": token,
            "appversion": "1.3",
            "Accept": "*/*",
            "Referer": "https://servicewechat.com/wx7605335e224edc7b/196/page-frame.html"
        }
        
        # 发送请求，设置超时
        response = session.get(
            url, 
            params=params, 
            headers=headers, 
            verify=False,
            timeout=(3, 5)  # 连接超时3秒，读取超时5秒
        )
        response.raise_for_status()
        
        # 检查响应状态
        if response.status_code != 200:
            logger.warning(f"充电桩 {eq_num} API返回非200状态码: {response.status_code}")
            raise PortStatusError(f"API返回状态码: {response.status_code}")
        
        # 解析响应数据
        data = response.json()
        
        # 检查API响应内容
        if not data.get('success'):
            error_msg = data.get('msg', '未知错误')
            logger.warning(f"充电桩 {eq_num} API返回错误: {error_msg}")
            raise PortStatusError(f"API错误: {error_msg}")
        
        # 提取充电端口状态
        ports = []
        device_data = data.get('data', {})
        port_list = device_data.get('portList', [])
        
        for port in port_list:
            # 状态转换：0为空闲，10为占用
            status = "空闲" if port.get('status') == 0 else "占用"
            voltage = 220.0 if status == "占用" else 0.0
            current = 10.0 if status == "占用" else 0.0
            
            port_data = {
                "port": port.get('portId'),
                "status": status,
                "service": "充电服务",
                "voltage": voltage,
                "current": current,
                "timestamp": datetime.now().isoformat()
            }
            ports.append(port_data)
        
        result = {
            "device_id": eq_num,
            "ports": ports
        }
        
        logger.debug(f"成功获取充电桩 {eq_num} 状态，共 {len(ports)} 个端口")
        return result
        
    except requests.Timeout:
        # 超时错误
        logger.error(f"获取充电桩 {eq_num} 状态超时")
        logger.info(f"返回模拟数据 - 充电桩 {eq_num}（API超时）")
        return generate_mock_port_data(eq_num)
        
    except requests.RequestException as e:
        # 其他请求错误
        logger.error(f"获取充电桩 {eq_num} 状态请求失败: {str(e)}")
        logger.info(f"返回模拟数据 - 充电桩 {eq_num}（请求失败）")
        return generate_mock_port_data(eq_num)
        
    except PortStatusError as e:
        # 自定义API错误
        logger.error(f"获取充电桩 {eq_num} 状态API错误: {str(e)}")
        logger.info(f"返回模拟数据 - 充电桩 {eq_num}（API错误）")
        return generate_mock_port_data(eq_num)
        
    except json.JSONDecodeError as e:
        # JSON解析错误
        logger.error(f"解析充电桩 {eq_num} 状态响应JSON失败: {str(e)}")
        logger.info(f"返回模拟数据 - 充电桩 {eq_num}（JSON解析错误）")
        return generate_mock_port_data(eq_num)
        
    except Exception as e:
        # 未知错误
        logger.error(f"获取充电桩 {eq_num} 状态时发生未知错误: {str(e)}")
        logger.info(f"返回模拟数据 - 充电桩 {eq_num}（未知错误）")
        return generate_mock_port_data(eq_num)
