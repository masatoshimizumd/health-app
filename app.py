import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- Google Sheets 認証 ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)

# スプレッドシートを開く
sheet = client.open("health_data").sheet1

st.title("📊 健康データ記録アプリ（Google Sheets版）")

# --- データ読み込み ---
records = sheet.get_all_records()
df = pd.DataFrame(records)

# --- 新規追加フォーム ---
st.subheader("新しいデータを追加")

with st.form("input_form"):
    date = st.date_input("日付", value=datetime.date.today())

    # --- HTML入力（電卓キーボードがiPhoneで必ず出る） ---
    st.markdown('<label>収縮期血圧 (mmHg)</label><input type="number" inputmode="numeric" name="systolic" id="systolic" style="width:100%;padding:5px;">', unsafe_allow_html=True)
    st.markdown('<label>拡張期血圧 (mmHg)</label><input type="number" inputmode="numeric" name="diastolic" id="diastolic" style="width:100%;padding:5px;">', unsafe_allow_html=True)
    st.markdown('<label>脈拍 (bpm)</label><input type="number" inputmode="numeric" name="pulse" id="pulse" style="width:100%;padding:5px;">', unsafe_allow_html=True)
    st.markdown('<label>体重 (kg)</label><input type="number" inputmode="numeric" name="weight" id="weight" style="width:100%;padding:5px;">', unsafe_allow_html=True)
    st.markdown('<label>体脂肪率 (%)</label><input type="number" inputmode="numeric" name="fat" id="fat" style="width:100%;padding:5px;">', unsafe_allow_html=True)
    st.markdown('<label>血糖値 (mg/dL)</label><input type="number" inputmode="numeric" name="glucose" id="glucose" style="width:100%;padding:5px;">', unsafe_allow_html=True)

    submitted = st.form_submit_button("保存")

    if submitted:
        # ⚠️ ここで JavaScript/streamlit_js_eval などを使って値を取得する必要あり
        # 簡単化のため、一旦 st.session_state を利用する仕組みにするのが良いです
        st.warning("⚠️ このバージョンでは入力値取得の仕組みを追加する必要があります。")
