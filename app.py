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

    # CSS（ゴシック系フォント＆入力欄を少し大きく）
    css_style = """
    <style>
    input[type=number] {
        font-family: Arial, Helvetica, sans-serif;
        width: 160px;
        font-size: 18px;
        padding: 6px;
        margin-bottom: 10px;
    }
    label {
        font-family: Arial, Helvetica, sans-serif;
        font-size: 15px;
    }
    </style>
    """
    st.markdown(css_style, unsafe_allow_html=True)

    # --- HTML埋め込みで電卓キーボードを確実に出す ---
    def number_input_html(label, name):
        return components.html(
            f"""
            <label>{label}</label><br>
            <input type="number" inputmode="numeric" id="{name}" name="{name}" style="width:160px;"><br>
            """,
            height=60
        )

    systolic = number_input_html("収縮期血圧 (mmHg)", "systolic")
    diastolic = number_input_html("拡張期血圧 (mmHg)", "diastolic")
    pulse = number_input_html("脈拍 (bpm)", "pulse")
    weight = number_input_html("体重 (kg)", "weight")
    fat = number_input_html("体脂肪率 (%)", "fat")
    glucose = number_input_html("血糖値 (mg/dL)", "glucose")

    submitted = st.form_submit_button("保存")

    if submitted:
        # ここで本来は JS から値をセッションに渡す仕組みが必要
        # （streamlit-js-eval を使えば可能）
        st.warning("⚠️ 現状は電卓キーボードは出ますが、保存するには JS → Streamlit への値バインディングを追加する必要があります。")
