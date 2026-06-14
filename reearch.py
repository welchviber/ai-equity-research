from dotenv import load_dotenv
load_dotenv()
import anthropic
import requests
import os
import sys

client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
SEC_HEADERS = {"User-Agent": "welchlim1@gmail.com"}

def get_cik(ticker):
    try:
        data = requests.get("https://www.sec.gov/files/company_tickers.json", headers=SEC_HEADERS).json()
        for entry in data.values():
            if entry.get("ticker", "").upper() == ticker.upper():
                return str(entry["cik_str"]).zfill(10), entry.get("title", ticker)
    except Exception:
        pass
    return None, None

def get_sec_filing(ticker):
    cik, name = get_cik(ticker)
    if not cik:
        return None
    try:
        url = f"https://data.sec.gov/submissions/CIK{cik}.json"
        data = requests.get(url, headers=SEC_HEADERS).json()
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        for i, form in enumerate(forms):
            if form == "10-K":
                return (
                    f"Company: {name} (CIK {cik})\n"
                    f"Filing Type: {form}\n"
                    f"Filed: {recent.get('filingDate', [None]*(i+1))[i]}\n"
                    f"Period: {recent.get('reportDate', [None]*(i+1))[i]}\n"
                    f"SIC/Industry: {data.get('sicDescription', 'N/A')}"
                )
        return f"Company: {name} (CIK {cik})\nNo recent 10-K found in submissions index."
    except Exception:
        return None

def get_analyst_consensus(ticker):
    try:
        ua = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"}
        session = requests.Session()
        session.get("https://fc.yahoo.com", headers=ua)
        crumb = session.get("https://query1.finance.yahoo.com/v1/test/getcrumb", headers=ua).text
        url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{ticker}"
        params = {"modules": "financialData,defaultKeyStatistics", "crumb": crumb}
        response = session.get(url, headers=ua, params=params).json()
        data = response['quoteSummary']['result'][0]
        financial = data['financialData']
        stats = data['defaultKeyStatistics']
        consensus = {
            "analyst_target": financial.get('targetMeanPrice', {}).get('raw', 'N/A'),
            "analyst_low": financial.get('targetLowPrice', {}).get('raw', 'N/A'),
            "analyst_high": financial.get('targetHighPrice', {}).get('raw', 'N/A'),
            "recommendation": financial.get('recommendationKey', 'N/A'),
            "current_price": financial.get('currentPrice', {}).get('raw', 'N/A'),
            "revenue_growth": financial.get('revenueGrowth', {}).get('raw', 'N/A'),
            "gross_margins": financial.get('grossMargins', {}).get('raw', 'N/A'),
            "forward_pe": stats.get('forwardPE', {}).get('raw', 'N/A'),
            "peg_ratio": stats.get('pegRatio', {}).get('raw', 'N/A'),
        }
        return consensus
    except:
        return None

def save_memo(ticker, content):
    filename = f"{ticker}_research_memo.txt"
    with open(filename, 'w', encoding='utf-8') as f:
        f.write(f"{ticker} - AI Equity Research Memo\n")
        f.write("="*50 + "\n\n")
        f.write(content)
    print(f"\nSaved to {filename}")

if len(sys.argv) > 1:
    ticker = sys.argv[1].upper()
else:
    ticker = input("Enter a stock ticker: ").upper()

print(f"\nFetching SEC filing for {ticker}...")
filing_info = get_sec_filing(ticker)

print(f"Fetching analyst consensus for {ticker}...")
consensus = get_analyst_consensus(ticker)

consensus_text = ""
if consensus:
    rev = consensus['revenue_growth']
    gm = consensus['gross_margins']
    rev_str = str(round(float(rev)*100, 1))+'%' if rev != 'N/A' else 'N/A'
    gm_str = str(round(float(gm)*100, 1))+'%' if gm != 'N/A' else 'N/A'
    consensus_text = (
        "ANALYST CONSENSUS DATA:\n"
        f"- Current Price: ${consensus['current_price']}\n"
        f"- Analyst Mean Price Target: ${consensus['analyst_target']}\n"
        f"- Analyst Price Range: ${consensus['analyst_low']} - ${consensus['analyst_high']}\n"
        f"- Wall Street Recommendation: {str(consensus['recommendation']).upper()}\n"
        f"- Revenue Growth (YoY): {rev_str}\n"
        f"- Gross Margins: {gm_str}\n"
        f"- Forward P/E: {consensus['forward_pe']}\n"
        f"- PEG Ratio: {consensus['peg_ratio']}\n"
    )

filing_text = filing_info if filing_info else "No SEC filing found - using general knowledge."

prompt = (
    f"You are a senior equity research analyst writing an investment memo on {ticker}.\n\n"
    "IMPORTANT INSTRUCTIONS:\n"
    "- The LIVE DATA below was fetched today from SEC EDGAR and Yahoo Finance. TREAT IT AS CURRENT AND AUTHORITATIVE.\n"
    "- USE the provided numbers directly. Do NOT say data is missing, unavailable, or that you cannot complete the analysis when a value is present below.\n"
    "- For any metric not explicitly provided (e.g. EV/EBITDA, FCF Yield), give your best informed estimate based on the company's known financial profile and the live figures provided, and clearly label it as an estimate.\n"
    "- Date the memo TODAY using the as-of date implied by this live data, not a date from your training cutoff.\n"
    "- Be specific, decisive, and grounded in the numbers below.\n\n"
    f"=== LIVE SEC FILING DATA ===\n{filing_text}\n\n"
    f"=== LIVE ANALYST/MARKET DATA ===\n{consensus_text}\n\n"
    "Generate a structured investment memo with ALL of the following sections. Every section is MANDATORY:\n\n"
    "1. EXECUTIVE SUMMARY (lead with the call and the key numbers)\n\n"
    "2. KEY METRICS (use a table; populate from live data, estimate the rest and label estimates)\n"
    "- EV/EBITDA\n"
    "- FCF Yield\n"
    "- Revenue Growth (YoY)\n"
    "- Gross Margins\n"
    "- Forward P/E and PEG Ratio\n\n"
    "3. GUIDANCE DELTA (MANDATORY)\n"
    "- Explicitly compare the company's CURRENT guidance/expectations against PRIOR-YEAR expectations.\n"
    "- State the direction of the delta (raised / lowered / in-line) for revenue, margins, and EPS where inferable.\n"
    "- If exact guidance figures are not in the live data, infer the directional delta from revenue growth, margins, and consensus, and label it as inferred. Never omit this section.\n\n"
    "4. BULL CASE (3-5 points, each tied to specific data)\n\n"
    "5. BEAR CASE (3-5 points, each tied to specific data)\n\n"
    "6. AI THESIS vs WALL STREET CONSENSUS BENCHMARK (MANDATORY)\n"
    "- State the Wall Street consensus recommendation and mean price target from the live data.\n"
    "- Provide a table benchmarking YOUR AI-generated bull/bear thesis against analyst consensus on DIRECTIONAL CALLS.\n"
    "- For each row, mark whether the AI view AGREES or DIVERGES from the Street, and explain the most important divergence.\n"
    "- Never omit this section.\n\n"
    "7. VALUATION AND RECOMMENDATION\n"
    "- Fair value estimate (with brief method)\n"
    "- 12-month price target\n"
    "- Investment recommendation (Buy/Hold/Sell)\n\n"
    "Be specific with numbers from the live data. Flag genuine uncertainty, but do not refuse to analyse."
)

print("Generating investment memo...\n")
message = client.messages.create(
    model="claude-haiku-4-5-20251001",
    max_tokens=4096,
    messages=[{"role": "user", "content": prompt}]
)

result = message.content[0].text
try:
    print(result)
except UnicodeEncodeError:
    sys.stdout.reconfigure(encoding='utf-8', errors='replace')
    print(result)

save_memo(ticker, result)