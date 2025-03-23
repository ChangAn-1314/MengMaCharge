# 充电桩监控系统

一个基于Flask和Vue.js的充电桩端口状态监控系统。

## 功能特点

- 实时监控多个充电桩的端口状态
- 自动刷新（每5秒更新一次）
- 支持手动刷新数据
- 清晰的状态显示（空闲/占用）
- 响应式布局，支持移动设备

## 技术栈

- 后端：Flask + SQLAlchemy
- 前端：Vue.js 3 + Bootstrap 5
- 数据库：MySQL

## 项目结构

```
MengMa/
├── app/                    # 应用主目录
│   ├── __init__.py        # 应用初始化
│   ├── config.py          # 配置管理
│   ├── init_db.py         # 数据库初始化
│   ├── blueprints/        # 蓝图模块
│   │   ├── __init__.py    # 蓝图初始化
│   │   ├── api.py         # API蓝图
│   │   └── main.py        # 主页蓝图
│   ├── services/          # 服务层
│   │   ├── __init__.py    # 服务层初始化
│   │   └── station_service.py  # 充电桩服务
│   ├── repositories/      # 数据访问层
│   │   ├── __init__.py    # 数据访问层初始化
│   │   └── station_repository.py  # 充电桩数据访问
│   ├── models/            # 数据模型
│   ├── static/            # 静态文件
│   └── templates/         # HTML模板
├── initialize_system.py   # 系统初始化脚本
├── port_status.py         # 外部API模块
├── .env.example           # 环境变量模板
├── requirements.txt       # 项目依赖
└── run.py                 # 应用入口
```

## 安装说明

1. 创建虚拟环境：
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 初始化系统：
```bash
python initialize_system.py
```
初始化脚本会引导您设置数据库配置，并创建必要的数据库表和初始数据。

4. 运行应用：
```bash
python run.py
```

## 配置说明

系统使用`.env`文件管理配置。您可以复制`.env.example`文件并重命名为`.env`，然后根据您的环境修改配置参数。

主要配置项包括：

```env
# 应用配置
FLASK_APP=run.py
FLASK_ENV=development  # development, testing, production
SECRET_KEY=your_secret_key_here

# 数据库配置
DB_USER=username
DB_PASSWORD=password
DB_HOST=localhost
DB_NAME=port_status_db

# API认证配置 (充电桩API接口)
API_SECRET_KEY=your_api_secret_key
API_APPID=mengma
API_APPCOMMID=MCB_INSTANCE_WECHAT_APP
API_TOKEN=your_api_token

# 缓存配置
CACHE_TIMEOUT=5  # 缓存过期时间（秒）
```

## 系统架构

系统采用分层架构设计，包括：

1. **表示层**：蓝图和路由，处理HTTP请求和响应
2. **服务层**：业务逻辑实现，如充电桩状态更新
3. **数据访问层**：封装数据库操作，提供数据访问接口
4. **模型层**：定义数据模型和关系

这种分层架构使系统具有良好的可维护性和可扩展性。

## API接口

### 获取所有充电桩状态
- URL: `/api/stations`
- 方法: GET
- 返回: 所有充电桩及其端口状态

### 获取单个充电桩状态
- URL: `/api/ports`
- 方法: GET
- 返回: 默认充电桩的端口状态

## 开发说明

- 代码规范遵循PEP 8
- 使用类型注解
- 所有函数都有文档字符串
- 使用统一的错误处理机制

## 维护者

- [An]

## 许可证

MIT
