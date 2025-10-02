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
    systolic = st.number_input("収縮期血圧 (mmHg)", min_value=0, max_value=300, step=1)
    diastolic = st.number_input("拡張期血圧 (mmHg)", min_value=0, max_value=200, step=1)
    pulse = st.number_input("脈拍 (bpm)", min_value=0, max_value=250, step=1)
    weight = st.number_input("体重 (kg)", min_value=0.0, max_value=200.0, step=0.1)
    fat = st.number_input("体脂肪率 (%)", min_value=0.0, max_value=100.0, step=0.1)
    glucose = st.number_input("血糖値 (mg/dL)", min_value=0, max_value=1000, step=1)
    submitted = st.form_submit_button("保存")

    if submitted:
        # --- 日付重複チェック ---
        if not df.empty and str(date) in df["date"].astype(str).values:
            st.error("⚠️ この日付のデータは既に存在します。別の日付を選んでください。")
        else:
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

        new_systolic = st.number_input("収縮期血圧", value=int(record["systolic"]) if record["systolic"] else 0)
        new_diastolic = st.number_input("拡張期血圧", value=int(record["diastolic"]) if record["diastolic"] else 0)
        new_pulse = st.number_input("脈拍", value=int(record["pulse"]) if record["pulse"] else 0)
        new_weight = st.number_input("体重", value=float(record["weight"]) if record["weight"] else 0.0)
        new_fat = st.number_input("体脂肪率", value=float(record["fat"]) if record["fat"] else 0.0)
        new_glucose = st.number_input("血糖値", value=int(record["glucose"]) if record["glucose"] else 0)

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
