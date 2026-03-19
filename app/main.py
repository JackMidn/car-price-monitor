from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.database import engine, Base
from app.routers.api import router as api_router
from app.models import CarSeries
import sqlalchemy

app = FastAPI(title="汽车报价监测系统")


def init_db():
    from app.database import DB_USER, DB_PASS, DB_HOST, DB_PORT, SessionLocal
    tmp_url = f"mysql+pymysql://{DB_USER}:{DB_PASS}@{DB_HOST}:{DB_PORT}/?charset=utf8mb4"
    tmp_engine = sqlalchemy.create_engine(tmp_url)
    with tmp_engine.connect() as conn:
        conn.execute(sqlalchemy.text("CREATE DATABASE IF NOT EXISTS car_price DEFAULT CHARSET utf8mb4"))
        conn.commit()
    tmp_engine.dispose()
    Base.metadata.create_all(bind=engine)

    # 初始化车系种子数据
    db = SessionLocal()
    try:
        if db.query(CarSeries).count() == 0:
            seed = [
                # 东风日产本品
                CarSeries(name="轩逸", brand="东风日产", brand_type="own", autohome_id=425, yiche_slug="xuanyi"),
                CarSeries(name="天籁", brand="东风日产", brand_type="own", autohome_id=634, yiche_slug="tianlai"),
                CarSeries(name="奇骏", brand="东风日产", brand_type="own", autohome_id=64, yiche_slug="qijun"),
                CarSeries(name="逍客", brand="东风日产", brand_type="own", autohome_id=2086, yiche_slug="xiaoke"),
                CarSeries(name="劲客", brand="东风日产", brand_type="own", autohome_id=4305, yiche_slug="jingke"),
                # 竞品
                CarSeries(name="卡罗拉", brand="一汽丰田", brand_type="competitor", autohome_id=116, yiche_slug="kalola"),
                CarSeries(name="朗逸", brand="上汽大众", brand_type="competitor", autohome_id=553, yiche_slug="langyi"),
                CarSeries(name="思域", brand="东风本田", brand_type="competitor", autohome_id=168, yiche_slug="siyu"),
                CarSeries(name="凯美瑞", brand="广汽丰田", brand_type="competitor", autohome_id=166, yiche_slug="kaimeirui"),
                CarSeries(name="雅阁", brand="广汽本田", brand_type="competitor", autohome_id=67, yiche_slug="yage"),
                CarSeries(name="帕萨特", brand="上汽大众", brand_type="competitor", autohome_id=9, yiche_slug="pasate"),
                CarSeries(name="RAV4荣放", brand="一汽丰田", brand_type="competitor", autohome_id=2099, yiche_slug="rav4"),
                CarSeries(name="CR-V", brand="东风本田", brand_type="competitor", autohome_id=62, yiche_slug="crv"),
            ]
            db.add_all(seed)
            db.commit()
    finally:
        db.close()


init_db()

app.include_router(api_router)
app.mount("/static", StaticFiles(directory="app/static"), name="static")


@app.get("/")
async def index():
    return FileResponse("app/static/index.html")
