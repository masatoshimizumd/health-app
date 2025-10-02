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
    systolic = st.text_input("収縮期血圧 (mmHg)", "")
    diastolic = st.text_input("拡張期血圧 (mmHg)", "")
    pulse = st.text_input("脈拍 (bpm)", "")
    weight = st.text_input("体重 (kg)", "")
    fat = st.text_input("体脂肪率 (%)", "")
    glucose = st.text_input("血糖値 (mg/dL)", "")
    submitted = st.form_submit_button("保存")

    if submitted:
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

# --- データ修正フォーム ---
st.subheader("既存データを修正")
if not df.empty:
    selected_date = st.selectbox("修正する日付を選択してください", df["date"].unique())

    if selected_date:
        record = df[df["date"] == selected_date].iloc[0]

        new_systolic = st.text_input("収縮期血圧", record["systolic"])
        new_diastolic = st.text_input("拡張期血圧", record["diastolic"])
        new_pulse = st.text_input("脈拍", record["pulse"])
        new_weight = st.text_input("体重", record["weight"])
        new_fat = st.text_input("体脂肪率", record["fat"])
        new_glucose = st.text_input("血糖値", record["glucose"])

        if st.button("更新"):
            row_index = df.index[df["date"] == selected_date][0] + 2  # 1行目はヘッダーなので+2
            sheet.update(
                f"A{row_index}:G{row_index}",
                [[selected_date, new_systolic, new_diastolic, new_pulse,
                  new_weight, new_fat, new_glucose]]
            )
            st.success("✅ データを更新しました！")

# --- データ一覧の表示 ---
st.subheader("データ一覧")
st.dataframe(df)
