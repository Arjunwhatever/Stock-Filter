# Stock & Crypto Screener Agent

A LangGraph-powered financial assistant that screens stocks and cryptocurrencies based on various criteria. Built with local LLMs (via Ollama) and yfinance.

## What it does

This agent helps you find stocks and cryptos that match specific criteria. Ask it questions in plain English and it'll figure out what you're looking for.

**Examples:**
- "Show me top gainers in India today"
- "What are the most active US stocks?"
- "Which cryptos have the highest market cap?"
- "Show me trending cryptocurrencies"

## Features

- **US Stock Screening** - Day gainers/losers, most actives, growth stocks, and more
- **Indian Stock Screening** - Top gainers/losers, most active, growth stocks
- **Crypto Screening** - Market cap leaders, 24h gainers/losers, high volume, trending
- **Conversational Interface** - Just ask what you want, no need to memorize commands
- **Memory** - Remembers context within your session

## Tech Stack

- **LangGraph** - Builds the agent workflow
- **Ollama (Qwen 3)** - Local LLM for natural language understanding
- **yfinance** - Fetches real-time market data
- **LangChain** - Tool binding and orchestration

## Setup

1. Install Ollama and pull the model:
```bash
ollama pull qwen3:8b
```

2. Install dependencies:
```bash
pip install langgraph langchain-ollama yfinance colorama
```

3. Run:
```bash
python main.py
```

## How it works

The agent uses LangGraph to decide which screening tool to call based on your query. It has three main tools:

- `simple_screener` - Pre-built Yahoo Finance screeners (US stocks)
- `stock_and_crypto_screener` - Custom Indian stock screeners
- `crypto_screener` - Cryptocurrency screening by various metrics

Results are saved to JSON files and displayed in the terminal.

## Notes

- Stock data is real-time from Yahoo Finance
- Crypto prices update every time you query
- The agent runs entirely locally - no API keys needed
- Type "exit" to quit

## Limitations

- Limited to stocks/cryptos available on Yahoo Finance
- Indian stock screeners use Yahoo's predefined queries
- Crypto universe is the top ~25 by market cap

## Future ideas

- Add technical indicators (RSI, moving averages)
- Support for more international markets
- Price alerts and notifications
- Historical performance analysis
