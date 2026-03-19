import asyncio
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from app.database import get_db, SessionLocal
from app.models import CarPrice, CrawlTask, CarSeries
from app.scraper import run_crawl

router = APIRouter(prefix="/api")


# ========== 车系管理 ==========

@router.get("/series")
def list_series(brand_type: str = "", db: Session = Depends(get_db)):
    """车系列表"""
    q = db.query(CarSeries)
    if brand_type:
        q = q.filter(CarSeries.brand_type == brand_type)
    rows = q.order_by(CarSeries.brand_type, CarSeries.brand, CarSeries.name).all()
    return [
        {
            "id": s.id, "name": s.name, "brand": s.brand,
            "brand_type": s.brand_type,
            "autohome_id": s.autohome_id,
            "dongchedi_id": s.dongchedi_id,
            "yiche_slug": s.yiche_slug,
            "is_active": s.is_active,
        }
        for s in rows
    ]


@router.post("/series")
def add_series(
    name: str, brand: str, brand_type: str = "competitor",
    autohome_id: int = None, dongchedi_id: int = None,
    yiche_slug: str = None, db: Session = Depends(get_db),
):
    """添加车系"""
    exists = db.query(CarSeries).filter(CarSeries.name == name).first()
    if exists:
        return {"error": f"车系「{name}」已存在", "id": exists.id}
    s = CarSeries(
        name=name, brand=brand, brand_type=brand_type,
        autohome_id=autohome_id, dongchedi_id=dongchedi_id, yiche_slug=yiche_slug,
    )
    db.add(s)
    db.commit()
    db.refresh(s)
    return {"id": s.id, "message": f"已添加「{name}」"}


@router.put("/series/{series_id}")
def update_series(
    series_id: int,
    name: str = None, brand: str = None, brand_type: str = None,
    autohome_id: int = None, dongchedi_id: int = None,
    yiche_slug: str = None, is_active: bool = None,
    db: Session = Depends(get_db),
):
    """更新车系信息"""
    s = db.query(CarSeries).get(series_id)
    if not s:
        return {"error": "车系不存在"}
    if name is not None:
        s.name = name
    if brand is not None:
        s.brand = brand
    if brand_type is not None:
        s.brand_type = brand_type
    if autohome_id is not None:
        s.autohome_id = autohome_id
    if dongchedi_id is not None:
        s.dongchedi_id = dongchedi_id
    if yiche_slug is not None:
        s.yiche_slug = yiche_slug
    if is_active is not None:
        s.is_active = is_active
    db.commit()
    return {"message": "更新成功"}


@router.delete("/series/{series_id}")
def delete_series(series_id: int, db: Session = Depends(get_db)):
    """删除车系"""
    s = db.query(CarSeries).get(series_id)
    if not s:
        return {"error": "车系不存在"}
    db.delete(s)
    db.commit()
    return {"message": f"已删除「{s.name}」"}


# ========== 采集任务 ==========

@router.post("/crawl/start")
async def start_crawl(
    series_name: str,
    sources: str = "autohome,dongchedi,yiche",
    scope: str = "single",
    db: Session = Depends(get_db),
):
    """启动采集任务
    sources: 逗号分隔的平台列表 autohome,dongchedi,yiche
    scope: single=单车系, brand=整品牌, all=全部
    """
    source_list = [s.strip() for s in sources.split(",") if s.strip()]
    task = CrawlTask(
        series_name=series_name,
        source=",".join(source_list),
        scope=scope,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    asyncio.create_task(run_crawl(task.id, SessionLocal, source_list))
    return {"task_id": task.id, "message": f"已启动「{series_name}」采集任务 ({','.join(source_list)})"}


@router.get("/crawl/status/{task_id}")
def crawl_status(task_id: int, db: Session = Depends(get_db)):
    """查询任务状态"""
    task = db.query(CrawlTask).get(task_id)
    if not task:
        return {"error": "任务不存在"}
    return {
        "id": task.id,
        "series_name": task.series_name,
        "source": task.source,
        "scope": task.scope,
        "status": task.status,
        "total": task.total,
        "message": task.message,
        "created_at": str(task.created_at) if task.created_at else None,
        "finished_at": str(task.finished_at) if task.finished_at else None,
    }


@router.get("/crawl/history")
def crawl_history(db: Session = Depends(get_db)):
    """历史任务列表"""
    tasks = db.query(CrawlTask).order_by(CrawlTask.id.desc()).limit(30).all()
    return [
        {
            "id": t.id,
            "series_name": t.series_name,
            "source": t.source,
            "scope": t.scope,
            "status": t.status,
            "total": t.total,
            "message": t.message,
            "created_at": str(t.created_at) if t.created_at else None,
        }
        for t in tasks
    ]


# ========== 数据查询 ==========

@router.get("/prices")
def get_prices(
    series_name: str = "",
    province: str = "",
    city: str = "",
    source: str = "",
    crawl_date: str = "",
    brand_type: str = "",
    page: int = 1,
    size: int = 20,
    db: Session = Depends(get_db),
):
    """查询报价数据"""
    q = db.query(CarPrice)
    if series_name:
        q = q.filter(CarPrice.series_name.like(f"%{series_name}%"))
    if province:
        q = q.filter(CarPrice.province == province)
    if city:
        q = q.filter(CarPrice.city == city)
    if source:
        q = q.filter(CarPrice.source == source)
    if crawl_date:
        q = q.filter(CarPrice.crawl_date == crawl_date)
    if brand_type:
        # 关联car_series表筛选本品/竞品
        series_ids = [s.id for s in db.query(CarSeries.id).filter(CarSeries.brand_type == brand_type).all()]
        if series_ids:
            q = q.filter(CarPrice.series_id.in_(series_ids))

    total = q.count()
    rows = q.order_by(CarPrice.crawl_date.desc(), CarPrice.source, CarPrice.province, CarPrice.city)\
        .offset((page - 1) * size).limit(size).all()

    return {
        "total": total,
        "page": page,
        "size": size,
        "data": [
            {
                "id": r.id,
                "crawl_date": str(r.crawl_date),
                "province": r.province,
                "city": r.city,
                "dealer_id": r.dealer_id,
                "dealer_name": r.dealer_name,
                "dealer_type": r.dealer_type,
                "series_name": r.series_name,
                "spec_name": r.spec_name if r.spec_name else None,
                "min_price": r.min_price,
                "max_price": r.max_price,
                "guide_price": r.guide_price,
                "guide_min_price": r.guide_min_price,
                "guide_max_price": r.guide_max_price,
                "max_discount": r.max_discount,
                "source": r.source,
                "price_level": r.price_level,
            }
            for r in rows
        ],
    }


# ========== 统计 ==========

@router.get("/stats/overview")
def stats_overview(db: Session = Depends(get_db)):
    """数据概览统计"""
    total_records = db.query(func.count(CarPrice.id)).scalar() or 0
    total_series = db.query(func.count(distinct(CarPrice.series_name))).scalar() or 0
    total_dealers = db.query(func.count(distinct(CarPrice.dealer_id))).scalar() or 0
    total_cities = db.query(func.count(distinct(CarPrice.city))).scalar() or 0
    latest_date = db.query(func.max(CarPrice.crawl_date)).scalar()

    # 各平台数据量
    source_stats = db.query(
        CarPrice.source, func.count(CarPrice.id)
    ).group_by(CarPrice.source).all()
    source_map = {s: c for s, c in source_stats}

    return {
        "total_records": total_records,
        "total_series": total_series,
        "total_dealers": total_dealers,
        "total_cities": total_cities,
        "latest_date": str(latest_date) if latest_date else "暂无数据",
        "source_stats": source_map,
    }


@router.get("/stats/province")
def stats_by_province(series_name: str = "", source: str = "", db: Session = Depends(get_db)):
    """按省份统计"""
    q = db.query(
        CarPrice.province,
        func.count(CarPrice.id).label("count"),
        func.avg(CarPrice.min_price).label("avg_min"),
        func.avg(CarPrice.max_discount).label("avg_discount"),
    )
    if series_name:
        q = q.filter(CarPrice.series_name.like(f"%{series_name}%"))
    if source:
        q = q.filter(CarPrice.source == source)
    rows = q.filter(CarPrice.province != "").group_by(CarPrice.province)\
        .order_by(func.count(CarPrice.id).desc()).all()
    return [
        {
            "province": r.province, "count": r.count,
            "avg_min_price": round(r.avg_min or 0, 2),
            "avg_discount": round(r.avg_discount or 0, 2),
        }
        for r in rows
    ]


@router.get("/filters")
def get_filters(db: Session = Depends(get_db)):
    """获取筛选项"""
    series = db.query(distinct(CarPrice.series_name)).all()
    provinces = db.query(distinct(CarPrice.province)).filter(CarPrice.province != "").all()
    dates = db.query(distinct(CarPrice.crawl_date)).order_by(CarPrice.crawl_date.desc()).limit(30).all()
    sources = db.query(distinct(CarPrice.source)).all()
    return {
        "series": [s[0] for s in series],
        "provinces": [p[0] for p in provinces],
        "dates": [str(d[0]) for d in dates],
        "sources": [s[0] for s in sources],
    }


@router.get("/series/suggest")
def series_suggest(q: str = "", db: Session = Depends(get_db)):
    """车系名称联想(从数据库查)"""
    query = db.query(CarSeries)
    if q:
        query = query.filter(CarSeries.name.like(f"%{q}%"))
    rows = query.filter(CarSeries.is_active == True).all()
    return [r.name for r in rows]
