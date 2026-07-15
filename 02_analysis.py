"""
Step 2: Core analysis - trader performance vs market sentiment
"""
import pandas as pd
import numpy as np

pd.set_option('display.width', 140)
pd.set_option('display.max_columns', 20)

df = pd.read_pickle('/home/claude/analysis/merged.pkl')

order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
order_simple = ['Fear', 'Neutral', 'Greed']

# Only closing trades carry realized PnL signal
closes = df[df['closed_pnl'] != 0].copy()

print("="*70)
print("1. OVERALL PnL & WIN RATE BY SENTIMENT (5-bucket)")
print("="*70)
g = closes.groupby('sentiment').agg(
    trades=('closed_pnl', 'count'),
    total_pnl=('closed_pnl', 'sum'),
    avg_pnl=('closed_pnl', 'mean'),
    median_pnl=('closed_pnl', 'median'),
    win_rate=('is_win', 'mean'),
    total_volume_usd=('size_usd', 'sum'),
).reindex(order)
g['win_rate'] = (g['win_rate']*100).round(2)
g['avg_pnl'] = g['avg_pnl'].round(2)
g['total_pnl'] = g['total_pnl'].round(0)
g['total_volume_usd'] = g['total_volume_usd'].round(0)
print(g)
g.to_csv('/home/claude/analysis/tbl_pnl_by_sentiment.csv')

print("\n" + "="*70)
print("2. TRADE SIZE & POSITION BEHAVIOR BY SENTIMENT")
print("="*70)
g2 = df.groupby('sentiment').agg(
    trades=('size_usd','count'),
    avg_trade_size_usd=('size_usd','mean'),
    median_trade_size_usd=('size_usd','median'),
    avg_start_position=('start_position','mean'),
).reindex(order)
print(g2.round(2))

print("\n" + "="*70)
print("3. LONG vs SHORT BIAS BY SENTIMENT (open trades)")
print("="*70)
opens = df[df['direction'].isin(['Open Long','Open Short'])]
g3 = pd.crosstab(opens['sentiment'], opens['direction'], normalize='index').reindex(order) * 100
print(g3.round(1))

print("\n" + "="*70)
print("4. LONG vs SHORT PROFITABILITY BY SENTIMENT")
print("="*70)
close_dir = closes[closes['direction'].isin(['Close Long','Close Short'])]
g4 = close_dir.groupby(['sentiment','direction']).agg(
    trades=('closed_pnl','count'),
    avg_pnl=('closed_pnl','mean'),
    win_rate=('is_win','mean'),
    total_pnl=('closed_pnl','sum')
).round(2)
print(g4.reindex(order, level=0))

print("\n" + "="*70)
print("5. TOP / BOTTOM PERFORMING COINS BY SENTIMENT (min 50 trades)")
print("="*70)
coin_sent = closes.groupby(['sentiment','coin']).agg(
    trades=('closed_pnl','count'),
    total_pnl=('closed_pnl','sum'),
    avg_pnl=('closed_pnl','mean')
)
coin_sent = coin_sent[coin_sent['trades']>=50]
for s in order:
    if s in coin_sent.index.get_level_values(0):
        sub = coin_sent.loc[s].sort_values('avg_pnl', ascending=False)
        print(f"\n-- {s} -- top 3 by avg pnl:")
        print(sub.head(3).round(2))
        print(f"-- {s} -- bottom 3 by avg pnl:")
        print(sub.tail(3).round(2))

print("\n" + "="*70)
print("6. ACCOUNT-LEVEL CONSISTENCY: does trader skill matter more than sentiment?")
print("="*70)
acct_sent = closes.groupby(['account','sentiment'])['closed_pnl'].mean().unstack()
acct_sent = acct_sent.reindex(columns=order)
acct_overall = closes.groupby('account')['closed_pnl'].agg(['count','mean','sum']).sort_values('sum', ascending=False)
print("Top 5 accounts by total PnL:")
print(acct_overall.head(5).round(2))
print("\nBottom 5 accounts by total PnL:")
print(acct_overall.tail(5).round(2))

# Correlation between sentiment score and avg daily PnL
print("\n" + "="*70)
print("7. DAILY AGGREGATE: sentiment score vs daily total PnL / volume")
print("="*70)
daily = closes.groupby('date').agg(
    daily_pnl=('closed_pnl','sum'),
    daily_volume=('size_usd','sum'),
    trades=('closed_pnl','count'),
    sentiment_score=('sentiment_score','first')
)
corr_pnl = daily['sentiment_score'].corr(daily['daily_pnl'])
corr_vol = daily['sentiment_score'].corr(daily['daily_volume'])
corr_trades = daily['sentiment_score'].corr(daily['trades'])
print(f"Correlation(sentiment_score, daily total PnL):    {corr_pnl:.3f}")
print(f"Correlation(sentiment_score, daily volume):        {corr_vol:.3f}")
print(f"Correlation(sentiment_score, daily trade count):   {corr_trades:.3f}")
daily.to_csv('/home/claude/analysis/tbl_daily.csv')

print("\n" + "="*70)
print("8. EXTREME FEAR vs EXTREME GREED head-to-head")
print("="*70)
ef = closes[closes['sentiment']=='Extreme Fear']
eg = closes[closes['sentiment']=='Extreme Greed']
print(f"Extreme Fear:  trades={len(ef):,}, win_rate={ef['is_win'].mean()*100:.2f}%, avg_pnl=${ef['closed_pnl'].mean():.2f}, total_pnl=${ef['closed_pnl'].sum():,.0f}")
print(f"Extreme Greed: trades={len(eg):,}, win_rate={eg['is_win'].mean()*100:.2f}%, avg_pnl=${eg['closed_pnl'].mean():.2f}, total_pnl=${eg['closed_pnl'].sum():,.0f}")

# save closes and daily for plotting
closes.to_pickle('/home/claude/analysis/closes.pkl')
daily.to_pickle('/home/claude/analysis/daily.pkl')
print("\nDone.")
