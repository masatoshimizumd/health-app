import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime

# --- Google Sheets 認証 ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("health_data").sheet1  # シート名が "health_data" であること

st.title("📊 健康データ記録アプリ（Google Sheets版）")

# --- 入力フォーム ---
with st.form("input_form"):
    date = st.date_input("日付", value=datetime.date.today())
    systolic = st.text_input("収縮期血圧 (mmHg)", "")
    diastolic = st.text_input("拡張期血圧 (mmHg)", "")
    pulse = st.text_input("脈拍 (bpm)", "")
    weight = st.text_input("体重 (kg)", "")
    fat = st.text_input("体脂肪率 (%)", "")
    glucose = st.text_input("血糖値 (mg/dL)", "")
    submitted = st.form_submit_button("保存")

    if submitted:
        # 空文字を None に変換
        row = [
            str(date),
            int(systolic) if systolic else None,
            int(diastolic) if diastolic else None,
            int(pulse) if pulse else None,
            float(weight) if weight else None,
            float(fat) if fat else None,
            int(glucose) if glucose else None
        ]
        sheet.append_row(row)
        st.success("✅ Googleスプレッドシートに保存しました！")

# --- データ一覧の表示 ---
records = sheet.get_all_records()
df = pd.DataFrame(records)

st.subheader("データ一覧")
st.dataframe(df)

# --- グラフ表示（おまけ） ---
if not df.empty:
    st.line_chart(df.set_index("date")[["systolic","diastolic","pulse","weight","fat","glucose"]])
