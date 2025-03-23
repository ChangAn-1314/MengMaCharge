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
from typing import Dict, Any, Optional
from dotenv import load_dotenv

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
    status_forcelist=[500, 502, 503, 504]  # 需要重试的HTTP状态码
)

# 配置连接池
adapter = HTTPAdapter(
    max_retries=retry_strategy,
    pool_connections=10,  # 连接池大小
    pool_maxsize=10  # 最大连接数
)

# 将连接池配置应用到会话
session.mount("http://", adapter)
session.mount("https://", adapter)

class PortStatusError(Exception):
    """端口状态获取错误"""
    pass

def get_signature(secret_key, params, method, timestamp):
    # 规范化处理参数（递归排序键名）
    def normalize_params(data):
        if isinstance(data, dict):
            return {k: normalize_params(v) for k, v in sorted(data.items())}
        elif isinstance(data, list):
            return sorted([normalize_params(item) for item in data])
        else:
            return data

    normalized = normalize_params(params)
    
    # 构造待签名字符串
    if method.upper() == "POST":
        str_to_sign = json.dumps(normalized, separators=(",", ":")) + str(timestamp)
    else:
        param_pairs = []
        for key in sorted(normalized.keys()):
            param_pairs.append(f"{key}={normalized[key]}")
        str_to_sign = "&".join(param_pairs) + str(timestamp)
    
    # 使用 HMAC-MD5 加密算法
    signature = hmac.new(
        secret_key.encode("utf-8"),
        str_to_sign.encode("utf-8"),
        digestmod=hashlib.md5
    ).hexdigest()
    return signature

# 从配置获取API参数
secret_key = Config.API_SECRET_KEY or "tquO0s2pGW8cXzR7Qu5QgO7Gtv8u7JAH"
appid = Config.API_APPID
appcommid = Config.API_APPCOMMID
token = Config.API_TOKEN or "AppletUser:d57aed571109778f5056496c6580792b"

def get_port_status(eq_num: Optional[str] = None) -> Dict[str, Any]:
    """获取充电桩端口状态
    
    Args:
        eq_num (str, optional): 充电桩编号. 如果未提供，将返回空列表
    
    Returns:
        dict: 包含设备ID和端口状态列表的字典
    """
    if not eq_num:
        print("未提供充电桩编号")
        return {
            "device_id": "",
            "ports": []
        }
    
    try:
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
        
        # 解析响应数据
        data = response.json()
        
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
        return result
        
    except requests.Timeout:
        # 超时错误
        return {
            "device_id": eq_num,
            "ports": []
        }
    except requests.RequestException as e:
        # 其他请求错误
        print(f"请求失败: {str(e)}")
        return {
            "device_id": eq_num,
            "ports": []
        }
    except Exception as e:
        print(f"处理数据时出错: {str(e)}")
        return {
            "device_id": eq_num,
            "ports": []
        }
