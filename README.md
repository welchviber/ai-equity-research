# AI Equity Research Agent

An autonomous financial research agent built with Python, OpenClaw, and the Claude API. It ingests SEC filings and live market data for any publicly traded company and generates structured investment memos with bull/bear case breakdowns - accessible from the command line or autonomously via Telegram.

## What It Does

- Resolves any stock ticker to its official SEC CIK and fetches the latest 10-K filing from EDGAR
- Pulls live analyst consensus and market data from Yahoo Finance (price targets, recommendations, revenue growth, margins, forward P/E, PEG)
- Sends the combined data to the Claude API with an engineered prompt pipeline
- Generates a structured investment memo including:
  - Executive summary
  - Key metrics (EV/EBITDA, FCF yield, revenue growth, gross margins, forward P/E, PEG)
  - Guidance delta (current vs prior-year expectations)
  - Bull and bear cases tied to specific data
  - AI thesis benchmarked against Wall Street consensus on directional calls
  - Valuation and investment recommendation
- Saves each memo as a .txt file
- Runs autonomously as an OpenClaw agent - message a ticker on Telegram and receive a full memo back

## Tech Stack

- Python — core research pipeline
- Anthropic Claude API — AI analysis and memo generation
- OpenClaw — agentic framework for autonomous operation
- SEC EDGAR API — official filing data and ticker-to-CIK resolution
- Yahoo Finance API — live analyst consensus and market data
- Telegram — messaging interface

## Architecture

```
User sends ticker (CLI or Telegram)
        |
        v
OpenClaw agent receives it (reads AGENTS.md / SOUL.md instructions)
        |
        v
Runs reearch.py with the ticker
        |
        v
[1] Resolve ticker -> CIK -> fetch latest 10-K from SEC EDGAR
[2] Fetch live analyst consensus from Yahoo Finance
[3] Engineered prompt -> Claude API
        |
        v
Structured investment memo (bull/bear, guidance delta, consensus benchmark)
        |
        v
Saved to .txt + returned to user on Telegram
```

## Built With Agentic Development

This project was developed using OpenClaw's agentic framework as an active development partner, not just a runtime. During build-out, the OpenClaw agent autonomously:

- Diagnosed bugs in the data pipeline (an incorrect SEC full-text search endpoint that returned the wrong company, and a Yahoo Finance endpoint that began requiring a session cookie + crumb token)
- Rewrote the SEC lookup to resolve tickers to CIKs via the official `company_tickers.json` map before fetching the correct 10-K
- Added the Yahoo crumb handshake so live consensus data flows reliably
- Hardened the prompt pipeline to use live data as authoritative and to make the guidance-delta and consensus-benchmark sections mandatory in every memo
- Fixed a console encoding crash with a UTF-8 fallback

## Agentic Debugging in Action

The OpenClaw agent autonomously diagnosing and fixing the SEC and Yahoo data pipeline bugs over Telegram:


<img width="842" height="591" alt="Screenshot 2026-06-14 004547" src="https://github.com/user-attachments/assets/1bd29f27-f686-4096-8080-724580a285ed" />
<img width="675" height="1151" alt="Screenshot 2026-06-14 004552" src="https://github.com/user-attachments/assets/f213e891-4622-47b3-ae46-c59265aaeb0a" />
<img width="998" height="1095" alt="Screenshot 2026-06-14 004557" src="https://github.com/user-attachments/assets/8bea79d8-e4ef-411b-924f-a28bc1c503b4" />
<img width="810" height="498" alt="Screenshot 2026-06-14 004927" src="https://github.com/user-attachments/assets/b4e426ee-4ac1-495a-845b-e34bf6bf3c8b" />



This demonstrates the agent operating across a real multi-step workflow: reading the codebase, testing data feeds in isolation, identifying root causes, patching the script, and verifying the fix end-to-end.

## Setup

### 1. Install dependencies
```
pip install anthropic requests python-dotenv
```

### 2. Add your API key
Create a `.env` file in the project folder:
```
ANTHROPIC_API_KEY=your-key-here
```

### 3. Run the research pipeline
```
python reearch.py AAPL
```
Or run without an argument and enter the ticker when prompted.

The script will fetch the SEC filing, pull live analyst consensus, generate the memo, print it, and save it as `AAPL_research_memo.txt`.

## OpenClaw Setup (Autonomous Agent via Telegram)

To run it as an autonomous agent you can message from your phone:

1. Install Node.js from nodejs.org
2. Install OpenClaw: `npm install -g openclaw`
3. Run onboarding: `openclaw onboard`
4. Connect your Anthropic API key and add a Telegram bot token from @BotFather
5. Add the equity research instructions to your OpenClaw workspace `AGENTS.md` (see SOUL.md in this repo for the agent definition) so the agent runs `reearch.py` when it receives a ticker
6. Start the gateway: `openclaw gateway run`
7. Message your bot any ticker on Telegram (e.g. `NVDA`) to receive a full memo

## Sample Output

See `AAPL_research_memo.txt` for an example generated memo with live data, guidance deltas, and analyst consensus benchmarking.

## Note

This tool is for research and educational purposes only. It is not financial advice.

## Author

Welch Lim Chee Cheng
