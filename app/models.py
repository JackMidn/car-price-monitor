from sqlalchemy import Column, Integer, String, Date, DateTime, Float, Boolean, Text, UniqueConstraint
from datetime import datetime
from app.database import Base


class CarSeries(Base):
    """
    车系配置表 - 跨平台 ID 映射

    每条记录代表一个需要监测的车系（如轩逸、天籁），
    存储该车系在各平台（汽车之家、懂车帝、易车）的唯一标识，
    brand_type 区分本品（own）和竞品（competitor）。
    """
    __tablename__ = "car_series"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True, comment="车系名称，如：轩逸、天籁")
    brand = Column(String(50), nullable=False, comment="品牌名称，如：东风日产")
    brand_type = Column(String(20), nullable=False, comment="own=本品牌 / competitor=竞品")
    autohome_id = Column(Integer, comment="汽车之家车系ID，用于调用 autohome API")
    dongchedi_id = Column(Integer, comment="懂车帝车系ID，可由搜索接口自动补全")
    yiche_slug = Column(String(100), comment="易车网 URL slug，如：xuanyi")
    is_active = Column(Boolean, default=True, comment="是否参与采集，设为 False 可暂停该车系")
    created_at = Column(DateTime, default=datetime.now)


class CarPrice(Base):
    """
    经销商报价记录表

    每条记录代表某天某经销商（或平台参考价）对某车系/车型的一次报价快照。
    price_level 区分车系级（series）和车型级（spec）两种粒度。
    唯一约束：同一天同一经销商同一车系/车型来源不重复插入（upsert 更新）。
    """
    __tablename__ = "car_price"

    id = Column(Integer, primary_key=True, autoincrement=True)
    crawl_date = Column(Date, nullable=False, comment="采集日期")
    province = Column(String(50), comment="所在省份")
    city = Column(String(50), comment="所在城市")
    dealer_id = Column(String(50), comment="经销商唯一ID（各平台自定义格式）")
    dealer_name = Column(String(200), comment="经销商名称")
    dealer_type = Column(String(20), comment="经销商类型，如：4S店、平台参考价")
    series_id = Column(Integer, nullable=False, comment="关联 car_series 表 ID")
    series_name = Column(String(100), nullable=False, comment="车系名称（冗余存储，方便查询）")
    spec_name = Column(String(200), comment="车型名称，如：2024款 轩逸 1.6L 自动舒适版")
    min_price = Column(Float, comment="经销商最低报价（万元）")
    max_price = Column(Float, comment="经销商最高报价（万元）")
    guide_price = Column(Float, comment="厂商指导价（万元）")
    guide_min_price = Column(Float, comment="指导价区间下限（万元）")
    guide_max_price = Column(Float, comment="指导价区间上限（万元）")
    max_discount = Column(Float, comment="最大优惠幅度（万元），= 指导价 - 报价")
    source = Column(String(20), nullable=False, default="autohome",
                    comment="数据来源：autohome / dongchedi / yiche")
    price_level = Column(String(10), default="series",
                         comment="价格粒度：series=车系级 / spec=车型级")
    raw_data = Column(Text, comment="原始 JSON 数据备份，用于后期溯源或字段扩展")
    created_at = Column(DateTime, default=datetime.now)

    __table_args__ = (
        # 联合唯一约束：同天、同经销商、同车系/车型、同来源只保留一条，重复时执行 UPDATE
        UniqueConstraint("crawl_date", "dealer_id", "series_name", "spec_name", "source",
                         name="uk_daily_dealer_series_spec"),
    )


class CrawlTask(Base):
    """
    采集任务记录表

    每次点击"开始采集"创建一条任务记录，后台异步执行并实时更新状态。
    scope 控制采集范围：single=仅该车系，brand=同品牌所有车系，all=全量采集。
    """
    __tablename__ = "crawl_task"

    id = Column(Integer, primary_key=True, autoincrement=True)
    series_name = Column(String(100), nullable=False, comment="触发采集的车系名称")
    series_id = Column(Integer, comment="关联 car_series 表 ID（可为空）")
    source = Column(String(100), nullable=False, comment="采集平台，逗号分隔，如：autohome,dongchedi")
    scope = Column(String(20), default="single",
                   comment="采集范围：single=单车系 / brand=整品牌 / all=全量")
    status = Column(String(20), default="pending",
                    comment="任务状态：pending=等待 / running=进行中 / done=完成 / error=出错")
    total = Column(Integer, default=0, comment="本次采集到的报价条数")
    message = Column(String(500), default="", comment="任务进度或错误信息")
    created_at = Column(DateTime, default=datetime.now)
    finished_at = Column(DateTime, nullable=True, comment="任务完成时间")
