# Trader Performance vs. Bitcoin Market Sentiment

Analysis of 211,224 Hyperliquid trade executions (32 accounts, 246 coins, May 2023 – May 2025) against the daily Bitcoin Fear & Greed Index, done as a data science hiring assignment for Primetrade.ai.

**TL;DR:** Traders in this dataset performed *best* during Fear and Extreme Greed regimes and *worst* during Extreme Fear — the opposite of the popular "buy when others are fearful" narrative. Trader skill also explains far more variance in outcomes than sentiment regime does.

## Key results

| Metric | Extreme Fear | Fear | Neutral | Greed | Extreme Greed |
|---|---|---|---|---|---|
| Trades (closed) | 10,406 | 29,808 | 18,159 | 25,176 | 20,853 |
| Win rate | 76.2% | 87.3% | 82.4% | 76.9% | 89.2% |
| Avg PnL / trade | $71.03 | $112.63 | $71.20 | $85.40 | $130.21 |
| Total realized PnL | $0.74M | $3.36M | $1.29M | $2.15M | $2.72M |

![Trader Profitability vs Market Sentiment](outputs/charts/01_pnl_winrate.png)

## Findings

1. **Non-monotonic performance** — Fear and Extreme Greed produce the strongest win rates and PnL; Extreme Fear is the weakest regime.
2. **Selectivity rises with greed** — average trade size falls from $7,816 (Fear) to $3,112 (Extreme Greed) as traders become more selective, not more aggressive.
3. **Contrarian positioning** — long bias (62–69%) in Fear/Neutral regimes flips to short bias (55–58%) in Greed regimes.
4. **Regime-dependent side profitability** — shorts outperform longs during Fear; longs outperform shorts during Greed/Extreme Greed.
5. **Skill beats sentiment** — the account-level PnL/trade spread is roughly 17–40x larger than the spread across sentiment regimes.
6. **Coin behavior is regime-dependent** — e.g. TRUMP is the top performer in Extreme Fear and the worst in Greed.

Full write-up, methodology, all charts, and strategic recommendations: **[`reports/Trader_Sentiment_Analysis_Report.docx`](reports/Trader_Sentiment_Analysis_Report.docx)**

## Repo structure

```
.
├── data/                    # place fear_greed_index.csv and historical_data.csv here (not committed, see below)
├── notebooks/
│   └── Trader_Sentiment_Analysis.ipynb   # full reproducible analysis, run top to bottom
├── src/
│   ├── 01_prepare_data.py   # load, clean, merge datasets on date
│   ├── 02_analysis.py       # core metrics: PnL/win-rate by sentiment, long/short bias, coin & account breakdowns
│   └── 03_charts.py         # generates all charts in outputs/charts/
├── outputs/
│   ├── charts/               # PNG charts referenced in the report and notebook
│   └── tables/                # exported summary tables (CSV)
├── reports/
│   └── Trader_Sentiment_Analysis_Report.docx   # final written report
└── requirements.txt
```

## Reproducing this analysis

```bash
git clone https://github.com/<your-username>/trader-sentiment-analysis.git
cd trader-sentiment-analysis
pip install -r requirements.txt

# place the two source CSVs in data/
#   data/fear_greed_index.csv
#   data/historical_data.csv

python src/01_prepare_data.py
python src/02_analysis.py
python src/03_charts.py

# or just run the notebook end to end:
jupyter notebook notebooks/Trader_Sentiment_Analysis.ipynb
```

## Data sources

- Bitcoin Fear & Greed Index (daily, 2018–2025)
- Hyperliquid historical trade data (account, coin, execution price, size, side, direction, closed PnL, fees, timestamps)

Raw CSVs are not committed to this repo due to size — see the assignment brief for the original download links, or drop your own copies into `data/`.

## Limitations

- The 32 accounts here are not necessarily representative of the broader Hyperliquid trader base.
- Sentiment is a daily, BTC-wide signal used as a proxy for "market mood" across all 246 coins traded — it is not coin-specific.
- Findings describe association, not causation.
