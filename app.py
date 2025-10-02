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

    # CSS調整（入力欄を大きめに）
    css_style = """
    <style>
    input[type=number] {
        font-family: Arial, Helvetica, sans-serif;
        width: 180px;   /* 横幅を拡大 */
        font-size: 18px; /* 文字サイズを大きく */
        padding: 8px;
        margin-bottom: 10px;
    }
    label {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 16px;
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

    # HTML入力（電卓キーボード確定）
    systolic = st.text_input("収縮期血圧 (mmHg)", "")
    diastolic = st.text_input("拡張期血圧 (mmHg)", "")
    pulse = st.text_input("脈拍 (bpm)", "")
    weight = st.text_input("体重 (kg)", "")
    fat = st.text_input("体脂肪率 (%)", "")
    glucose = st.text_input("血糖値 (mg/dL)", "")

    submitted = st.form_submit_button("保存")

    if submitted:
        # --- 日付重複チェック ---
        if not df.empty and str(date) in df["date"].astype(str).values:
            st.error("⚠️ この日付のデータは既に存在します。")
        else:
            def to_number(x, cast_func):
                try:
                    return cast_func(x)
                except:
                    return None

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

            # 保存後にデータ再読み込み
            records = sheet.get_all_records()
            df = pd.DataFrame(records)

# --- 直近データの表示 ---
st.subheader("📅 直近の記録（最新5件）")
if not df.empty:
    st.dataframe(df.tail(5))  # 最新5件だけ表示
else:
    st.info("まだ記録がありません。")
