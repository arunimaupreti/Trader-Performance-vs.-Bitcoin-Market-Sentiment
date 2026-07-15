import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.spines.top'] = False
plt.rcParams['axes.spines.right'] = False

order = ['Extreme Fear', 'Fear', 'Neutral', 'Greed', 'Extreme Greed']
colors = ['#8b1e1e', '#d9603b', '#9b9b9b', '#5fa777', '#1e6b3a']

closes = pd.read_pickle('/home/claude/analysis/closes.pkl')
daily = pd.read_pickle('/home/claude/analysis/daily.pkl')
df = pd.read_pickle('/home/claude/analysis/merged.pkl')

g = closes.groupby('sentiment').agg(
    trades=('closed_pnl','count'), total_pnl=('closed_pnl','sum'),
    avg_pnl=('closed_pnl','mean'), win_rate=('is_win','mean'),
    total_volume_usd=('size_usd','sum')
).reindex(order)

# ---- Chart 1: Avg PnL & Win rate by sentiment (dual axis) ----
fig, ax1 = plt.subplots(figsize=(8,5))
bars = ax1.bar(order, g['avg_pnl'], color=colors, alpha=0.85)
ax1.set_ylabel('Avg Closed PnL per Trade (USD)')
ax1.set_title('Trader Profitability vs Market Sentiment', fontsize=13, fontweight='bold')
ax1.axhline(0, color='black', linewidth=0.8)
for b, v in zip(bars, g['avg_pnl']):
    ax1.text(b.get_x()+b.get_width()/2, v + (2 if v>=0 else -6), f"${v:.0f}", ha='center', fontsize=9)

ax2 = ax1.twinx()
ax2.plot(order, g['win_rate']*100, color='#1a1a1a', marker='o', linewidth=2, label='Win Rate')
ax2.set_ylabel('Win Rate (%)')
ax2.set_ylim(60, 100)
for i, v in enumerate(g['win_rate']*100):
    ax2.text(i, v+1.2, f"{v:.1f}%", ha='center', fontsize=9, color='#1a1a1a')
plt.tight_layout()
plt.savefig('/home/claude/analysis/charts/01_pnl_winrate.png', dpi=150)
plt.close()

# ---- Chart 2: Total PnL & Volume by sentiment ----
fig, axes = plt.subplots(1, 2, figsize=(11,4.5))
axes[0].bar(order, g['total_pnl']/1e6, color=colors, alpha=0.85)
axes[0].set_title('Total Realized PnL by Sentiment')
axes[0].set_ylabel('Total PnL (USD, millions)')
axes[1].bar(order, g['total_volume_usd']/1e6, color=colors, alpha=0.85)
axes[1].set_title('Total Trading Volume by Sentiment')
axes[1].set_ylabel('Volume (USD, millions)')
for ax in axes:
    ax.tick_params(axis='x', rotation=20)
plt.tight_layout()
plt.savefig('/home/claude/analysis/charts/02_pnl_volume_totals.png', dpi=150)
plt.close()

# ---- Chart 3: Long/short bias by sentiment ----
opens = df[df['direction'].isin(['Open Long','Open Short'])]
bias = pd.crosstab(opens['sentiment'], opens['direction'], normalize='index').reindex(order)*100
fig, ax = plt.subplots(figsize=(8,5))
bottom = np.zeros(len(order))
for col, c in zip(['Open Long','Open Short'], ['#2e7d4f','#b23a2e']):
    ax.bar(order, bias[col], bottom=bottom, label=col, color=c, alpha=0.85)
    bottom += bias[col].values
ax.set_ylabel('% of position-opening trades')
ax.set_title('Long vs Short Positioning by Market Sentiment', fontsize=13, fontweight='bold')
ax.legend(loc='upper right')
ax.axhline(50, color='white', linewidth=1, linestyle='--')
plt.tight_layout()
plt.savefig('/home/claude/analysis/charts/03_long_short_bias.png', dpi=150)
plt.close()

# ---- Chart 4: Daily sentiment score vs daily PnL trend (rolling) ----
daily_sorted = daily.sort_index()
daily_sorted['pnl_roll'] = daily_sorted['daily_pnl'].rolling(14, min_periods=1).mean()
daily_sorted['score_roll'] = daily_sorted['sentiment_score'].rolling(14, min_periods=1).mean()

fig, ax1 = plt.subplots(figsize=(11,5))
ax1.plot(daily_sorted.index, daily_sorted['pnl_roll'], color='#1e6b3a', linewidth=1.6, label='14d Avg Daily PnL')
ax1.set_ylabel('14-day Avg Daily Realized PnL (USD)', color='#1e6b3a')
ax1.axhline(0, color='grey', linewidth=0.6)
ax2 = ax1.twinx()
ax2.plot(daily_sorted.index, daily_sorted['score_roll'], color='#8b1e1e', linewidth=1.2, alpha=0.7, label='14d Avg Fear/Greed Score')
ax2.set_ylabel('14-day Avg Fear & Greed Score', color='#8b1e1e')
ax1.set_title('Daily Trading PnL vs Market Sentiment Score Over Time', fontsize=13, fontweight='bold')
fig.autofmt_xdate()
plt.tight_layout()
plt.savefig('/home/claude/analysis/charts/04_timeseries.png', dpi=150)
plt.close()

# ---- Chart 5: Long vs Short win rate/avg pnl by sentiment ----
close_dir = closes[closes['direction'].isin(['Close Long','Close Short'])]
g4 = close_dir.groupby(['sentiment','direction'])['closed_pnl'].mean().unstack().reindex(order)
fig, ax = plt.subplots(figsize=(8,5))
x = np.arange(len(order))
w = 0.35
ax.bar(x-w/2, g4['Close Long'], w, label='Long trades', color='#2e7d4f', alpha=0.85)
ax.bar(x+w/2, g4['Close Short'], w, label='Short trades', color='#b23a2e', alpha=0.85)
ax.set_xticks(x); ax.set_xticklabels(order, rotation=15)
ax.set_ylabel('Avg Closed PnL per Trade (USD)')
ax.set_title('Long vs Short Avg PnL by Sentiment', fontsize=13, fontweight='bold')
ax.axhline(0, color='black', linewidth=0.8)
ax.legend()
plt.tight_layout()
plt.savefig('/home/claude/analysis/charts/05_long_short_pnl.png', dpi=150)
plt.close()

print("Charts saved:")
import os
for f in sorted(os.listdir('/home/claude/analysis/charts')):
    print(' -', f)
