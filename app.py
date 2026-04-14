"""
Trea Finance Lab - Web版本
Flask主应用
"""

from flask import Flask, render_template, request, jsonify, session
from simulator import TradingSimulator
from data_fetcher import DataFetcher
import os
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'trea-finance-lab-secret-key'

# 初始化组件
fetcher = DataFetcher(cache_duration=60)

# 生成贵州茅台2012-2014年模拟股价数据
def generate_maotai_stock_data():
    """生成贵州茅台2012-2014年模拟股价数据"""
    data = {
        'dates': [],
        'prices': [],
        'events': []
    }
    
    # 2012年初：起始价格200元
    start_date = datetime(2012, 1, 1)
    current_price = 200.0
    
    # 生成2012年1月-2013年6月的下跌趋势（腰斩）
    for i in range(540):  # 约18个月
        date = start_date + timedelta(days=i)
        data['dates'].append(date.strftime('%Y-%m-%d'))
        
        # 模拟缓慢下跌，平均每天下跌约0.1元
        current_price -= 0.1
        if current_price < 95:
            current_price = 95  # 最低跌至95元左右
        data['prices'].append(round(current_price, 2))
        
        # 添加关键事件
        if i == 180:  # 2012年中
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '新闻报道：高端白酒消费受限'
            })
        if i == 360:  # 2013年初
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '券商下调茅台盈利预测'
            })
        if i == 500:  # 2013年末
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'crash',
                'content': '单日大跌8%，市场出现"茅台神话终结"的恐慌言论',
                'question': '股价已从高点跌去超过50%，新闻一片悲观。作为股东，你现在应该：A) 跟随恐慌卖出；B) 持有不动，相信品牌；C) 趁机买入更多？'
            })
    
    # 生成2014年震荡筑底阶段
    for i in range(540, 720):  # 约6个月
        date = start_date + timedelta(days=i)
        data['dates'].append(date.strftime('%Y-%m-%d'))
        
        # 模拟100元左右震荡
        current_price = 95 + random.uniform(-2, 3)
        data['prices'].append(round(current_price, 2))
        
        if i == 600:  # 2014年中
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '财报显示，茅台净利润依然稳健'
            })
        if i == 660:  # 2014年末
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '民间消费开始承接政务需求'
            })
    
    return data

# 自由交易区模拟器
trade_simulator = TradingSimulator(initial_balance=100000, portfolio_file='portfolio.json')

# 学习实验区模拟器（数据隔离）
experiment_simulators = {}

def get_experiment_simulator(experiment_id):
    """获取指定实验的模拟器实例"""
    if experiment_id not in experiment_simulators:
        experiment_simulators[experiment_id] = TradingSimulator(
            initial_balance=248500, 
            portfolio_file=f'experiment_{experiment_id}.json'
        )
    return experiment_simulators[experiment_id]

# 实验数据
experiments = [
    {
        'id': '1',
        'title': '认识波动：股权思维植入',
        'description': '理解股价波动是常态，建立"股权所有者"心态，避免被短期价格牵着走',
        'difficulty': '入门',
        'duration': '20分钟',
        'image': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=financial%20trading%20basics%20education&image_size=square'
    },
    {
        'id': '2',
        'title': '定投实验：可视化对比与心理提示',
        'description': '体验定投策略如何平滑成本、降低择时压力，对比一次性买入的心理差异',
        'difficulty': '中级',
        'duration': '30分钟',
        'image': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=stock%20market%20trend%20analysis&image_size=square'
    },
    {
        'id': '3',
        'title': '抗跌组合：构建逻辑与归因',
        'description': '学习构建分散配置的组合，理解不同行业配置如何降低整体风险',
        'difficulty': '高级',
        'duration': '40分钟',
        'image': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=diversified%20investment%20portfolio%20risk%20management&image_size=square'
    }
]

@app.route('/')
def index():
    """首页 - 门户页面"""
    return render_template('index.html')

@app.route('/lab')
def lab():
    """学习实验区 - 实验大厅"""
    return render_template('lab.html', experiments=experiments)

@app.route('/lab/experiment/<experiment_id>')
def experiment(experiment_id):
    """实验沙盒 - 基于历史数据的模拟交易界面"""
    experiment_data = next((exp for exp in experiments if exp['id'] == experiment_id), None)
    if not experiment_data:
        return render_template('404.html'), 404
    
    simulator = get_experiment_simulator(experiment_id)
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    
    return render_template('experiment.html', 
                          experiment=experiment_data, 
                          portfolio=portfolio)

@app.route('/lab/report/<experiment_id>')
def experiment_report(experiment_id):
    """实验报告 - 实验完成后的复盘页面"""
    experiment_data = next((exp for exp in experiments if exp['id'] == experiment_id), None)
    if not experiment_data:
        return render_template('404.html'), 404
    
    simulator = get_experiment_simulator(experiment_id)
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    transactions = simulator.get_transaction_history()
    
    return render_template('experiment_report.html', 
                          experiment=experiment_data, 
                          portfolio=portfolio, 
                          transactions=transactions)

@app.route('/trade')
def trade():
    """自由交易区 - 复用旧项目的模拟交易界面"""
    portfolio = trade_simulator.get_portfolio_value(fetcher.get_price)
    transactions = trade_simulator.get_transaction_history()
    return render_template('trade.html', portfolio=portfolio, transactions=transactions)

@app.route('/account')
def account():
    """我的账户 - 用户数据汇总页面"""
    trade_portfolio = trade_simulator.get_portfolio_value(fetcher.get_price)
    
    # 计算学习进度
    completed_experiments = 0
    for exp_id in experiment_simulators:
        simulator = get_experiment_simulator(exp_id)
        if simulator.get_transaction_history():
            completed_experiments += 1
    
    learning_progress = {
        'total': len(experiments),
        'completed': completed_experiments,
        'percentage': (completed_experiments / len(experiments)) * 100 if experiments else 0
    }
    
    return render_template('account.html', 
                          trade_portfolio=trade_portfolio, 
                          learning_progress=learning_progress)

# 自由交易区API
@app.route('/api/trade/price/<symbol>')
def get_trade_price(symbol):
    """获取股票价格API"""
    price = fetcher.get_price(symbol)
    if price:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'price': price
        })
    else:
        return jsonify({
            'success': False,
            'error': f'无法获取 {symbol} 的价格'
        }), 400

@app.route('/api/trade/buy', methods=['POST'])
def buy_trade_stock():
    """买入股票API"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    quantity = data.get('quantity', 0)
    
    if not symbol or quantity <= 0:
        return jsonify({
            'success': False,
            'error': '参数错误'
        }), 400
    
    # 获取当前价格
    price = fetcher.get_price(symbol)
    if price is None:
        return jsonify({
            'success': False,
            'error': f'无法获取 {symbol} 的价格'
        }), 400
    
    # 执行买入
    success, message = trade_simulator.buy(symbol, quantity, price)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'price': price
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/trade/sell', methods=['POST'])
def sell_trade_stock():
    """卖出股票API"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    quantity = data.get('quantity', 0)
    
    if not symbol or quantity <= 0:
        return jsonify({
            'success': False,
            'error': '参数错误'
        }), 400
    
    # 获取当前价格
    price = fetcher.get_price(symbol)
    if price is None:
        return jsonify({
            'success': False,
            'error': f'无法获取 {symbol} 的价格'
        }), 400
    
    # 执行卖出
    success, message = trade_simulator.sell(symbol, quantity, price)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'price': price
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/trade/search/<query>')
def search_trade_stocks(query):
    """搜索股票API"""
    results = fetcher.search_stocks(query)
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/api/trade/portfolio')
def get_trade_portfolio():
    """获取投资组合API"""
    portfolio = trade_simulator.get_portfolio_value(fetcher.get_price)
    return jsonify(portfolio)

@app.route('/api/trade/history')
def get_trade_history():
    """获取交易历史API"""
    limit = request.args.get('limit', 20, type=int)
    transactions = trade_simulator.get_transaction_history(limit=limit)
    return jsonify(transactions)

@app.route('/trade/history')
def trade_history_page():
    """交易历史页面"""
    portfolio = trade_simulator.get_portfolio_value(fetcher.get_price)
    transactions = trade_simulator.get_transaction_history()
    holdings = portfolio.get('holdings', [])
    return render_template('trade_history.html', 
                          portfolio=portfolio, 
                          transactions=transactions, 
                          holdings=holdings)

@app.route('/trade/stock/<symbol>')
def trade_stock_detail(symbol):
    """股票详情页面"""
    portfolio = trade_simulator.get_portfolio_value(fetcher.get_price)
    stock_info = fetcher.get_stock_info(symbol)
    price_change = fetcher.get_price_change(symbol)
    
    # 获取持仓信息
    holding = None
    if 'holdings' in portfolio:
        for h in portfolio['holdings']:
            if h['symbol'] == symbol:
                holding = h
                break
    
    # 构建股票数据
    stock = {
        'symbol': symbol,
        'name': stock_info.get('name', symbol),
        'price': stock_info.get('price', 0),
        'change': price_change.get('change', 0),
        'change_percent': price_change.get('change_percent', 0),
        'sector': stock_info.get('sector', '未知')
    }
    
    return render_template('trade_stock_detail.html', 
                          stock=stock, 
                          holding=holding)

@app.route('/api/trade/reset', methods=['POST'])
def reset_trade_account():
    """重置账户API"""
    trade_simulator._init_new_account()
    return jsonify({
        'success': True,
        'message': '账户已重置'
    })

# 实验区API
@app.route('/api/experiment/<experiment_id>/price/<symbol>')
def get_experiment_price(experiment_id, symbol):
    """获取实验区股票价格API"""
    price = fetcher.get_price(symbol)
    if price:
        return jsonify({
            'success': True,
            'symbol': symbol,
            'price': price
        })
    else:
        return jsonify({
            'success': False,
            'error': f'无法获取 {symbol} 的价格'
        }), 400

@app.route('/api/experiment/<experiment_id>/buy', methods=['POST'])
def buy_experiment_stock(experiment_id):
    """实验区买入股票API"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    quantity = data.get('quantity', 0)
    
    if not symbol or quantity <= 0:
        return jsonify({
            'success': False,
            'error': '参数错误'
        }), 400
    
    # 获取当前价格
    price = fetcher.get_price(symbol)
    if price is None:
        return jsonify({
            'success': False,
            'error': f'无法获取 {symbol} 的价格'
        }), 400
    
    # 执行买入
    simulator = get_experiment_simulator(experiment_id)
    success, message = simulator.buy(symbol, quantity, price)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'price': price
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/experiment/<experiment_id>/sell', methods=['POST'])
def sell_experiment_stock(experiment_id):
    """实验区卖出股票API"""
    data = request.json
    symbol = data.get('symbol', '').upper()
    quantity = data.get('quantity', 0)
    
    if not symbol or quantity <= 0:
        return jsonify({
            'success': False,
            'error': '参数错误'
        }), 400
    
    # 获取当前价格
    price = fetcher.get_price(symbol)
    if price is None:
        return jsonify({
            'success': False,
            'error': f'无法获取 {symbol} 的价格'
        }), 400
    
    # 执行卖出
    simulator = get_experiment_simulator(experiment_id)
    success, message = simulator.sell(symbol, quantity, price)
    
    if success:
        return jsonify({
            'success': True,
            'message': message,
            'price': price
        })
    else:
        return jsonify({
            'success': False,
            'error': message
        }), 400

@app.route('/api/experiment/<experiment_id>/portfolio')
def get_experiment_portfolio(experiment_id):
    """获取实验区投资组合API"""
    simulator = get_experiment_simulator(experiment_id)
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    return jsonify(portfolio)

@app.route('/api/experiment/<experiment_id>/history')
def get_experiment_history(experiment_id):
    """获取实验区交易历史API"""
    simulator = get_experiment_simulator(experiment_id)
    limit = request.args.get('limit', 20, type=int)
    transactions = simulator.get_transaction_history(limit=limit)
    return jsonify(transactions)

@app.route('/api/experiment/<experiment_id>/reset', methods=['POST'])
def reset_experiment_account(experiment_id):
    """重置实验账户API"""
    simulator = get_experiment_simulator(experiment_id)
    simulator._init_new_account()
    return jsonify({
        'success': True,
        'message': '实验账户已重置'
    })

@app.route('/api/experiment/1/maotai-data')
def get_maotai_stock_data():
    """获取贵州茅台模拟股价数据API"""
    data = generate_maotai_stock_data()
    return jsonify({
        'success': True,
        'data': data
    })

# 生成沪深300指数2015-2019年模拟数据
def generate_hs300_stock_data():
    """生成沪深300指数2015-2019年模拟数据"""
    data = {
        'dates': [],
        'prices': [],
        'events': []
    }
    
    # 2015年6月：起始价格5000点（牛市顶点）
    start_date = datetime(2015, 6, 1)
    current_price = 5000.0
    
    # 生成2015年6月-2016年的暴跌和阴跌趋势
    for i in range(365):  # 约1年
        date = start_date + timedelta(days=i)
        data['dates'].append(date.strftime('%Y-%m-%d'))
        
        # 模拟暴跌和阴跌
        if i < 60:  # 前2个月暴跌
            current_price -= 30  # 快速下跌
        elif i < 180:  # 中间4个月阴跌
            current_price -= 5  # 缓慢下跌
        else:  # 后6个月震荡
            current_price += random.uniform(-10, 10)
        
        if current_price < 3000:
            current_price = 3000  # 最低3000点
        data['prices'].append(round(current_price, 2))
        
        # 添加关键事件
        if i == 30:  # 2015年7月
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'crash',
                'content': '股灾开始，指数暴跌'
            })
        if i == 180:  # 2016年初
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '指数进入漫长震荡期'
            })
    
    # 生成2017-2018年的震荡期
    for i in range(365, 1095):  # 约2年
        date = start_date + timedelta(days=i)
        data['dates'].append(date.strftime('%Y-%m-%d'))
        
        # 模拟震荡
        current_price += random.uniform(-20, 20)
        if current_price < 3000:
            current_price = 3000
        if current_price > 4000:
            current_price = 4000
        data['prices'].append(round(current_price, 2))
        
        if i == 730:  # 2017年6月
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '市场持续震荡，定投成本持续摊薄'
            })
        if i == 1000:  # 2018年贸易摩擦
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '贸易摩擦加剧，指数再次探底'
            })
    
    # 生成2019年初的回升期
    for i in range(1095, 1278):  # 约6个月
        date = start_date + timedelta(days=i)
        data['dates'].append(date.strftime('%Y-%m-%d'))
        
        # 模拟回升
        current_price += 5  # 稳步回升
        if current_price > 3500:
            current_price = 3500  # 最终3500点
        data['prices'].append(round(current_price, 2))
        
        if i == 1200:  # 2019年初
            data['events'].append({
                'date': date.strftime('%Y-%m-%d'),
                'type': 'news',
                'content': '指数开始回升，定投账户实现盈利'
            })
    
    return data

@app.route('/api/experiment/2/hs300-data')
def get_hs300_stock_data():
    """获取沪深300模拟指数数据API"""
    data = generate_hs300_stock_data()
    return jsonify({
        'success': True,
        'data': data
    })

# 生成实验三的行业分化模拟数据
def generate_industry_stocks_data():
    """生成行业分化模拟数据"""
    # 股票池
    stocks = [
        {
            'symbol': '600519',
            'name': '贵州茅台',
            'industry': '消费',
            'type': '高估值成长',
            'start_price': 2000.0,
            'price_change': []
        },
        {
            'symbol': '603288',
            'name': '海天味业',
            'industry': '消费',
            'type': '高估值成长',
            'start_price': 100.0,
            'price_change': []
        },
        {
            'symbol': '600276',
            'name': '恒瑞医药',
            'industry': '医药',
            'type': '高估值成长',
            'start_price': 80.0,
            'price_change': []
        },
        {
            'symbol': '300750',
            'name': '宁德时代',
            'industry': '新能源',
            'type': '高景气成长',
            'start_price': 300.0,
            'price_change': []
        },
        {
            'symbol': '600036',
            'name': '招商银行',
            'industry': '金融',
            'type': '低估值价值',
            'start_price': 40.0,
            'price_change': []
        },
        {
            'symbol': '601088',
            'name': '中国神华',
            'industry': '传统能源',
            'type': '周期价值',
            'start_price': 20.0,
            'price_change': []
        }
    ]
    
    # 生成2021年全年的数据（365天）
    start_date = datetime(2021, 1, 1)
    dates = []
    for i in range(365):
        date = start_date + timedelta(days=i)
        dates.append(date.strftime('%Y-%m-%d'))
    
    # 为每只股票生成价格变化
    for stock in stocks:
        current_price = stock['start_price']
        prices = []
        
        for i in range(365):
            # 根据行业和时间阶段生成不同的价格变化
            if i < 60:  # 2021年初，核心资产上涨
                if stock['type'] == '高估值成长':
                    current_price *= (1 + random.uniform(0.001, 0.003))
                elif stock['type'] == '高景气成长':
                    current_price *= (1 + random.uniform(0.002, 0.004))
                else:
                    current_price *= (1 + random.uniform(0.0005, 0.0015))
            elif i < 180:  # 2021年中，核心资产回调
                if stock['type'] == '高估值成长':
                    current_price *= (1 + random.uniform(-0.003, -0.001))
                elif stock['type'] == '高景气成长':
                    current_price *= (1 + random.uniform(0.002, 0.005))
                elif stock['industry'] == '传统能源':
                    current_price *= (1 + random.uniform(0.001, 0.003))
                else:
                    current_price *= (1 + random.uniform(-0.0005, 0.0005))
            else:  # 2021年末，风格分化加剧
                if stock['type'] == '高估值成长':
                    current_price *= (1 + random.uniform(-0.001, 0.001))
                elif stock['type'] == '高景气成长':
                    current_price *= (1 + random.uniform(0.003, 0.006))
                elif stock['industry'] == '传统能源':
                    current_price *= (1 + random.uniform(0.002, 0.004))
                else:
                    current_price *= (1 + random.uniform(0.0005, 0.0015))
            
            prices.append(round(current_price, 2))
        
        stock['prices'] = prices
    
    # 生成事件
    events = [
        {
            'date': '2021-02-01',
            'type': 'news',
            'content': '核心资产抱团达到顶峰'
        },
        {
            'date': '2021-03-01',
            'type': 'crash',
            'content': '核心资产开始回调'
        },
        {
            'date': '2021-06-01',
            'type': 'news',
            'content': '新能源行业景气度高涨'
        },
        {
            'date': '2021-09-01',
            'type': 'news',
            'content': '传统能源价格上涨'
        },
        {
            'date': '2021-12-31',
            'type': 'news',
            'content': '风格分化明显，新能源和传统能源表现强势'
        }
    ]
    
    return {
        'dates': dates,
        'stocks': stocks,
        'events': events
    }

@app.route('/api/experiment/3/industry-data')
def get_industry_stocks_data():
    """获取行业分化模拟数据API"""
    data = generate_industry_stocks_data()
    return jsonify({
        'success': True,
        'data': data
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8000)
