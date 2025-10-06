def _process_coins(self, raw_coins):
    """پردازش امن داده‌های ارزها - تست"""
    print(f"🎯 TEST: دریافت {len(raw_coins)} ارز از سرور")
    
    # فقط 5 ارز اول رو برگردون برای تست
    test_coins = []
    for i in range(min(5, len(raw_coins))):
        coin = raw_coins[i]
        test_coins.append({
            'name': str(coin.get('name', f'Test_{i}')),
            'symbol': str(coin.get('symbol', f'TST_{i}')),
            'price': float(coin.get('price', 100)),
            'priceChange24h': 1.0,
            'priceChange1h': 0.1,
            'volume': 1000000,
            'marketCap': 1000000000,
            'index': i
        })
    
    print(f"🎯 TEST: برمی‌گردونم {len(test_coins)} ارز")
    return test_coins
