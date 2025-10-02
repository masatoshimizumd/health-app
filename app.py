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

    # CSSで縦並び・余白調整・日付を大きく
    css_style = """
    <style>
    .input-block {
        display: flex;
        flex-direction: column;
        margin-bottom: 6px;   /* 各項目間の余白を小さく */
        font-family: Arial, Helvetica, sans-serif;
    }
    .input-block label {
        font-size: 14px;
        margin-bottom: 2px;
    }
    .input-block input {
        width: 220px;
        font-size: 20px;
        padding: 6px;
        border-radius: 6px;
        border: 1px solid #ccc;
    }
    .date-block input {
        width: 240px;
        font-size: 26px;   /* 日付だけ大きめ */
        font-weight: bold;
        padding: 6px;
        border-radius: 6px;
        border: 1px solid #333;
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

    # --- 入力欄（縦並び） ---
    today_str = datetime.date.today().strftime("%Y-%m-%d")

    st.markdown(
        f"""
        <div class="input-block date-block">
            <label>日付</label>
            <input type="date" id="date" value="{today_str}">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="input-block">
            <label>収縮期血圧 (mmHg)</label>
            <input type="number" inputmode="numeric" id="systolic">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="input-block">
            <label>拡張期血圧 (mmHg)</label>
            <input type="number" inputmode="numeric" id="diastolic">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="input-block">
            <label>脈拍 (bpm)</label>
            <input type="number" inputmode="numeric" id="pulse">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="input-block">
            <label>体重 (kg)</label>
            <input type="number" inputmode="numeric" id="weight">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="input-block">
            <label>体脂肪率 (%)</label>
            <input type="number" inputmode="numeric" id="fat">
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="input-block">
            <label>血糖値 (mg/dL)</label>
            <input type="number" inputmode="numeric" id="glucose">
        </div>
        """,
        unsafe_allow_html=True,
    )

    # --- JSから値を取得 ---
    date_val   = streamlit_js_eval("document.getElementById('date')?.value", key="date")
    systolic   = streamlit_js_eval("document.getElementById('systolic')?.value", key="systolic")
    diastolic  = streamlit_js_eval("document.getElementById('diastolic')?.value", key="diastolic")
    pulse      = streamlit_js_eval("document.getElementById('pulse')?.value", key="pulse")
    weight     = streamlit_js_eval("document.getElementById('weight')?.value", key="weight")
    fat        = streamlit_js_eval("document.getElementById('fat')?.value", key="fat")
    glucose    = streamlit_js_eval("document.getElementById('glucose')?.value", key="glucose")

    # --- 保存ボタン ---
    submitted = st.form_submit_button("保存")

    if submitted:
        if not df.empty and str(date_val) in df["date"].astype(str).values:
            st.error("⚠️ この日付のデータは既に存在します。")
        else:
            def to_number(x, cast_func):
                try:
                    return cast_func(x)
                except:
                    return None

            row = [
                str(date_val),
                to_number(systolic, int),
                to_number(diastolic, int),
                to_number(pulse, int),
                to_number(weight, float),
                to_number(fat, floa_
