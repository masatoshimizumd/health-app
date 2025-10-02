# --- 新規追加フォーム ---
st.subheader("新しいデータを追加")
with st.form("input_form"):
    date = st.date_input("日付", value=datetime.date.today())

    # 数字専用入力欄（iPhoneで電卓キーボードが出る）
    systolic = st.text_input("収縮期血圧 (mmHg)", value="", placeholder="数値を入力してください")
    diastolic = st.text_input("拡張期血圧 (mmHg)", value="", placeholder="数値を入力してください")
    pulse = st.text_input("脈拍 (bpm)", value="", placeholder="数値を入力してください")
    weight = st.text_input("体重 (kg)", value="", placeholder="数値を入力してください")
    fat = st.text_input("体脂肪率 (%)", value="", placeholder="数値を入力してください")
    glucose = st.text_input("血糖値 (mg/dL)", value="", placeholder="数値を入力してください")

    submitted = st.form_submit_button("保存")

    if submitted:
        # --- 入力チェック ---
        def to_number(x, cast_func):
            try:
                return cast_func(x)
            except:
                return None

        if not df.empty and str(date) in df["date"].astype(str).values:
            st.error("⚠️ この日付のデータは既に存在します。別の日付を選んでください。")
        else:
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
