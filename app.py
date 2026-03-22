"""
Trea Finance Lab - Web版本
Flask主应用
"""

from flask import Flask, render_template, request, jsonify, session
from simulator import TradingSimulator
from data_fetcher import DataFetcher
import os

app = Flask(__name__)
app.secret_key = 'trea-finance-lab-secret-key'

# 初始化组件
fetcher = DataFetcher(cache_duration=60)

# 自由交易区模拟器
trade_simulator = TradingSimulator(initial_balance=100000, portfolio_file='portfolio.json')

# 学习实验区模拟器（数据隔离）
experiment_simulators = {}

def get_experiment_simulator(experiment_id):
    """获取指定实验的模拟器实例"""
    if experiment_id not in experiment_simulators:
        experiment_simulators[experiment_id] = TradingSimulator(
            initial_balance=100000, 
            portfolio_file=f'experiment_{experiment_id}.json'
        )
    return experiment_simulators[experiment_id]

# 实验数据
experiments = [
    {
        'id': '1',
        'title': '新手入门：基础交易策略',
        'description': '学习基本的股票交易操作，了解买卖流程和费用计算',
        'difficulty': '入门',
        'duration': '30分钟',
        'image': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=financial%20trading%20basics%20education&image_size=square'
    },
    {
        'id': '2',
        'title': '趋势交易：跟随市场走势',
        'description': '学习识别市场趋势，掌握趋势交易策略',
        'difficulty': '中级',
        'duration': '45分钟',
        'image': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=stock%20market%20trend%20analysis&image_size=square'
    },
    {
        'id': '3',
        'title': '价值投资：寻找低估股票',
        'description': '学习基本面分析，识别具有投资价值的股票',
        'difficulty': '高级',
        'duration': '60分钟',
        'image': 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=value%20investing%20analysis&image_size=square'
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5004)
