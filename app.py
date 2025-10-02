import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
import streamlit.components.v1 as components

# --- Google Sheets 認証 ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)

# スプレッドシートを開く
sheet = client.open("health_data").sheet1

# --- タイトルを変更 ---
st.markdown("<h1 style='font-family:Arial,Helvetica,sans-serif;'>smt-health_data</h1>", unsafe_allow_html=True)

# --- データ読み込み ---
records = sheet.get_all_records()
df = pd.DataFrame(records)

# --- 入力フォーム ---
st.subheader("新しいデータを追加")

with st.form("input_form"):
    date = st.date_input("日付", value=datetime.date.today())

    # CSS調整（フォント＝ゴシック系、幅を狭める）
    css_style = """
    <style>
    input[type=number] {
        font-family: Arial, Helvetica, sans-serif;
        width: 120px;   /* 入力欄の幅を狭める */
        padding: 5px;
        margin-bottom: 8px;
    }
    label {
        font-family: Arial, Helvetica, sans-serif;
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

    # iPhone電卓キーボード用 inputmode="numeric"
    systolic = components.html('<input type="number" inputmode="numeric" id="systolic" placeholder="収縮期血圧">', height=40)
    diastolic = components.html('<input type="number" inputmode="numeric" id="diastolic" placeholder="拡張期血圧">', height=40)
    pulse = components.html('<input type="number" inputmode="numeric" id="pulse" placeholder="脈拍">', height=40)
    weight = components.html('<input type="number" inputmode="numeric" id="weight" placeholder="体重">', height=40)
    fat = components.html('<input type="number" inputmode="numeric" id="fat" placeholder="体脂肪率">', height=40)
    glucose = components.html('<input type="number" inputmode="numeric" id="glucose" placeholder="血糖値">', height=40)

    submitted = st.form_submit_button("保存")

    if submitted:
        # --- 入力値取得（JS経由でセッションに反映する仕組みを利用） ---
        # 今回はシンプルに st.session_state から受け取れるよう構成するのが安全
        st.warning("⚠️ 値のバインディング実装が必要です（送信ボタンなしで直接保存するため）。")
