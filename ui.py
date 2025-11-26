import streamlit as st
import requests
import json
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime, timedelta

# Page config
st.set_page_config(
    page_title="AI Investment Analyst",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS to mimic Google Finance Dark Mode
st.markdown("""
    <style>
    /* General App Styling */
    .stApp {
        background-color: #202124;
        color: #e8eaed;
    }
    
    /* Metrics Styling */
    div[data-testid="stMetricValue"] {
        font-size: 36px;
        font-weight: 400;
        font-family: 'Google Sans', sans-serif;
    }
    div[data-testid="stMetricDelta"] {
        font-size: 16px;
        font-weight: 500;
    }
    
    /* Custom Stats Grid */
    .stat-label {
        color: #9aa0a6;
        font-size: 12px;
        margin-bottom: 4px;
    }
    .stat-value {
        color: #e8eaed;
        font-size: 14px;
        font-weight: 500;
        border-bottom: 1px solid #3c4043;
        padding-bottom: 8px;
        margin-bottom: 8px;
    }
    
    /* Radio Button as Tabs Styling */
    div[role="radiogroup"] {
        display: flex;
        gap: 8px;
        background-color: transparent;
        margin-bottom: 10px;
    }
    div[role="radiogroup"] label {
        background-color: transparent !important;
        border: 1px solid #3c4043;
        border-radius: 16px;
        padding: 4px 16px;
        color: #9aa0a6;
        font-size: 12px;
        cursor: pointer;
        transition: all 0.2s;
    }
    div[role="radiogroup"] label[data-checked="true"] {
        background-color: #8ab4f8 !important;
        color: #202124 !important;
        border-color: #8ab4f8 !important;
    }
    div[role="radiogroup"] div[data-testid="stMarkdownContainer"] p {
        font-size: 12px;
    }
    
    /* Remove default padding */
    .main .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    
    /* Input Area Styling */
    .stTextArea textarea {
        background-color: #303134;
        color: #e8eaed;
        border: 1px solid #3c4043;
        border-radius: 8px;
    }
    </style>
    """, unsafe_allow_html=True)

# Helper functions
def get_stock_data(ticker, period="1d"):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        # Map period to yfinance format
        # 1天=1d, 5天=5d, 1個月=1mo, 6個月=6mo, 本年迄今=ytd, 1年=1y, 5年=5y, 最久=max
        interval = "1d"
        if period == "1d":
            interval = "1m"
        elif period == "5d":
            interval = "15m"
        elif period in ["1mo", "3mo"]:
            interval = "1h" # Better granularity for 1 month
            
        history = stock.history(period=period, interval=interval)
        
        # Fallback if granular data is missing
        if history.empty and period == "1d":
             history = stock.history(period="1d", interval="15m")
             
        return info, history
    except Exception as e:
        return None, None

def plot_google_finance_chart(history, ticker):
    if history.empty:
        return go.Figure()

    # Determine color based on change
    start_price = history['Close'].iloc[0]
    end_price = history['Close'].iloc[-1]
    line_color = "#81c995" if end_price >= start_price else "#f28b82"
    
    # Calculate dynamic Y-axis range
    min_price = history['Low'].min()
    max_price = history['High'].max()
    padding = (max_price - min_price) * 0.05 if max_price != min_price else max_price * 0.01
    y_range = [min_price - padding, max_price + padding]

    # Prepare X-axis labels and ticks
    # We use type='category' to remove gaps (non-trading days/hours)
    # But we need to manually handle ticks to avoid overcrowding
    
    # 1. Format all dates for hover/x-axis values
    # Determine format based on time range
    time_diff = history.index[-1] - history.index[0]
    
    if time_diff <= timedelta(days=1):
        # Intraday
        date_format = "%H:%M"
        hover_format = "%H:%M"
    elif time_diff <= timedelta(days=365):
        # < 1 Year
        date_format = "%m/%d"
        hover_format = "%b %d"
    else:
        # > 1 Year
        date_format = "%Y/%m"
        hover_format = "%b %Y"
        
    # Convert index to string for category axis
    # Note: yfinance index is datetime, we convert to formatted string
    # We use a separate list for display to keep the plot clean
    x_values = history.index.strftime(hover_format) # For hover
    
    # 2. Select specific ticks to display (e.g., 6-7 ticks)
    num_ticks = 7
    if len(history) > num_ticks:
        import numpy as np
        tick_indices = np.linspace(0, len(history) - 1, num=num_ticks, dtype=int)
        tick_vals = [history.index[i] for i in tick_indices]
        tick_text = [history.index[i].strftime(date_format) for i in tick_indices]
    else:
        tick_vals = history.index
        tick_text = [d.strftime(date_format) for d in history.index]

    fig = go.Figure()
    
    # Area Chart
    # We pass x as the original datetime index but set type='category' in layout
    # This ensures Plotly treats them as discrete buckets (no gaps)
    fig.add_trace(go.Scatter(
        x=history.index, 
        y=history['Close'],
        mode='lines',
        fill='tozeroy',
        line=dict(color=line_color, width=2),
        fillcolor=f"rgba({int(line_color[1:3], 16)}, {int(line_color[3:5], 16)}, {int(line_color[5:7], 16)}, 0.1)",
        name=ticker,
        hovertemplate=f"%{{x|{hover_format}}}<br>Price: %{{y:.2f}}<extra></extra>"
    ))

    fig.update_layout(
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(
            type='category', # This removes the gaps!
            showgrid=False, 
            showticklabels=True,
            linecolor='#3c4043',
            tickfont=dict(color='#9aa0a6'),
            tickmode='array',
            tickvals=tick_vals,
            ticktext=tick_text
        ),
        yaxis=dict(
            showgrid=True, 
            gridcolor='#3c4043',
            showticklabels=True,
            tickfont=dict(color='#9aa0a6'),
            side='right',
            range=y_range
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=350,
        hovermode="x unified",
        showlegend=False
    )
    return fig

def format_large_number(num):
    if not num: return "-"
    if num >= 1_000_000_000_000:
        return f"{num/1_000_000_000_000:.2f}兆"
    if num >= 1_000_000_000:
        return f"{num/1_000_000_000:.2f}0億"
    if num >= 1_000_000:
        return f"{num/1_000_000:.2f}百萬"
    return f"{num:,.2f}"

# --- Main Application ---

st.title("🤖 AI 投資分析助理")

# Input Section
query = st.text_area("請輸入您的投資問題或感興趣的股票：", placeholder="例如：分析台積電 (TSM) 和輝達 (NVDA) 的近期表現與風險...", height=100)

if st.button("🚀 開始分析", type="primary"):
    if not query:
        st.warning("請輸入問題")
    else:
        with st.spinner("代理人團隊正在進行深度研究... (這可能需要一分鐘)"):
            try:
                response = requests.post("http://localhost:8000/research", json={"query": query})
                if response.status_code == 200:
                    st.session_state.research_result = response.json()
                else:
                    st.error(f"API Error: {response.text}")
            except Exception as e:
                st.error(f"Connection Error: {str(e)}")

# Results Display
if 'research_result' in st.session_state:
    result = st.session_state.research_result
    tickers = result.get("tickers", [])
    
    st.markdown("---")
    
    # 1. Dashboard Section
    if tickers:
        st.subheader("📈 市場儀表板")
        
        # Ticker Selector
        selected_ticker = tickers[0]
        if len(tickers) > 1:
            # Use radio as pills for selection
            selected_ticker = st.radio("選擇股票", tickers, horizontal=True, label_visibility="collapsed")
        
        # Render Dashboard for selected ticker
        # Time Period Selector
        period_options = {
            "1 天": "1d", "5 天": "5d", "1 個月": "1mo", "6 個月": "6mo",
            "本年迄今": "ytd", "1 年": "1y", "5 年": "5y", "最久": "max"
        }
        
        # Default to 1mo
        if 'selected_period_label' not in st.session_state:
            st.session_state.selected_period_label = "1 個月"
            
        # Fetch Data
        stock = yf.Ticker(selected_ticker)
        info = stock.info
        
        if info:
            # Breadcrumb
            st.markdown(f"<div style='color: #9aa0a6; font-size: 14px; margin-bottom: 5px;'>市場概況 > {info.get('longName', selected_ticker)}</div>", unsafe_allow_html=True)
            
            # Time Selector UI
            selected_label = st.radio(
                "Time Period",
                options=list(period_options.keys()),
                horizontal=True,
                label_visibility="collapsed",
                key=f"period_selector_{selected_ticker}", # Unique key per ticker
                index=2
            )
            selected_period_code = period_options[selected_label]
            
            # Fetch History
            _, history = get_stock_data(selected_ticker, period=selected_period_code)
            
            # Price Section
            current_price = info.get('currentPrice', info.get('regularMarketPrice', 0))
            
            if not history.empty:
                if selected_period_code == "1d":
                    start_price = info.get('previousClose', history['Open'].iloc[0])
                    end_price = history['Close'].iloc[-1]
                    if info.get('currentPrice'): end_price = info.get('currentPrice')
                else:
                    start_price = history['Close'].iloc[0]
                    end_price = history['Close'].iloc[-1]
                    
                change = end_price - start_price
                change_pct = (change / start_price) * 100
            else:
                change = 0
                change_pct = 0
                
            color_class = "#81c995" if change >= 0 else "#f28b82"
            sign = "+" if change >= 0 else ""
            period_text = "今天" if selected_period_code == "1d" else f"過去 {selected_label}"
            
            st.markdown(f"""
                <div style="display: flex; align-items: baseline; gap: 10px; margin-top: -10px;">
                    <span style="font-size: 36px; font-weight: 400; color: #e8eaed;">{current_price:.2f}</span>
                    <span style="font-size: 14px; color: #9aa0a6;">{info.get('currency', 'USD')}</span>
                    <span style="font-size: 16px; color: {color_class}; font-weight: 500;">
                        {sign}{change:.2f} ({change_pct:.2f}%) {sign if change >=0 else '↓'} {period_text}
                    </span>
                </div>
                <div style="color: #9aa0a6; font-size: 12px; margin-bottom: 20px;">
                    已收盤 • 免責聲明
                </div>
            """, unsafe_allow_html=True)

            # Chart
            if history is not None and not history.empty:
                st.plotly_chart(plot_google_finance_chart(history, selected_ticker), use_container_width=True, config={'displayModeBar': False})
            else:
                st.warning("暫無此時段數據")

            # Stats Grid
            st.markdown("<br>", unsafe_allow_html=True)
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown(f"""
                    <div class='stat-label'>開盤</div><div class='stat-value'>{info.get('open', '-')}</div>
                    <div class='stat-label'>最高</div><div class='stat-value'>{info.get('dayHigh', '-')}</div>
                    <div class='stat-label'>最低</div><div class='stat-value'>{info.get('dayLow', '-')}</div>
                """, unsafe_allow_html=True)
                
            with col2:
                mkt_cap = format_large_number(info.get('marketCap'))
                pe_ratio = f"{info.get('trailingPE', '-'):.2f}" if info.get('trailingPE') else "-"
                
                div_yield_raw = info.get('dividendYield')
                if div_yield_raw is not None:
                    div_yield = f"{div_yield_raw:.2f}%"
                else:
                    div_yield_raw = info.get('trailingAnnualDividendYield')
                    div_yield = f"{div_yield_raw*100:.2f}%" if div_yield_raw is not None else "-"
                
                st.markdown(f"""
                    <div class='stat-label'>市值</div><div class='stat-value'>{mkt_cap}</div>
                    <div class='stat-label'>本益比</div><div class='stat-value'>{pe_ratio}</div>
                    <div class='stat-label'>殖利率</div><div class='stat-value'>{div_yield}</div>
                """, unsafe_allow_html=True)
                
            with col3:
                high_52 = info.get('fiftyTwoWeekHigh', '-')
                low_52 = info.get('fiftyTwoWeekLow', '-')
                div_rate = info.get('dividendRate', '-')
                
                st.markdown(f"""
                    <div class='stat-label'>52 週高點</div><div class='stat-value'>{high_52}</div>
                    <div class='stat-label'>52 週低點</div><div class='stat-value'>{low_52}</div>
                    <div class='stat-label'>股利金額</div><div class='stat-value'>{div_rate}</div>
                """, unsafe_allow_html=True)
        else:
            st.error(f"無法獲取 {selected_ticker} 的數據")

    # 2. Report Section
    st.markdown("---")
    st.subheader("📝 AI 投資報告")
    
    t1, t2, t3, t4 = st.tabs(["最終建議", "數據分析", "新聞摘要", "風險評估"])
    
    with t1:
        st.markdown(result.get("final_report", "無報告"))
    with t2:
        st.markdown(result.get("data_analysis", "無數據"))
    with t3:
        st.markdown(result.get("news_analysis", "無新聞"))
    with t4:
        st.markdown(result.get("risk_assessment", "無風險評估"))
