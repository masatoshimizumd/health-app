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

# --- タイトル（下余白ゼロ） ---
st.markdown(
    "<h1 style='font-family:Arial,Helvetica,sans-serif;margin-bottom:0;'>Health_Data</h1>",
    unsafe_allow_html=True
)

# --- データ読み込み & カラム名正規化 ---
records = sheet.get_all_records()
df = pd.DataFrame(records)
if not df.empty:
    # カラム名を小文字に統一
    df.columns = [str(c).strip().lower() for c in df.columns]
    # 日付カラム名の推定（"date" が無ければ最初のカラムを仮に使う）
    date_col = "date" if "date" in df.columns else df.columns[0]
else:
    date_col = "date"

# --- CSS（余白削減・日付26px・保存ボタン下の余白ゼロ・フォーム直後の余白ゼロ） ---
st.markdown(
    """
    <style>
    .input-block{
        display:flex;flex-direction:column;margin-bottom:6px;
        font-family:Arial,Helvetica,sans-serif;
    }
    .input-block label{font-size:14px;margin-bottom:2px;}
    .input-block input{
        width:220px;font-size:20px;padding:6px;border-radius:6px;border:1px solid #ccc;
    }
    .date-block input{
        width:240px;font-size:26px;font-weight:bold;padding:6px;border-radius:6px;border:1px solid #333;
    }
    /* 保存ボタンの下余白ゼロ */
    div.stButton > button{margin-bottom:0 !important;}
    /* フォーム自体の下余白ゼロ（直後とのスキマをなくす）*/
    div[data-testid="stForm"]{margin-bottom:0 !important;padding-bottom:0 !important;}
    /* フォーム直後のブロック（見出しなど）の上余白ゼロ */
    div[data-testid="stForm"] + div {margin-top:0 !important;padding-top:0 !important;}
    div[data-testid="stForm"] + div h3 {margin-top:0 !important;padding-top:0 !important;line-height:1 !important;}
    </style>
    """,
    unsafe_allow_html=True
)

# --- 入力フォーム（HTMLのみ配置） ---
today_str = datetime.date.today().strftime("%Y-%m-%d")
with st.form("input_form"):
    st.markdown(
        f"""
        <div class="input-block date-block">
            <label>日付</label>
            <input type="date" id="date" value="{today_str}">
        </div>
        <div class="input-block">
            <label>収縮期血圧 (mmHg)</label>
            <input type="number" inputmode="numeric" id="systolic">
        </div>
        <div class="input-block">
            <label>拡張期血圧 (mmHg)</label>
            <input typ
