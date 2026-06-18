import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="BPM Team Dashboard", layout="wide")

st.title("💼 BPM Team Dashboard (Notion 即時同步版)")
st.caption("後端 Python 直連，完全不受瀏覽器 CORS 限制")

# 1. 寫死你的安全密鑰，省去重複輸入的麻煩
DEFAULT_TOKEN = "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"

# 2. 側邊欄設定連線資訊
st.sidebar.header("🔑 Notion 連線設定")

# 下拉選單：直接對應你真實的專案名稱
project_choice = st.sidebar.selectbox(
    "📂 請選擇要同步的專案資料庫",
    [
        "BPM 多語系專案",
        "ALPM BPM 優化專案",
        "ALPT ALPSG BPM 導入專案",
        "Ad-Hoc Project"
    ]
)

# 根據你的選擇，自動切換過濾後的純淨 32 位元 Database ID
if project_choice == "BPM 多語系專案":
    DEFAULT_DB_ID = "38146c131ee3809ebe63db8f72fb615d"
elif project_choice == "ALPM BPM 優化專案":
    DEFAULT_DB_ID = "38146c131ee38099ae66cdae04e36c92"
elif project_choice == "ALPT ALPSG BPM 導入專案":
    DEFAULT_DB_ID = "38146c131ee380938377fc08df63428b"
else:
    DEFAULT_DB_ID = "38246c131ee3803299c4f30c7d3960f3"

# 顯示輸入框（已自動帶入對應的預設值，你也可以手動覆蓋）
NOTION_TOKEN = st.sidebar.text_input("Notion Secret Token", value=DEFAULT_TOKEN, type="password").strip()
DATABASE_ID = st.sidebar.text_input("Database ID", value=DEFAULT_DB_ID).strip()

# 3. 定義抓取資料的函式
def fetch_notion_data(token, db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    # 發送空白 Body 代表撈取該資料庫全部的 Pages
    response = requests.post(url, headers=headers, json={})
    return response

# 4. 主要互動按鈕
if st.sidebar.button("🔄 立即同步最新資料"):
    with st.spinner(f"正在穿透後端抓取【{project_choice}】的資料中..."):
        res = fetch_notion_data(NOTION_TOKEN, DATABASE_ID)
        
        if res.status_code == 200:
            st.success(f"✅ 【{project_choice}】資料同步成功！")
            raw_data = res.json()
            
            results = raw_data.get("results", [])
            st.metric(label="目前成功撈回任務筆數", value=f"{len(results)} 筆")
            
            # 展開原始 JSON 結構供你確認資料格式
            with st.expander("🔍 檢視從 Notion 撈回來的原始資料 (JSON)"):
                st.json(raw_data)
        else:
            st.error(f"❌ Notion API 回傳錯誤，狀態碼：{res.status_code}")
            st.json(res.json())
else:
    st.info(f"💡 目前就緒：【{project_choice}】。請點擊左側「立即同步最新資料」開始抓取。")
