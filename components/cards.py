import streamlit as st

def render_metric_card(title, value, change, theme):
    """کارت متریک"""
    change_html = ""
    if change:
        change_color = theme['success'] if change.startswith('+') else theme['error']
        change_html = f"""<div style="color: {change_color}; font-size: 0.9rem; margin-top: 0.5rem;">{change}</div>"""
    
    html_content = f"""
    <div style="background: {theme['surface']}; padding: 1.5rem; border-radius: 12px; border-left: 4px solid {theme['primary']}; margin: 0.5rem 0;">
        <div style="color: {theme['text_secondary']}; font-size: 0.9rem;">{title}</div>
        <div style="color: {theme['text_primary']}; font-size: 1.8rem; font-weight: bold; margin: 0.5rem 0;">{value}</div>
        {change_html}
    </div>
    """
    st.html(html_content)

def render_coin_card(coin, theme):
    """کارت نمایش کوین"""
    change_color = theme['success'] if coin['change_24h'] >= 0 else theme['error']
    change_icon = "📈" if coin['change_24h'] >= 0 else "📉"
    
    anomaly_badge = ""
    if coin['anomaly']:
        anomaly_badge = f"""
        <div style="background: {theme['warning']}; color: white; padding: 0.2rem 0.5rem; border-radius: 12px; font-size: 0.7rem; display: inline-block; margin-left: 0.5rem;">
            ⚠️ Anomaly
        </div>
        """
    
    html_content = f"""
    <div style="background: {theme['surface']}; padding: 1rem; border-radius: 10px; border: 1px solid {theme['border']}; margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="font-size: 1.5rem;">🪙</div>
                <div>
                    <div style="display: flex; align-items: center;">
                        <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                            {coin['symbol']}
                        </div>
                        {anomaly_badge}
                    </div>
                    <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">{coin['name']}</div>
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="font-weight: bold; color: {theme['text_primary']}; font-size: 1.1rem;">
                    ${coin['price']:,.2f}
                </div>
                <div style="color: {change_color}; font-size: 0.9rem;">
                    {change_icon} {coin['change_24h']:+.2f}%
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Signal</div>
                <div style="color: {theme['primary']}; font-weight: bold; font-size: 1.1rem;">
                    {coin['signal']}/10
                </div>
            </div>
            
            <div style="text-align: center;">
                <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">Volume</div>
                <div style="color: {theme['text_primary']}; font-size: 0.9rem;">
                    ${coin['volume']/1000000:.1f}M
                </div>
            </div>
        </div>
    </div>
    """
    st.html(html_content)

def render_alert_card(alert, theme):
    """کارت هشدار"""
    alert_colors = {
        "volume": theme['warning'],
        "price": theme['error'],
        "signal": theme['success']
    }
    
    html_content = f"""
    <div style="background: {theme['surface']}; padding: 1rem; border-radius: 10px; border-left: 4px solid {alert_colors[alert['type']]}; margin: 0.5rem 0;">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <div style="font-weight: bold; color: {theme['text_primary']};">
                    {alert['coin']} - {alert['message']}
                </div>
            </div>
            <div style="color: {theme['text_secondary']}; font-size: 0.8rem;">
                {alert['time']}
            </div>
        </div>
    </div>
    """
    st.html(html_content)
