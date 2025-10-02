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

st.title("📊 健康データ記録アプリ（Google Sheets版）")

# --- データ読み込み ---
records = sheet.get_all_records()
df = pd.DataFrame(records)

# --- 新規追加フォーム ---
st.subheader("新しいデータを追加")

with st.form("input_form"):
    date = st.date_input("日付", value=datetime.date.today())

    # --- HTML埋め込みでiPhone電卓キーボードを出す ---
    html_code = """
    <script>
    function sendValues(){
        const data = {
            systolic: document.getElementById("systolic").value,
            diastolic: document.getElementById("diastolic").value,
            pulse: document.getElementById("pulse").value,
            weight: document.getElementById("weight").value,
            fat: document.getElementById("fat").value,
            glucose: document.getElementById("glucose").value
        }
        // Streamlitにデータを送る
        window.parent.postMessage({isStreamlitMessage: true, type: "streamlit:setComponentValue", value: data}, "*");
    }
    </script>

    <label>収縮期血圧 (mmHg)</label><input type="number" inputmode="numeric" id="systolic" style="width:100%;padding:5px;"><br>
    <label>拡張期血圧 (mmHg)</label><input type="number" inputmode="numeric" id="diastolic" style="width:100%;padding:5px;"><br>
    <label>脈拍 (bpm)</label><input type="number" inputmode="numeric" id="pulse" style="width:100%;padding:5px;"><br>
    <label>体重 (kg)</label><input type="number" inputmode="numeric" id="weight" style="width:100%;padding:5px;"><br>
    <label>体脂肪率 (%)</label><input type="number" inputmode="numeric" id="fat" style="width:100%;padding:5px;"><br>
    <label>血糖値 (mg/dL)</label><input type="number" inputmode="numeric" id="glucose" style="width:100%;padding:5px;"><br>
    <button type="button" onclick="sendValues()">入力値を送信</button>
    """

    # コンポーネント呼び出し
    values = components.html(html_code, height=400)

    submitted = st.form_submit_button("保存")

    if submitted:
        if values is None:
            st.error("⚠️ 先に『入力値を送信』ボタンを押してください。")
        else:
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
                    to_number(values.get("systolic", ""), int),
                    to_number(values.get("diastolic", ""), int),
                    to_number(values.get("pulse", ""), int),
                    to_number(values.get("weight", ""), float),
                    to_number(values.get("fat", ""), float),
                    to_number(values.get("glucose", ""), int),
                ]
                sheet.append_row(row)
                st.success("✅ Googleスプレッドシートに保存しました！")

# --- データ一覧の表示 ---
st.subheader("データ一覧")
st.dataframe(df)
