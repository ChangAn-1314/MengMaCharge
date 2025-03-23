# 充电桩监控系统

## 项目介绍
充电桩监控系统是一个用于实时监控和管理充电站点的Web应用，能够显示充电端口的状态、电压、电流等信息，支持异步更新和缓存机制。

## 主要特性
- 实时监控充电桩端口状态
- 支持多个充电站点管理
- 异步任务处理提高系统响应速度
- 缓存机制减少API请求和数据库访问
- 自动刷新和手动刷新功能
- RESTful API接口
- 响应式Web界面

## 性能优化
系统在以下几个方面进行了性能优化：

### 1. 缓存优化
- 使用Redis缓存充电桩状态，减少重复API请求
- 缓存自动过期机制，确保数据时效性
- 智能缓存刷新策略，避免不必要的更新

### 2. 异步处理
- Celery任务队列处理状态更新
- 任务重试机制确保数据可靠性
- 并发工作进程处理多个充电桩请求

### 3. 数据库优化
- 批量数据库操作减少数据库连接开销
- 数据库连接池管理连接资源
- 索引优化提高查询速度

### 4. 网络请求优化
- HTTP连接池重用连接
- 请求重试机制处理网络波动
- 超时控制避免长时间阻塞

## 技术栈
- 后端：Python + Flask + SQLAlchemy + Celery
- 数据库：MySQL
- 缓存：Redis
- 前端：HTML + CSS + JavaScript + Vue.js
- 部署：Docker（可选）

## 系统架构
```
+---------------+     +-------------+     +-----------+
| Web界面/API   | --> | Flask应用    | --> | 数据库    |
+---------------+     +-------------+     +-----------+
                      |  |
                      |  v
                   +--+-------+     +------------+
                   | Celery  | --> | 外部API     |
                   +----------+     +------------+
                      |
                      v
                   +----------+
                   | Redis    |
                   +----------+
```

## 安装部署

### 环境要求
- Python 3.8+
- MySQL 5.7+
- Redis 6.0+

### 基础安装
1. 克隆代码库
```bash
git clone https://github.com/yourusername/charging-station-monitor.git
cd charging-station-monitor
```

2. 创建并激活虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

4. 配置环境变量
```bash
cp .env.example .env
# 编辑.env文件，设置数据库和API密钥等配置
```

5. 初始化数据库
```bash
flask init-db
```

6. 运行应用
```bash
flask run
```

### 使用Docker部署（可选）
```bash
docker-compose up -d
```

## 使用说明

### Web界面
访问`http://localhost:5000`查看充电桩监控界面，可以：
- 查看充电桩列表和状态
- 查看端口详细信息
- 手动刷新状态

### API接口
- `GET /api/stations` - 获取所有充电桩列表
- `GET /api/stations/<station_id>` - 获取特定充电桩信息
- `GET /api/ports` - 获取默认充电桩的端口状态

## 开发指南

### 项目结构
```
charging-station-monitor/
├── app/                    # 应用主目录
│   ├── __init__.py         # 应用初始化
│   ├── config.py           # 配置文件
│   ├── models/             # 数据模型
│   ├── services/           # 业务逻辑
│   ├── repositories/       # 数据访问
│   ├── blueprints/         # 蓝图模块
│   ├── cache.py            # 缓存处理
│   ├── tasks.py            # 异步任务
│   ├── static/             # 静态资源
│   └── templates/          # 模板文件
├── port_status.py          # 外部API访问
├── celery_worker.py        # Celery工作进程
├── initialize_system.py    # 系统初始化脚本
├── requirements.txt        # 依赖清单
├── .env.example            # 环境变量模板
└── README.md               # 项目说明
```

### 添加新功能
1. 实现数据模型（`app/models/`）
2. 添加数据访问层（`app/repositories/`）
3. 实现业务逻辑（`app/services/`）
4. 创建API路由（`app/blueprints/`）

## 故障排除
- 确保MySQL和Redis服务正常运行
- 检查日志文件中的错误信息
- 确保环境变量正确设置
- 使用`flask test-connection`测试数据库连接

## 许可证
本项目采用MIT许可证。
