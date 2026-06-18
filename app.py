import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="BPM Team Dashboard", layout="wide")

st.title("💼 BPM Team Dashboard (Notion 即時同步版)")
st.caption("後端 Python 直連，完全不受瀏覽器 CORS 限制")

# 1. 側邊欄設定連線資訊
st.sidebar.header("🔑 Notion 連線設定")
NOTION_TOKEN = st.sidebar.text_input("Notion Secret Token", type="password", placeholder="secret_...")
DATABASE_ID = st.sidebar.text_input("Database ID", placeholder="請輸入 32 位元的資料庫 ID")

# 2. 定義抓取資料的函式
def fetch_notion_data(token, db_id):
    # 注意：Notion 官方標準 API 端點是 v1，不是 v2
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28", # 官方推薦的穩定版本
        "Content-Type": "application/json"
    }
    
    response = requests.post(url, headers=headers)
    return response

# 3. 主要互動按鈕
if st.sidebar.button("🔄 立即同步最新資料"):
    if not NOTION_TOKEN or not DATABASE_ID:
        st.error("❌ 請填寫完整的 Token 與 Database ID！")
    else:
        with st.spinner("正在穿透後端抓取 Notion 資料中..."):
            res = fetch_notion_data(NOTION_TOKEN, DATABASE_ID)
            
            if res.status_code == 200:
                st.success("✅ 資料同步成功！")
                raw_data = res.json()
                
                # 簡單解析範例（你可以根據你的 Notion 欄位再調整）
                results = raw_data.get("results", [])
                st.write(f"目前成功撈回 {len(results)} 筆任務資料！")
                
                # 顯示原始 JSON 結構供你確認
                with st.expander("🔍 檢視從 Notion 撈回來的原始資料 (JSON)"):
                    st.json(raw_data)
            else:
                st.error(f"❌ Notion API 回傳錯誤，狀態碼：{res.status_code}")
                st.json(res.json())
else:
    st.info("💡 請在左側輸入您的 Notion 連線資訊，並點擊「立即同步最新資料」按鈕。")
