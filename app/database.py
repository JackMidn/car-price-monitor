import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库连接参数，优先读取环境变量，本地开发时使用默认值
DB_HOST = os.getenv("DB_HOST", "host.docker.internal")  # Docker 内访问宿主机 MySQL
DB_PORT = os.getenv("DB_PORT", "3306")
DB_USER = os.getenv("DB_USER", "root")
DB_PASS = os.getenv("DB_PASS", "your_password")
DB_NAME = os.getenv("DB_NAME", "car_price")

# 连接字符串，使用 pymysql 驱动，utf8mb4 支持中文及 emoji
DATABASE_URL = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/{DB_NAME}?charset=utf8mb4"

# 连接池配置：pool_pre_ping 自动检测失效连接，pool_size 控制并发连接数
engine = create_engine(DATABASE_URL, pool_pre_ping=True, pool_size=5)

# 会话工厂，每次请求通过 get_db() 获取独立 Session
SessionLocal = sessionmaker(bind=engine)

# ORM 模型基类，所有 Table 类继承它
Base = declarative_base()


def get_db():
    """FastAPI 依赖注入：每次请求创建数据库 Session，请求结束后自动关闭"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
