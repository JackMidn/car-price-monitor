# 汽车报价监测系统

一个用于抓取和分析汽车经销商报价数据的工具，支持从汽车之家、懂车帝、易车等平台采集数据，帮助快速了解目标车系在全国各地的真实成交价格与折扣行情。

## 功能特性

- **多平台采集**：支持汽车之家、懂车帝、易车同步抓取
- **本品 & 竞品对比**：可同时监测自有品牌与竞争品牌的报价动态
- **任务管理**：异步采集任务，支持单车系、整品牌、全量三种采集范围
- **数据查询**：按省份、城市、平台、日期多维度筛选报价记录
- **统计分析**：省份维度均价、折扣分析，平台数据量对比
- **可视化 UI**：内置 Web 界面，无需额外部署前端

## 技术栈

- **后端**：Python 3.11 + FastAPI + SQLAlchemy
- **数据库**：MySQL 8.0
- **部署**：Docker + Docker Compose

## 快速开始

### 环境要求

- Docker & Docker Compose
- 已有 MySQL 实例（或自行添加到 compose 中）

### 部署步骤

1. 克隆仓库

```bash
git clone https://github.com/JackMidn/car-price-monitor.git
cd car-price-monitor
```

2. 配置环境变量（可选，有默认值）

```bash
export DB_HOST=your_mysql_host
export DB_PORT=3306
export DB_USER=root
export DB_PASS=your_password
export DB_NAME=car_price
```

3. 启动服务

```bash
docker-compose up -d
```

4. 访问系统

打开浏览器访问 `http://localhost:8088`

### 本地开发

```bash
pip install -r requirements.txt

DB_HOST=127.0.0.1 DB_PASS=your_password uvicorn app.main:app --reload
```

## API 文档

启动后访问 `http://localhost:8088/docs` 查看完整的 Swagger API 文档。

主要接口：

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/series` | 车系列表 |
| POST | `/api/series` | 添加车系 |
| POST | `/api/crawl/start` | 启动采集任务 |
| GET | `/api/crawl/status/{id}` | 查询任务状态 |
| GET | `/api/prices` | 报价数据查询 |
| GET | `/api/stats/overview` | 数据概览统计 |
| GET | `/api/stats/province` | 按省份统计 |

## 项目结构

```
car-price-monitor/
├── app/
│   ├── main.py          # FastAPI 应用入口
│   ├── database.py      # 数据库连接配置
│   ├── models.py        # ORM 数据模型
│   ├── scraper.py       # 多平台爬虫核心
│   ├── routers/
│   │   └── api.py       # API 路由
│   └── static/          # 前端静态文件
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## License

MIT
