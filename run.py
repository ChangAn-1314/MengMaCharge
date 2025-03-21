"""
充电桩监控系统 - 应用入口

这个模块是应用的入口点，负责创建和运行Flask应用。
"""

from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
