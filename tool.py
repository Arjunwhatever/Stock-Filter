from langchain.tools import tool 
import yfinance as yf 
import json
from datetime import datetime, timedelta

@tool
def simple_screener(screen_type: str, offset: int = 0) -> str: 
    """Returns screened assets (stocks, funds, bonds) given popular criteria. 

    Args:
        screen_type: One of a default set of stock screener queries from yahoo finance. 
        aggressive_small_caps, day_gainers, day_losers, growth_technology_stocks,
        most_actives, most_shorted_stocks, small_cap_gainers, undervalued_growth_stocks,
        undervalued_large_caps, conservative_foreign_funds, high_yield_bond, portfolio_anchors,
        solid_large_growth_funds, solid_midcap_growth_funds, top_mutual_funds
        offset: the pagination start point

    Returns:
        The a JSON output of assets that meet the criteria
    """
    
    query = yf.PREDEFINED_SCREENER_QUERIES[screen_type]['query']
    result = yf.screen(query, offset=offset, size=5) 

    with open('output.json', 'w') as f: 
        json.dump(result, f) 
     
    fields = ["shortName", "bid", "ask", "exchange", "fiftyTwoWeekHigh", "fiftyTwoWeekLow", 
              "averageAnalystRating", "dividendYield", "symbol"] 
    output_data = []
    for stock_detail in result['quotes']: 
        details = {}
        for key, val in stock_detail.items(): 
            if key in fields: 
                details[key] = val 
        output_data.append(details) 
    
    return f"Stock Screener Results: {output_data}"


@tool
def stock_and_crypto_screener(screen_type: str, offset: int = 0) -> str:
    """
    Returns screened assets (stocks and cryptocurrencies) given popular criteria.

    Args:
        screen_type: The type of screener query. Options:
            Stocks: 'top_gainers', 'top_losers', 'most_active', 'growth_stocks'
        offset: The pagination start point.

    Returns:
        JSON output of assets that meet the criteria.
    """
    
    # Define stock queries for Indian stocks
    stock_queries = {
        'top_gainers': 'top_gainers_in_india',
        'top_losers': 'top_losers_in_india',
        'most_active': 'most_active_in_india',
        'growth_stocks': 'growth_indian_stocks',
    }

    # Ensure valid screen type is passed
    if screen_type not in stock_queries:
        raise ValueError(f"Invalid screen type. Choose from: {list(stock_queries.keys())}")
    
    query = stock_queries[screen_type]
    
    # Get stock data
    result = yf.screen(query, offset=offset, size=5)
    
    # Fields for stock data
    stock_fields = ["shortName", "bid", "ask", "exchange", "fiftyTwoWeekHigh", "fiftyTwoWeekLow", 
                    "averageAnalystRating", "dividendYield", "symbol"]
    
    # Process stock data
    stock_data = []
    for stock_detail in result['quotes']: 
        details = {}
        for key, val in stock_detail.items(): 
            if key in stock_fields: 
                details[key] = val 
        stock_data.append(details)

    # Combine data
    combined_data = {
        "stocks": stock_data
    }

    # Write the result to a file
    with open('combined_output.json', 'w') as f: 
        json.dump(combined_data, f)

    return f"Stock Screener Results: {combined_data}"


@tool
def crypto_screener(screen_type: str, limit: int = 10) -> str:
    """
    Returns screened cryptocurrencies based on various criteria using Yahoo Finance.

    Args:
        screen_type: The type of crypto screening. Options:
            'top_by_market_cap' - Top cryptocurrencies by market capitalization
            'top_gainers_24h' - Biggest gainers in last 24 hours
            'top_losers_24h' - Biggest losers in last 24 hours
            'high_volume' - Highest 24h trading volume
            'trending' - Popular/trending cryptocurrencies
        limit: Number of results to return (default: 10, max: 50)

    Returns:
        JSON output of cryptocurrencies that meet the criteria.
    """
    
    # Top cryptocurrencies by market cap (as of 2025)
    crypto_universe = [
        'BTC-USD', 'ETH-USD', 'USDT-USD', 'BNB-USD', 'SOL-USD',
        'XRP-USD', 'USDC-USD', 'ADA-USD', 'DOGE-USD', 'TRX-USD',
        'AVAX-USD', 'SHIB-USD', 'DOT-USD', 'LINK-USD', 'MATIC-USD',
        'LTC-USD', 'BCH-USD', 'UNI-USD', 'XLM-USD', 'ATOM-USD',
        'FIL-USD', 'APT-USD', 'ARB-USD', 'OP-USD', 'INJ-USD'
    ]
    
    limit = min(limit, 50)  # Cap at 50
    
    crypto_data = []
    
    # Fetch data for all cryptos
    for symbol in crypto_universe[:limit * 2]:  # Fetch more than needed for filtering
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period='1d')
            
            if hist.empty:
                continue
            
            # Calculate 24h change
            current_price = hist['Close'].iloc[-1]
            open_price = hist['Open'].iloc[0]
            change_24h = ((current_price - open_price) / open_price) * 100
            
            crypto_info = {
                'symbol': symbol.replace('-USD', ''),
                'name': info.get('longName', symbol),
                'price': round(current_price, 6),
                'change_24h': round(change_24h, 2),
                'volume_24h': int(hist['Volume'].iloc[-1]) if not hist['Volume'].empty else 0,
                'market_cap': info.get('marketCap', 0),
                'exchange': info.get('exchange', 'CCC')
            }
            crypto_data.append(crypto_info)
        except Exception as e:
            print(f"Error fetching {symbol}: {e}")
            continue
    
    # Apply screening logic
    if screen_type == 'top_by_market_cap':
        crypto_data.sort(key=lambda x: x['market_cap'], reverse=True)
        result_title = "Top Cryptocurrencies by Market Cap"
        
    elif screen_type == 'top_gainers_24h':
        crypto_data.sort(key=lambda x: x['change_24h'], reverse=True)
        result_title = "Top 24h Gainers"
        
    elif screen_type == 'top_losers_24h':
        crypto_data.sort(key=lambda x: x['change_24h'])
        result_title = "Top 24h Losers"
        
    elif screen_type == 'high_volume':
        crypto_data.sort(key=lambda x: x['volume_24h'], reverse=True)
        result_title = "Highest 24h Volume"
        
    elif screen_type == 'trending':
        # Simple trending logic: combination of volume and price change
        for crypto in crypto_data:
            crypto['trend_score'] = (abs(crypto['change_24h']) * 0.5 + 
                                    (crypto['volume_24h'] / 1e9) * 0.5)
        crypto_data.sort(key=lambda x: x.get('trend_score', 0), reverse=True)
        result_title = "Trending Cryptocurrencies"
    else:
        raise ValueError(f"Invalid screen_type. Choose from: top_by_market_cap, top_gainers_24h, top_losers_24h, high_volume, trending")
    
    # Get top results
    screened_cryptos = crypto_data[:limit]
    
    result = {
        "screen_type": result_title,
        "count": len(screened_cryptos),
        "cryptocurrencies": screened_cryptos
    }
    
    # Write to file
    with open('crypto_screener_output.json', 'w') as f: 
        json.dump(result, f, indent=2)
    
    return f"Crypto Screener Results: {result}"

    