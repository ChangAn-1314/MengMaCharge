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
│   ├── routes.py          # 路由定义
│   ├── controllers/       # 控制器
│   ├── models/           # 数据模型
│   ├── static/           # 静态文件
│   └── templates/        # HTML模板
├── instance/             # 实例配置
├── port_status.py        # 端口状态处理
├── requirements.txt      # 项目依赖
└── run.py               # 应用入口
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

3. 配置数据库：
   - 创建MySQL数据库
   - 配置数据库连接信息（在.env文件中）

4. 运行应用：
```bash
python run.py
```

## 配置说明

在项目根目录创建`.env`文件，包含以下配置：

```env
FLASK_APP=run.py
FLASK_ENV=development
DATABASE_URL=mysql+pymysql://username:password@localhost/dbname
```

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
