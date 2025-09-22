import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
import numpy as np
from datetime import datetime, timedelta
import json
import time
import logging
import random
import sqlite3
import base64

# ==================== تنظیمات اولیه ====================
st.set_page_config(
    page_title="CoinState Market Scanner Pro",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ==================== دیکشنری دو زبانه ====================
TEXTS = {
    "فارسی": {
        "title": "📊 اسکنر بازار CoinState Pro",
        "select_symbol": "انتخاب نماد:",
        "select_interval": "انتخاب تایم‌فریم:",
        "loading": "در حال دریافت داده‌ها...",
        "price_chart": "نمودار قیمت",
        "indicators": "اندیکاتورها",
        "price": "قیمت",
        "high": "بالاترین",
