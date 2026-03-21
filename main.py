"""
Trea Finance Lab - 虚拟股票交易模拟器
命令行交互主程序
"""

from data_fetcher import DataFetcher
from simulator import TradingSimulator

def print_welcome():
    """打印欢迎信息"""
    print("=" * 60)
    print("  🚀 Trea Finance Lab - 虚拟股票交易模拟器")
    print("=" * 60)
    print("  初始资金: $100,000")
    print("  交易手续费: 0.1%")
    print("=" * 60)
    print()

def print_help():
    """打印帮助信息"""
    print("📖 可用命令:")
    print("-" * 40)
    print("  price <股票代码>     - 查询股票价格 (如: price AAPL)")
    print("  buy <代码> <数量>    - 买入股票 (如: buy AAPL 10)")
    print("  sell <代码> <数量>   - 卖出股票 (如: sell AAPL 5)")
    print("  portfolio            - 查看资产组合")
    print("  history              - 查看交易历史")
    print("  reset                - 重置账户(谨慎使用!)")
    print("  help                 - 显示帮助")
    print("  quit/exit            - 退出程序")
    print("-" * 40)
    print()

def format_money(amount):
    """格式化金额显示"""
    if amount >= 0:
        return f"${amount:,.2f}"
    else:
        return f"-${abs(amount):,.2f}"

def main():
    """主程序"""
    print_welcome()
    
    # 初始化组件
    fetcher = DataFetcher(cache_duration=60)
    simulator = TradingSimulator(initial_balance=100000)
    
    print_help()
    
    while True:
        try:
            # 获取用户输入
            user_input = input("💰 Trea Finance > ").strip()
            
            if not user_input:
                continue
            
            # 解析命令
            parts = user_input.split()
            command = parts[0].lower()
            
            # 处理命令
            if command in ['quit', 'exit', 'q']:
                print("👋 感谢使用 Trea Finance Lab，再见！")
                break
            
            elif command == 'help':
                print_help()
            
            elif command == 'price':
                if len(parts) < 2:
                    print("❌ 用法: price <股票代码>")
                    print("   示例: price AAPL")
                    continue
                
                symbol = parts[1]
                print(f"📊 正在查询 {symbol} 的价格...")
                price = fetcher.get_price(symbol)
                
                if price:
                    print(f"✅ {symbol} 当前价格: {format_money(price)}")
                else:
                    print(f"❌ 无法获取 {symbol} 的价格，请检查股票代码")
            
            elif command == 'buy':
                if len(parts) < 3:
                    print("❌ 用法: buy <股票代码> <数量>")
                    print("   示例: buy AAPL 10")
                    continue
                
                symbol = parts[1]
                try:
                    quantity = int(parts[2])
                except ValueError:
                    print("❌ 数量必须是整数")
                    continue
                
                # 获取当前价格
                print(f"📊 正在获取 {symbol} 的当前价格...")
                price = fetcher.get_price(symbol)
                
                if price is None:
                    print(f"❌ 无法获取 {symbol} 的价格，买入失败")
                    continue
                
                # 确认买入
                total_cost = quantity * price * 1.001  # 含手续费
                print(f"\n💡 买入预览:")
                print(f"   股票: {symbol}")
                print(f"   数量: {quantity} 股")
                print(f"   价格: {format_money(price)}")
                print(f"   预估总成本(含手续费): {format_money(total_cost)}")
                
                confirm = input("确认买入? (y/n): ").lower()
                if confirm != 'y':
                    print("❌ 已取消买入")
                    continue
                
                # 执行买入
                success, msg = simulator.buy(symbol, quantity, price)
                if success:
                    print(f"✅ {msg}")
                else:
                    print(f"❌ {msg}")
            
            elif command == 'sell':
                if len(parts) < 3:
                    print("❌ 用法: sell <股票代码> <数量>")
                    print("   示例: sell AAPL 5")
                    continue
                
                symbol = parts[1]
                try:
                    quantity = int(parts[2])
                except ValueError:
                    print("❌ 数量必须是整数")
                    continue
                
                # 获取当前价格
                print(f"📊 正在获取 {symbol} 的当前价格...")
                price = fetcher.get_price(symbol)
                
                if price is None:
                    print(f"❌ 无法获取 {symbol} 的价格，卖出失败")
                    continue
                
                # 确认卖出
                print(f"\n💡 卖出预览:")
                print(f"   股票: {symbol}")
                print(f"   数量: {quantity} 股")
                print(f"   价格: {format_money(price)}")
                
                confirm = input("确认卖出? (y/n): ").lower()
                if confirm != 'y':
                    print("❌ 已取消卖出")
                    continue
                
                # 执行卖出
                success, msg = simulator.sell(symbol, quantity, price)
                print(f"{'✅' if success else '❌'} {msg}")
            
            elif command == 'portfolio':
                print("\n" + "=" * 60)
                print("📊 资产组合概览")
                print("=" * 60)
                
                portfolio = simulator.get_portfolio_value(fetcher.get_price)
                
                # 显示现金
                print(f"💵 现金: {format_money(portfolio['cash'])}")
                print(f"📈 股票市值: {format_money(portfolio['stock_value'])}")
                print(f"💰 总资产: {format_money(portfolio['total_assets'])}")
                print(f"📊 初始资金: {format_money(portfolio['initial_balance'])}")
                
                # 显示盈亏
                pnl = portfolio['total_profit_loss']
                pnl_pct = portfolio['total_profit_loss_pct']
                if pnl >= 0:
                    print(f"🎉 总盈亏: +{format_money(pnl)} (+{pnl_pct:.2f}%)")
                else:
                    print(f"📉 总盈亏: {format_money(pnl)} ({pnl_pct:.2f}%)")
                
                # 显示持仓详情
                if portfolio['holdings']:
                    print("\n📋 持仓详情:")
                    print("-" * 60)
                    print(f"{'股票':<10} {'数量':<8} {'成本价':<12} {'现价':<12} {'市值':<15} {'盈亏'}")
                    print("-" * 60)
                    
                    for holding in portfolio['holdings']:
                        symbol = holding['symbol']
                        qty = holding['quantity']
                        avg_cost = holding['avg_cost']
                        current = holding['current_price']
                        value = holding['market_value']
                        pnl = holding['profit_loss']
                        pnl_pct = holding['profit_loss_pct']
                        
                        pnl_str = f"+{pnl:,.2f}" if pnl >= 0 else f"{pnl:,.2f}"
                        print(f"{symbol:<10} {qty:<8} ${avg_cost:<11.2f} ${current:<11.2f} ${value:<14,.2f} {pnl_str}")
                else:
                    print("\n📭 当前没有持仓")
                
                print("=" * 60)
            
            elif command == 'history':
                print("\n📜 最近交易记录:")
                print("=" * 60)
                
                transactions = simulator.get_transaction_history(limit=10)
                
                if not transactions:
                    print("暂无交易记录")
                else:
                    for i, trans in enumerate(reversed(transactions), 1):
                        t_type = trans['type']
                        symbol = trans['symbol']
                        qty = trans['quantity']
                        price = trans['price']
                        fee = trans['fee']
                        total = trans['total_amount']
                        time = trans['timestamp'][:19]  # 去掉毫秒
                        
                        action = "买入" if t_type == 'BUY' else "卖出"
                        print(f"{i}. [{time}] {action} {qty}股 {symbol} @ ${price:.2f}")
                        print(f"   手续费: ${fee:.2f}, 总金额: ${total:,.2f}")
                        
                        if 'profit_loss' in trans:
                            pnl = trans['profit_loss']
                            pnl_str = f"+${pnl:,.2f}" if pnl >= 0 else f"-${abs(pnl):,.2f}"
                            print(f"   盈亏: {pnl_str}")
                        print()
                
                print("=" * 60)
            
            elif command == 'reset':
                result = simulator.reset_account()
                print(f"🔄 {result}")
            
            else:
                print(f"❌ 未知命令: {command}")
                print("输入 'help' 查看可用命令")
            
            print()  # 空行分隔
            
        except KeyboardInterrupt:
            print("\n\n👋 感谢使用 Trea Finance Lab，再见！")
            break
        except Exception as e:
            print(f"❌ 错误: {str(e)}")
            print()

if __name__ == "__main__":
    main()
