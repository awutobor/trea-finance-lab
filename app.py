"""
Trea Finance Lab - Web版本
Flask主应用
"""

from flask import Flask, render_template, request, jsonify
from simulator import TradingSimulator
from data_fetcher import DataFetcher
import os

app = Flask(__name__)
app.secret_key = 'trea-finance-lab-secret-key'

# 初始化组件
fetcher = DataFetcher(cache_duration=60)
simulator = TradingSimulator(initial_balance=100000, portfolio_file='portfolio.json')

@app.route('/')
def index():
    """首页"""
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    return render_template('index.html', portfolio=portfolio)

@app.route('/api/price/<symbol>')
def get_price(symbol):
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

@app.route('/api/buy', methods=['POST'])
def buy_stock():
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

@app.route('/api/sell', methods=['POST'])
def sell_stock():
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

@app.route('/api/search/<query>')
def search_stocks(query):
    """搜索股票API"""
    results = fetcher.search_stocks(query)
    return jsonify({
        'success': True,
        'results': results
    })

@app.route('/api/portfolio')
def get_portfolio():
    """获取投资组合API"""
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    return jsonify(portfolio)

@app.route('/api/history')
def get_history():
    """获取交易历史API"""
    limit = request.args.get('limit', 20, type=int)
    transactions = simulator.get_transaction_history(limit=limit)
    return jsonify(transactions)

@app.route('/history')
def history_page():
    """交易历史页面"""
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    return render_template('history.html', portfolio=portfolio)

@app.route('/stock/<symbol>')
def stock_detail(symbol):
    """股票详情页面"""
    portfolio = simulator.get_portfolio_value(fetcher.get_price)
    stock_info = fetcher.get_stock_info(symbol)
    price_change = fetcher.get_price_change(symbol)
    return render_template('stock_detail.html', 
                          portfolio=portfolio, 
                          stock_info=stock_info, 
                          price_change=price_change)

@app.route('/api/reset', methods=['POST'])
def reset_account():
    """重置账户API"""
    simulator._init_new_account()
    return jsonify({
        'success': True,
        'message': '账户已重置'
    })

if __name__ == '__main__':
    app.run(debug=True, port=5002)
