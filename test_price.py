from data_fetcher import DataFetcher

f = DataFetcher()
print('测试获取AAPL价格:')
price = f.get_price('AAPL')
if price:
    print(f'结果: ${price:.2f}')
else:
    print('失败')
