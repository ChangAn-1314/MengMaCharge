"""
充电桩监控系统 - 应用入口

这个模块是应用的入口点，负责创建和运行Flask应用。
"""

import os
from app import create_app

# 创建应用实例
app = create_app(os.environ.get('FLASK_ENV', 'development'))

if __name__ == '__main__':
    # 使用环境变量中的端口或默认端口
    port = int(os.environ.get('PORT', 5000))
    # 开发环境使用调试模式
    debug = os.environ.get('FLASK_ENV', 'development') == 'development'
    
    # 运行应用
    app.run(host='0.0.0.0', port=port, debug=debug)
