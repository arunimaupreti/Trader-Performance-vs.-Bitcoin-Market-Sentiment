"""
Step 1: Load, clean, and merge trader data with Fear/Greed sentiment index.
"""
import pandas as pd
import numpy as np

# ---- Load ----
fg = pd.read_csv('/mnt/user-data/uploads/fear_greed_index.csv')
hd = pd.read_csv('/mnt/user-data/uploads/historical_data.csv')

# ---- Clean Fear/Greed index ----
fg['date'] = pd.to_datetime(fg['date'])
fg = fg[['date', 'classification', 'value']].rename(
    columns={'classification': 'sentiment', 'value': 'sentiment_score'}
)

# Collapse to a simplified 3-bucket sentiment for cleaner comparisons
sentiment_map = {
    'Extreme Fear': 'Fear',
    'Fear': 'Fear',
    'Neutral': 'Neutral',
    'Greed': 'Greed',
    'Extreme Greed': 'Greed',
}
fg['sentiment_simple'] = fg['sentiment'].map(sentiment_map)

# ---- Clean trader data ----
hd['dt'] = pd.to_datetime(hd['Timestamp IST'], format='%d-%m-%Y %H:%M')
hd['date'] = hd['dt'].dt.normalize()

# Standardize column names
hd = hd.rename(columns={
    'Account': 'account',
    'Coin': 'coin',
    'Execution Price': 'exec_price',
    'Size Tokens': 'size_tokens',
    'Size USD': 'size_usd',
    'Side': 'side',
    'Start Position': 'start_position',
    'Direction': 'direction',
    'Closed PnL': 'closed_pnl',
    'Fee': 'fee',
    'Trade ID': 'trade_id',
})

keep_cols = ['account', 'coin', 'exec_price', 'size_tokens', 'size_usd', 'side',
             'dt', 'date', 'start_position', 'direction', 'closed_pnl', 'fee', 'trade_id']
hd = hd[keep_cols]

# Flag closing trades (only closing trades realize PnL)
hd['is_close'] = hd['direction'].isin(['Close Long', 'Close Short', 'Buy', 'Sell']) & (hd['closed_pnl'] != 0)
hd['is_win'] = hd['closed_pnl'] > 0

# ---- Merge on date ----
merged = hd.merge(fg[['date', 'sentiment', 'sentiment_simple', 'sentiment_score']], on='date', how='left')

print(f"Trader rows: {len(hd):,}")
print(f"Merged rows: {len(merged):,}")
print(f"Unmatched sentiment rows (no FG data for that date): {merged['sentiment'].isna().sum():,} "
      f"({merged['sentiment'].isna().mean()*100:.1f}%)")

merged = merged.dropna(subset=['sentiment'])
print(f"Final analysis rows after dropping unmatched dates: {len(merged):,}")
print(f"Date range analyzed: {merged['date'].min().date()} to {merged['date'].max().date()}")
print(f"Unique accounts: {merged['account'].nunique()}")
print(f"Unique coins: {merged['coin'].nunique()}")

merged.to_pickle('/home/claude/analysis/merged.pkl')
print("\nSaved merged.pkl")
print(merged['sentiment'].value_counts())
