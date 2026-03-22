# Trea Finance Lab - 金融交易实验室

一个基于Web的金融交易模拟平台，提供学习实验区和自由交易区，让用户使用10万虚拟本金体验真实股票交易。

## 功能特点

### 🎯 核心功能
- 📈 **实时股价查询** - 使用 yfinance 获取真实股票数据，支持模拟数据模式
- 💰 **虚拟交易** - 买入/卖出股票，体验真实交易流程
- 📊 **资产管理** - 实时计算持仓市值和盈亏
- 💾 **数据持久化** - 使用 JSON 保存数据，重启后数据不丢失
- 🔒 **数据隔离** - 学习实验区与自由交易区数据完全隔离
- 📱 **响应式设计** - 适配不同屏幕尺寸

### 🎓 学习实验区
- 🏫 **实验大厅** - 提供3个不同难度的结构化实验
- 🧪 **实验沙盒** - 基于历史数据的模拟交易环境
- 📋 **实验报告** - 交易结果分析和复盘总结
- 📈 **学习进度追踪** - 记录实验完成情况

### 🎮 自由交易区
- 📊 **K线图表** - 股票价格走势可视化
- 🔍 **股票搜索** - 快速查找股票
- ⭐ **自选股列表** - 关注感兴趣的股票
- 💼 **账户总览** - 实时资产状况
- 📋 **交易记录** - 完整的买卖历史
- 📦 **持仓管理** - 详细的持仓信息

## 安装依赖

```bash
pip3 install -r requirements.txt
```

## 快速开始

### 启动Web服务器

```bash
# 进入项目目录
cd trea_finance_lab

# 启动服务器
python3 app.py
```

### 访问应用

打开浏览器，访问：
```
http://127.0.0.1:5004
```

## 项目结构

```
trea_finance_lab/
├── app.py               # Flask主应用，处理路由和API
├── simulator.py         # 交易模拟器核心逻辑
├── data_fetcher.py      # 股票数据获取模块
├── requirements.txt     # 项目依赖
├── portfolio.json       # 自由交易区数据文件
├── experiment_*.json    # 实验区数据文件（自动生成）
└── templates/           # HTML模板
    ├── index.html       # 首页
    ├── lab.html         # 学习实验区
    ├── experiment.html  # 实验沙盒
    ├── experiment_report.html  # 实验报告
    ├── trade.html       # 自由交易区
    ├── trade_history.html      # 交易历史
    ├── trade_stock_detail.html # 股票详情
    └── account.html     # 我的账户
```

## 技术栈

### 后端
- Python 3.9+
- Flask - Web框架
- yfinance - 股票数据获取
- JSON - 数据存储

### 前端
- HTML5 + CSS3
- JavaScript (原生)
- ECharts - K线图表可视化
- Responsive Design - 响应式布局

## 核心API

### 自由交易区API
- `GET /api/trade/price/<symbol>` - 获取股票价格
- `POST /api/trade/buy` - 买入股票
- `POST /api/trade/sell` - 卖出股票
- `GET /api/trade/portfolio` - 获取投资组合
- `GET /api/trade/history` - 获取交易历史
- `POST /api/trade/reset` - 重置账户

### 实验区API
- `GET /api/experiment/<id>/price/<symbol>` - 获取实验区股票价格
- `POST /api/experiment/<id>/buy` - 实验区买入股票
- `POST /api/experiment/<id>/sell` - 实验区卖出股票
- `GET /api/experiment/<id>/portfolio` - 获取实验区投资组合
- `GET /api/experiment/<id>/history` - 获取实验区交易历史
- `POST /api/experiment/<id>/reset` - 重置实验账户

## 使用指南

### 学习实验区
1. 访问首页，点击"开始学习"进入实验大厅
2. 选择一个实验，点击"开始实验"进入沙盒环境
3. 在沙盒中进行模拟交易，体验真实的交易流程
4. 完成实验后，点击"查看实验报告"查看分析结果

### 自由交易区
1. 访问首页，点击"开始交易"进入自由交易区
2. 在左侧栏搜索股票或从自选股列表中选择
3. 右侧会显示K线图和交易面板
4. 输入交易数量，点击"买入"或"卖出"执行交易
5. 底部标签页查看持仓、委托和成交记录

## 注意事项

1. **API 限制**: yfinance 有请求频率限制，频繁查询可能会被暂时限制
2. **数据延迟**: 股价数据可能有15分钟延迟，仅供模拟使用
3. **虚拟资金**: 所有资金均为虚拟，不涉及真实交易
4. **数据安全**: 数据文件包含交易记录，请妥善保管
5. **K线图**: 当前使用模拟数据，未来将接入真实历史数据

## 支持的股票

支持所有 Yahoo Finance 可查询的股票代码，例如：
- AAPL (苹果)
- GOOGL (谷歌)
- MSFT (微软)
- TSLA (特斯拉)
- AMZN (亚马逊)
- META (Meta)
- NVDA (英伟达)
- 等等...

## 未来规划

1. **K线图优化** - 接入真实历史数据，添加技术指标
2. **委托系统** - 实现完整的委托下单功能
3. **实验报告增强** - 更详细的交易分析和策略评估
4. **股票搜索扩展** - 支持更多股票和高级搜索
5. **用户系统** - 多用户支持和账户管理
6. **实时数据** - 接入实时股票数据API
7. **移动应用** - 开发移动版客户端

## 许可证

MIT License