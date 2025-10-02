import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import datetime
from streamlit_js_eval import streamlit_js_eval

# --- Google Sheets 認証 ---
scope = ["https://spreadsheets.google.com/feeds",
         "https://www.googleapis.com/auth/drive"]

creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
client = gspread.authorize(creds)

# スプレッドシートを開く
sheet = client.open("health_data").sheet1

# --- タイトル ---
st.markdown("<h1 style='font-family:Arial,Helvetica,sans-serif;'>smt-health_data</h1>", unsafe_allow_html=True)

# --- データ読み込み ---
records = sheet.get_all_records()
df = pd.DataFrame(records)

# --- 入力フォーム ---
st.subheader("新しいデータを追加")

with st.form("input_form"):
    date = st.date_input("日付", value=datetime.date.today())

    # --- CSSで入力欄を大きく & ゴシック体 ---
    css_style = """
    <style>
    input[type=number] {
        font-family: Arial, Helvetica, sans-serif;
        width: 250px;     /* 広めに */
        font-size: 22px;  /* 大きめ文字 */
        padding: 10px;
        margin-bottom: 12px;
        border-radius: 6px;
        border: 1px solid #ccc;
    }
    label {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 16px;
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

    # --- HTML input をJSで拾ってセッションに送る ---
    systolic = streamlit_js_eval(js_expressions="document.getElementById('systolic')?.value", key="systolic")
    diastolic = streamlit_js_eval(js_expressions="document.getElementById('diastolic')?.value", key="diastolic")
    pulse = streamlit_js_eval(js_expressions="document.getElementById('pulse')?.value", key="pulse")
    weight = streamlit_js_eval(js_expressions="document.getElementById('weight')?.value", key="weight")
    fat = streamlit_js_eval(js_expressions="document.getElementById('fat')?.value", key="fat")
    glucose = streamlit_js_eval(js_expressions="document.getElementById('glucose')?.value", key="glucose")

    # 実際の入力欄
    st.markdown('<input type="number" inputmode="numeric" id="systolic" placeholder="収縮期血圧 (mmHg)">', unsafe_allow_html=True)
    st.markdown('<input type="number" inputmode="numeric" id="diastolic" placeholder="拡張期血圧 (mmHg)">', unsafe_allow_html=True)
    st.markdown('<input type="number" inputmode="numeric" id="pulse" placeholder="脈拍 (bpm)">', unsafe_allow_html=True)
    st.markdown('<input type="number" inputmode="numeric" id="weight" placeholder="体重 (kg)">', unsafe_allow_html=True)
    st.markdown('<input type="number" inputmode="numeric" id="fat" placeholder="体脂肪率 (%)">', unsafe_allow_html=True)
    st.markdown('<input type="number" inputmode="numeric" id="glucose" placeholder="血糖値 (mg/dL)">', unsafe_allow_html=True)

    submitted = st.form_submit_button("保存")

    if submitted:
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

            # 保存後に再読み込み
            records = sheet.get_all_records()
            df = pd.DataFrame(records)

# --- 直近データ表示 ---
st.subheader("📅 直近の記録（最新5件）")
if not df.empty:
    st.dataframe(df.tail(5))
else:
    st.info("まだ記録がありません。")
