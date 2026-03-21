"""
股票交易模拟器核心逻辑
处理买入、卖出、资产计算等功能
"""

import json
import os
from datetime import datetime

class TradingSimulator:
    def __init__(self, initial_balance=100000, portfolio_file="portfolio.json"):
        """
        初始化交易模拟器
        :param initial_balance: 初始资金，默认10万
        :param portfolio_file: 持仓数据文件
        """
        self.initial_balance = initial_balance
        self.portfolio_file = portfolio_file
        self.transaction_fee_rate = 0.001  # 手续费率0.1%
        
        # 加载或初始化数据
        self.load_data()
    
    def load_data(self):
        """
        从JSON文件加载持仓和交易记录
        """
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.cash = data.get('cash', self.initial_balance)
                    self.holdings = data.get('holdings', {})
                    self.transactions = data.get('transactions', [])
                    self.yesterday_assets = data.get('yesterday_assets', self.initial_balance)
                    print(f"已加载数据，当前现金: ${self.cash:,.2f}")
            except Exception as e:
                print(f"加载数据失败: {e}，使用初始资金")
                self._init_new_account()
        else:
            print("未找到数据文件，创建新账户")
            self._init_new_account()
    
    def _init_new_account(self):
        """
        初始化新账户
        """
        self.cash = self.initial_balance
        self.holdings = {}  # {symbol: {'quantity': 数量, 'avg_cost': 平均成本}}
        self.transactions = []
        self.yesterday_assets = self.initial_balance  # 昨日总资产
        self.save_data()
    
    def save_data(self):
        """
        保存数据到JSON文件
        """
        data = {
            'cash': self.cash,
            'holdings': self.holdings,
            'transactions': self.transactions,
            'yesterday_assets': getattr(self, 'yesterday_assets', self.initial_balance),
            'last_updated': datetime.now().isoformat()
        }
        
        try:
            with open(self.portfolio_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存数据失败: {e}")
    
    def buy(self, symbol, quantity, price):
        """
        买入股票
        :param symbol: 股票代码
        :param quantity: 买入数量
        :param price: 买入价格
        :return: (success, message)
        """
        symbol = symbol.upper().strip()
        quantity = int(quantity)
        
        if quantity <= 0:
            return False, "买入数量必须大于0"
        
        # 计算总成本（含手续费）
        total_cost = quantity * price
        fee = total_cost * self.transaction_fee_rate
        total_amount = total_cost + fee
        
        # 检查资金是否充足
        if total_amount > self.cash:
            return False, f"资金不足！需要${total_amount:,.2f}，当前现金${self.cash:,.2f}"
        
        # 执行买入
        self.cash -= total_amount
        
        # 更新持仓
        if symbol in self.holdings:
            # 已持有，计算新的平均成本
            old_quantity = self.holdings[symbol]['quantity']
            old_cost = self.holdings[symbol]['avg_cost'] * old_quantity
            new_quantity = old_quantity + quantity
            new_avg_cost = (old_cost + total_cost) / new_quantity
            
            self.holdings[symbol]['quantity'] = new_quantity
            self.holdings[symbol]['avg_cost'] = new_avg_cost
        else:
            # 新持仓
            self.holdings[symbol] = {
                'quantity': quantity,
                'avg_cost': price
            }
        
        # 记录交易
        transaction = {
            'type': 'BUY',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'fee': fee,
            'total_amount': total_amount,
            'timestamp': datetime.now().isoformat()
        }
        self.transactions.append(transaction)
        
        # 保存数据
        self.save_data()
        
        return True, f"成功买入 {quantity} 股 {symbol} @ ${price:.2f}，手续费: ${fee:.2f}"
    
    def sell(self, symbol, quantity, price):
        """
        卖出股票
        :param symbol: 股票代码
        :param quantity: 卖出数量
        :param price: 卖出价格
        :return: (success, message)
        """
        symbol = symbol.upper().strip()
        quantity = int(quantity)
        
        if quantity <= 0:
            return False, "卖出数量必须大于0"
        
        # 检查是否持有该股票
        if symbol not in self.holdings:
            return False, f"未持有 {symbol} 股票"
        
        current_quantity = self.holdings[symbol]['quantity']
        if quantity > current_quantity:
            return False, f"持仓不足！持有{current_quantity}股，尝试卖出{quantity}股"
        
        # 计算收入（扣除手续费）
        total_revenue = quantity * price
        fee = total_revenue * self.transaction_fee_rate
        net_revenue = total_revenue - fee
        
        # 计算盈亏
        avg_cost = self.holdings[symbol]['avg_cost']
        cost_basis = quantity * avg_cost
        profit_loss = net_revenue - cost_basis
        profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0
        
        # 执行卖出
        self.cash += net_revenue
        
        # 更新持仓
        self.holdings[symbol]['quantity'] -= quantity
        if self.holdings[symbol]['quantity'] == 0:
            del self.holdings[symbol]
        
        # 记录交易
        transaction = {
            'type': 'SELL',
            'symbol': symbol,
            'quantity': quantity,
            'price': price,
            'fee': fee,
            'total_amount': net_revenue,
            'profit_loss': profit_loss,
            'timestamp': datetime.now().isoformat()
        }
        self.transactions.append(transaction)
        
        # 保存数据
        self.save_data()
        
        # 构建返回消息
        msg = f"成功卖出 {quantity} 股 {symbol} @ ${price:.2f}，手续费: ${fee:.2f}"
        if profit_loss >= 0:
            msg += f"\n盈利: ${profit_loss:,.2f} (+{profit_loss_pct:.2f}%) 🎉"
        else:
            msg += f"\n亏损: ${profit_loss:,.2f} ({profit_loss_pct:.2f}%) 📉"
        
        return True, msg
    
    def get_portfolio_value(self, price_fetcher):
        """
        获取投资组合总价值
        :param price_fetcher: 价格获取函数
        :return: 投资组合信息字典
        """
        total_stock_value = 0
        holdings_detail = []
        
        for symbol, data in self.holdings.items():
            quantity = data['quantity']
            avg_cost = data['avg_cost']
            
            # 获取当前价格
            current_price = price_fetcher(symbol)
            if current_price is None:
                current_price = avg_cost  # 如果获取失败，使用成本价
            
            market_value = quantity * current_price
            total_stock_value += market_value
            
            # 计算盈亏
            cost_basis = quantity * avg_cost
            profit_loss = market_value - cost_basis
            profit_loss_pct = (profit_loss / cost_basis) * 100 if cost_basis > 0 else 0
            
            holdings_detail.append({
                'symbol': symbol,
                'quantity': quantity,
                'avg_cost': avg_cost,
                'current_price': current_price,
                'market_value': market_value,
                'profit_loss': profit_loss,
                'profit_loss_pct': profit_loss_pct
            })
        
        total_assets = self.cash + total_stock_value
        total_profit_loss = total_assets - self.initial_balance
        total_profit_loss_pct = (total_profit_loss / self.initial_balance) * 100
        
        # 计算今日盈亏（相对于上次访问时的资产）
        yesterday_assets = getattr(self, 'yesterday_assets', self.initial_balance)
        daily_profit_loss = total_assets - yesterday_assets
        daily_profit_loss_pct = (daily_profit_loss / yesterday_assets) * 100 if yesterday_assets > 0 else 0
        
        # 更新昨日资产为当前总资产（用于下次计算）
        self.yesterday_assets = total_assets
        self.save_data()
        
        return {
            'cash': self.cash,
            'stock_value': total_stock_value,
            'total_assets': total_assets,
            'initial_balance': self.initial_balance,
            'total_profit_loss': total_profit_loss,
            'total_profit_loss_pct': total_profit_loss_pct,
            'yesterday_assets': yesterday_assets,
            'daily_profit_loss': daily_profit_loss,
            'daily_profit_loss_pct': daily_profit_loss_pct,
            'holdings': holdings_detail
        }
    
    def get_transaction_history(self, limit=10):
        """
        获取交易历史
        :param limit: 返回最近多少条记录
        :return: 交易记录列表
        """
        return self.transactions[-limit:]
    
    def reset_account(self):
        """
        重置账户（谨慎使用！）
        """
        confirm = input("确定要重置账户吗？所有数据将被清除！(yes/no): ")
        if confirm.lower() == 'yes':
            self._init_new_account()
            return "账户已重置"
        return "取消重置"


# 测试代码
if __name__ == "__main__":
    sim = TradingSimulator()
    
    # 测试买入
    print("测试买入功能:")
    success, msg = sim.buy("AAPL", 10, 150.0)
    print(msg)
    
    # 查看持仓
    print("\n当前持仓:")
    print(f"现金: ${sim.cash:,.2f}")
    print(f"持仓: {sim.holdings}")
