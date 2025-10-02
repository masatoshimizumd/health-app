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

    # 🔹 日付 + 血圧2項目を横並びに
    col1, col2, col3 = st.columns([1,1,1])

    with col1:
        date = st.date_input("日付", value=datetime.date.today())

    with col2:
        st.markdown(
            """
            <div class="input-block">
              <label>収縮期血圧 (mmHg)</label><br>
              <input type="number" inputmode="numeric" id="systolic">
            </div>
            """,
            unsafe_allow_html=True
        )
        systolic = streamlit_js_eval(
            js_expressions="document.getElementById('systolic')?.value", key="systolic"
        )

    with col3:
        st.markdown(
            """
            <div class="input-block">
              <label>拡張期血圧 (mmHg)</label><br>
              <input type="number" inputmode="numeric" id="diastolic">
            </div>
            """,
            unsafe_allow_html=True
        )
        diastolic = streamlit_js_eval(
            js_expressions="document.getElementById('diastolic')?.value", key="diastolic"
        )

    # CSS で入力欄デザインを調整
    css_style = """
    <style>
    .input-block {
        margin-bottom: 6px;
    }
    input[type=number] {
        font-family: Arial, Helvetica, sans-serif;
        width: 200px;
        font-size: 18px;
        padding: 6px;
        border-radius: 6px;
        border: 1px solid #ccc;
    }
    label {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 14px;
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

    # 🔹 その他の入力欄（縦並び）
    st.markdown(
        '<label>脈拍 (bpm)</label><br><input type="number" inputmode="numeric" id="pulse">',
        unsafe_allow_html=True
    )
    pulse = streamlit_js_eval(
        js_expressions="document.getElementById('pulse')?.value", key="pulse"
    )

    st.markdown(
        '<label>体重 (kg)</label><br><input type="number" inputmode="numeric" id="weight">',
        unsafe_allow_html=True
    )
    weight = streamlit_js_eval(
        js_expressions="document.getElementById('weight')?.value", key="weight"
    )

    st.markdown(
        '<label>体脂肪率 (%)</label><br><input type="number" inputmode="numeric" id="fat">',
        unsafe_allow_html=True
    )
    fat = streamlit_js_eval(
        js_expressions="document.getElementById('fat')?.value", key="fat"
    )

    st.markdown(
        '<label>血糖値 (mg/dL)</label><br><input type="number" inputmode="numeric" id="glucose">',
        unsafe_allow_html=True
    )
    glucose = streamlit_js_eval(
        js_expressions="document.getElementById('glucose')?.value", key="glucose"
    )

    # 保存ボタン
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
