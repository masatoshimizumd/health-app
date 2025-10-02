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

    # iPhoneで電卓キーボードを出したいので text_input を利用
    systolic = st.text_input("収縮期血圧 (mmHg)", value="", placeholder="数値を入力")
    diastolic = st.text_input("拡張期血圧 (mmHg)", value="", placeholder="数値を入力")
    pulse = st.text_input("脈拍 (bpm)", value="", placeholder="数値を入力")
    weight = st.text_input("体重 (kg)", value="", placeholder="数値を入力")
    fat = st.text_input("体脂肪率 (%)", value="", placeholder="数値を入力")
    glucose = st.text_input("血糖値 (mg/dL)", value="", placeholder="数値を入力")

    submitted = st.form_submit_button("保存")

    if submitted:
        # --- 入力チェック関数 ---
        def to_number(x, cast_func):
            try:
                return cast_func(x)
            except:
                return None

        # --- 日付重複チェック ---
        if not df.empty and str(date) in df["date"].astype(str).values:
            st.error("⚠️ この日付のデータは既に存在します。")
        else:
            row = [
                str(date),
                to_number(systolic, int),
                to_number(diastolic, int),
                to_number(pulse, int),
                to_number(weight, float),
                to_number(fat, float),
                to_number(glucose, int)
            ]
            sheet.append_row(row)
            st.success("✅ Googleスプレッドシートに保存しました！")

# --- データ一覧の表示 ---
st.subheader("データ一覧")
st.dataframe(df)
