from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Boolean, Text, UniqueConstraint
from datetime import datetime
from app.database import Base


class CarSeries(Base):
    """车系管理表 - 跨平台ID映射"""
    __tablename__ = "car_series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="车系名称")
    brand = Column(String(50), nullable=False, comment="品牌")
    brand_type = Column(String(20), nullable=False, comment="own=本品/competitor=竞品")
    autohome_id = Column(Integer, comment="汽车之家车系ID")
    dongchedi_id = Column(Integer, comment="懂车帝车系ID")
    yiche_slug = Column(String(100), comment="易车网URL slug")
    is_active = Column(Boolean, default=True, comment="是否启用采集")
    created_at = Column(DateTime, default=datetime.now)


class CarPrice(Base):
    """经销商报价数据"""
    __tablename__ = "car_price"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crawl_date = Column(Date, nullable=False, comment="采集日期")
    province = Column(String(50), comment="省份")
    city = Column(String(50), comment="城市")
    dealer_id = Column(String(50), comment="经销商ID(各平台)")
    dealer_name = Column(String(200), comment="经销商名称")
    dealer_type = Column(String(20), comment="经销商类型(4S店等)")
    series_id = Column(Integer, nullable=False, comment="car_series表ID")
    series_name = Column(String(100), nullable=False, comment="车系名称")
    spec_name = Column(String(200), comment="车型名称(款型级别)")
    min_price = Column(Float, comment="最低报价(万)")
    max_price = Column(Float, comment="最高报价(万)")
    guide_price = Column(Float, comment="指导价(万)")
    guide_min_price = Column(Float, comment="指导价最低(万)")
    guide_max_price = Column(Float, comment="指导价最高(万)")
    max_discount = Column(Float, comment="最大优惠(万)")
    source = Column(String(20), nullable=False, default="autohome", comment="数据来源: autohome/dongchedi/yiche")
    price_level = Column(String(10), default="series", comment="价格级别: series=车系/spec=车型")
    raw_data = Column(Text, comment="原始JSON数据备份")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        UniqueConstraint("crawl_date", "dealer_id", "series_name", "spec_name", "source",
                         name="uk_daily_dealer_series_spec"),
    )


class CrawlTask(Base):
    """采集任务"""
    __tablename__ = "crawl_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    series_name = Column(String(100), nullable=False, comment="车系名称")
    series_id = Column(Integer, comment="car_series表ID")
    source = Column(String(100), nullable=False, comment="数据来源(逗号分隔)")
    scope = Column(String(20), default="single", comment="single=单车系/brand=整品牌/all=全部")
    status = Column(String(20), default="pending", comment="pending/running/done/error")
    total = Column(Integer, default=0, comment="总记录数")
    message = Column(String(500), default="")
    created_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime, nullable=True)
