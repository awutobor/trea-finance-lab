"""
股票数据获取模块
使用yfinance获取实时股价数据，带缓存机制
支持模拟数据模式，用于测试和API限流时使用
"""

import yfinance as yf
import time
import random
from datetime import datetime, timedelta

class DataFetcher:
    def __init__(self, cache_duration=300, use_mock_data=True):
        """
        初始化数据获取器
        :param cache_duration: 缓存时间（秒），默认300秒（5分钟）
        :param use_mock_data: 是否使用模拟数据模式，默认True
        """
        self.cache = {}
        self.cache_duration = cache_duration
        self.last_fetch_time = {}
        self.use_mock_data = use_mock_data
        
        # 模拟数据：常见股票的基准价格
        self.mock_prices = {
            'AAPL': 178.50,
            'GOOGL': 141.80,
            'GOOG': 142.30,
            'MSFT': 378.90,
            'TSLA': 248.50,
            'AMZN': 178.25,
            'META': 505.75,
            'NVDA': 875.30,
            'JPM': 198.45,
            'V': 279.80,
            'WMT': 165.30,
            'DIS': 112.45,
            'NFLX': 628.90,
            'ADBE': 578.20,
            'CRM': 305.60,
            'INTC': 31.25,
            'AMD': 158.90,
            'PYPL': 62.45,
            'BA': 178.90,
            'IBM': 195.30,
            '600519': 200.00  # 贵州茅台：基准价格
        }
        
        # 股票基本信息数据库
        self.stock_info = {
            'AAPL': {'name': '苹果公司', 'sector': '科技', 'exchange': 'NASDAQ'},
            'GOOGL': {'name': 'Alphabet公司', 'sector': '科技', 'exchange': 'NASDAQ'},
            'GOOG': {'name': 'Alphabet公司', 'sector': '科技', 'exchange': 'NASDAQ'},
            'MSFT': {'name': '微软公司', 'sector': '科技', 'exchange': 'NASDAQ'},
            'TSLA': {'name': '特斯拉公司', 'sector': '汽车', 'exchange': 'NASDAQ'},
            'AMZN': {'name': '亚马逊公司', 'sector': '零售', 'exchange': 'NASDAQ'},
            'META': {'name': 'Meta公司', 'sector': '科技', 'exchange': 'NASDAQ'},
            'NVDA': {'name': '英伟达公司', 'sector': '科技', 'exchange': 'NASDAQ'},
            'JPM': {'name': '摩根大通', 'sector': '金融', 'exchange': 'NYSE'},
            'V': {'name': 'Visa公司', 'sector': '金融', 'exchange': 'NYSE'},
            'WMT': {'name': '沃尔玛公司', 'sector': '零售', 'exchange': 'NYSE'},
            'DIS': {'name': '迪士尼公司', 'sector': '娱乐', 'exchange': 'NYSE'},
            'NFLX': {'name': '奈飞公司', 'sector': '娱乐', 'exchange': 'NASDAQ'},
            'ADBE': {'name': 'Adobe公司', 'sector': '软件', 'exchange': 'NASDAQ'},
            'CRM': {'name': 'Salesforce公司', 'sector': '软件', 'exchange': 'NYSE'},
            'INTC': {'name': '英特尔公司', 'sector': '半导体', 'exchange': 'NASDAQ'},
            'AMD': {'name': 'AMD公司', 'sector': '半导体', 'exchange': 'NASDAQ'},
            'PYPL': {'name': 'PayPal公司', 'sector': '金融科技', 'exchange': 'NASDAQ'},
            'BA': {'name': '波音公司', 'sector': '航空', 'exchange': 'NYSE'},
            'IBM': {'name': 'IBM公司', 'sector': '科技', 'exchange': 'NYSE'},
            '600519': {'name': '贵州茅台', 'sector': '食品饮料', 'exchange': 'SSE'}
        }
    
    def get_price(self, symbol):
        """
        获取股票当前价格
        :param symbol: 股票代码，如AAPL
        :return: 当前价格或None
        """
        symbol = symbol.upper().strip()
        
        # 检查缓存
        if self._is_cache_valid(symbol):
            print(f"[缓存] {symbol}: ${self.cache[symbol]:.2f}")
            return self.cache[symbol]
        
        # 贵州茅台特殊处理：模拟2012-2014年股价走势
        if self.use_mock_data and symbol == '600519':
            price = self._get_maotai_price()
            self.cache[symbol] = price
            self.last_fetch_time[symbol] = time.time()
            print(f"[模拟数据-茅台] 600519: ¥{price:.2f}")
            return price
        
        # 如果启用了模拟数据模式，优先使用模拟数据
        if self.use_mock_data and symbol in self.mock_prices:
            price = self._get_mock_price(symbol)
            self.cache[symbol] = price
            self.last_fetch_time[symbol] = time.time()
            print(f"[模拟数据] {symbol}: ${price:.2f}")
            return price
        
        # 尝试从真实API获取
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if data.empty:
                print(f"错误：无法获取 {symbol} 的数据")
                # 如果真实数据获取失败，尝试使用模拟数据
                if self.use_mock_data:
                    return self._try_mock_fallback(symbol)
                return None
            
            current_price = data['Close'].iloc[-1]
            self.cache[symbol] = current_price
            self.last_fetch_time[symbol] = time.time()
            print(f"[真实数据] {symbol}: ${current_price:.2f}")
            return current_price
            
        except Exception as e:
            print(f"获取 {symbol} 数据时出错: {str(e)}")
            # 如果API限流，尝试使用模拟数据
            if "Rate limited" in str(e) or "Too Many Requests" in str(e):
                print("API限流，切换到模拟数据模式")
                return self._try_mock_fallback(symbol)
            return None
    
    def _get_mock_price(self, symbol):
        """
        获取模拟价格（带随机波动）
        """
        base_price = self.mock_prices.get(symbol, 100.0)
        # 添加 -2% 到 +2% 的随机波动
        fluctuation = random.uniform(-0.02, 0.02)
        price = base_price * (1 + fluctuation)
        return round(price, 2)
    
    def _try_mock_fallback(self, symbol):
        """
        尝试使用模拟数据作为后备
        """
        if symbol in self.mock_prices:
            price = self._get_mock_price(symbol)
            self.cache[symbol] = price
            self.last_fetch_time[symbol] = time.time()
            print(f"[模拟数据后备] {symbol}: ${price:.2f}")
            return price
        else:
            # 如果没有预设价格，生成一个随机价格
            price = round(random.uniform(50, 500), 2)
            self.mock_prices[symbol] = price
            self.cache[symbol] = price
            self.last_fetch_time[symbol] = time.time()
            print(f"[随机模拟] {symbol}: ${price:.2f}")
            return price
    
    def _get_maotai_price(self):
        """
        获取贵州茅台的模拟价格（基于2012-2014年历史数据）
        """
        # 模拟2012-2014年茅台股价走势
        # 2012年初：248.50元（实验初始价格）
        base_price = 248.50  # 实验初始价格
        # 添加随机波动
        fluctuation = random.uniform(-1, 1)
        price = base_price + fluctuation
        return round(price, 2)
    
    def get_stock_info(self, symbol):
        """
        获取股票详细信息
        :param symbol: 股票代码
        :return: 股票信息字典
        """
        symbol = symbol.upper().strip()
        
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            return {
                'name': info.get('longName', 'N/A'),
                'symbol': symbol,
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'pe_ratio': info.get('trailingPE', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A')
            }
        except Exception as e:
            print(f"获取 {symbol} 信息时出错: {str(e)}")
            # 返回模拟信息
            return {
                'name': f'{symbol} Corporation',
                'symbol': symbol,
                'sector': 'Technology',
                'industry': 'Technology',
                'market_cap': 'N/A',
                'pe_ratio': 'N/A',
                '52_week_high': 'N/A',
                '52_week_low': 'N/A'
            }
    
    def search_stocks(self, query):
        """
        搜索股票
        :param query: 搜索关键词
        :return: 匹配的股票列表
        """
        query = query.upper().strip()
        results = []
        
        # 从股票信息数据库中搜索
        for symbol, info in self.stock_info.items():
            if (query in symbol) or (query in info['name'].upper()):
                results.append({
                    'symbol': symbol,
                    'name': info['name'],
                    'sector': info['sector'],
                    'exchange': info['exchange'],
                    'price': self.get_price(symbol)
                })
        
        # 限制返回结果数量
        return results[:10]
    
    def get_price_change(self, symbol):
        """
        获取股票今日涨跌幅
        :param symbol: 股票代码
        :return: 包含当前价格、昨日收盘价、涨跌幅的字典
        """
        symbol = symbol.upper().strip()
        
        # 获取当前价格
        current_price = self.get_price(symbol)
        if current_price is None:
            return None
        
        # 获取昨日收盘价（模拟数据模式下使用基准价格的95%-105%作为昨日收盘价）
        if self.use_mock_data and symbol in self.mock_prices:
            base_price = self.mock_prices[symbol]
            # 模拟昨日收盘价（在当前价格基础上随机波动-3%到+3%）
            yesterday_close = base_price * random.uniform(0.97, 1.03)
        else:
            try:
                ticker = yf.Ticker(symbol)
                # 获取历史数据（2天）
                hist = ticker.history(period="2d")
                if len(hist) >= 2:
                    yesterday_close = hist['Close'].iloc[-2]
                else:
                    yesterday_close = current_price * 0.98  # 默认昨日比今日低2%
            except:
                yesterday_close = current_price * 0.98
        
        # 计算涨跌幅
        change = current_price - yesterday_close
        change_percent = (change / yesterday_close) * 100 if yesterday_close > 0 else 0
        
        return {
            'current_price': current_price,
            'yesterday_close': yesterday_close,
            'change': change,
            'change_percent': change_percent
        }
    
    def _is_cache_valid(self, symbol):
        """
        检查缓存是否有效
        """
        if symbol not in self.cache:
            return False
        
        last_time = self.last_fetch_time.get(symbol, 0)
        current_time = time.time()
        
        return (current_time - last_time) < self.cache_duration
    
    def clear_cache(self):
        """
        清除所有缓存
        """
        self.cache.clear()
        self.last_fetch_time.clear()
        print("缓存已清除")
    
    def set_mock_data_mode(self, enabled):
        """
        设置是否使用模拟数据模式
        :param enabled: True启用，False禁用
        """
        self.use_mock_data = enabled
        print(f"模拟数据模式: {'启用' if enabled else '禁用'}")


# 测试代码
if __name__ == "__main__":
    print("=== 测试模式1：使用模拟数据 ===")
    fetcher = DataFetcher(use_mock_data=True)
    
    # 测试获取价格
    print("\n测试获取股票价格:")
    for symbol in ['AAPL', 'GOOGL', 'TSLA']:
        price = fetcher.get_price(symbol)
        if price:
            print(f"{symbol} 当前价格: ${price:.2f}")
    
    # 测试缓存
    print("\n测试缓存（应该使用缓存）:")
    price = fetcher.get_price("AAPL")
    
    # 测试未知股票
    print("\n测试未知股票:")
    price = fetcher.get_price("UNKNOWN")
    if price:
        print(f"UNKNOWN 当前价格: ${price:.2f}")
    
    print("\n=== 测试模式2：禁用模拟数据 ===")
    fetcher2 = DataFetcher(use_mock_data=False)
    print("\n尝试获取真实数据（可能因限流失败）:")
    price = fetcher2.get_price("AAPL")
    if price:
        print(f"AAPL 当前价格: ${price:.2f}")
    else:
        print("获取失败（预期行为，因为API限流）")
