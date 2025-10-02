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
            <input type="number" inputmode="numeric" id="diastolic">
        </div>
        <div class="input-block">
            <label>脈拍 (bpm)</label>
            <input type="number" inputmode="numeric" id="pulse">
        </div>
        <div class="input-block">
            <label>体重 (kg)</label>
            <input type="number" inputmode="numeric" id="weight">
        </div>
        <div class="input-block">
            <label>体脂肪率 (%)</label>
            <input type="number" inputmode="numeric" id="fat">
        </div>
        <div class="input-block">
            <label>血糖値 (mg/dL)</label>
            <input type="number" inputmode="numeric" id="glucose">
        </div>
        """,
        unsafe_allow_html=True,
    )
    submitted = st.form_submit_button("保存")

# --- フォーム外で値を取得（js_expressions= を必ず付ける） ---
date_val   = streamlit_js_eval(js_expressions="document.getElementById('date')?.value",     key="date")
systolic   = streamlit_js_eval(js_expressions="document.getElementById('systolic')?.value", key="systolic")
diastolic  = streamlit_js_eval(js_expressions="document.getElementById('diastolic')?.value",key="diastolic")
pulse      = streamlit_js_eval(js_expressions="document.getElementById('pulse')?.value",    key="pulse")
weight     = streamlit_js_eval(js_expressions="document.getElementById('weight')?.value",   key="weight")
fat        = streamlit_js_eval(js_expressions="document.getElementById('fat')?.value",      key="fat")
glucose    = streamlit_js_eval(js_expressions="document.getElementById('glucose')?.value",  key="glucose")

# --- 保存処理 ---
if submitted:
    # 重複チェック（dfが空の場合はスキップ）
    if (not df.empty) and (str(date_val) in df[date_col].astype(str).values):
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
            to_number(fat, float),
            to_number(glucose, int),
        ]
        sheet.append_row(row)
        st.success("✅ Googleスプレッドシートに保存しました！")
        # 再読み込み
        records = sheet.get_all_records()
        df = pd.DataFrame(records)
        if not df.empty:
            df.columns = [str(c).strip().lower() for c in df.columns]
            date_col = "date" if "date" in df.columns else df.columns[0]

# --- 直近データ（新しい順で上・保存ボタンとの余白ゼロ） ---
st.markdown("<h3 class='no-space'>📅 直近の記録（最新5件・新しい順）</h3>", unsafe_allow_html=True)

if not df.empty:
    # 日付をdatetimeにして降順、欠損は最後
    df_view = df.copy()
    # date_colが存在しない場合の保険
    if date_col not in df_view.columns:
        date_col = df_view.columns[0]
    df_view["_dt"] = pd.to_datetime(df_view[date_col].astype(str), errors="coerce")
    df_view = df_view.sort_values("_dt", ascending=False, na_position="last").drop(columns=["_dt"])
    st.dataframe(df_view.head(5))
else:
    st.info("まだ記録がありません。")
