import streamlit as st
from notion_client import Client
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="BPM Team Dashboard", layout="wide", page_icon="📊")

st.title("📊 BPM Team Dashboard")
st.caption("資料來源：Notion · BPM Team teamspace")

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]

DB_CONFIG = [
    {"proj": "ALPT ALPSG BPM 導入專案", "id": "38146c131ee380938377fc08df63428b"},
    {"proj": "ALPM BPM 優化專案", "id": "38146c131ee38099ae66cdae04e36c92"},
    {"proj": "BPM 多語系專案", "id": "38146c131ee3809ebe63db8f72fb615d"},
    {"proj": "Ad-Hoc Project", "id": "38246c131ee3803299c4f30c7d3960f3"},   # 已修正
]

if st.button("🔄 更新最新資料", type="primary", use_container_width=True):
    with st.spinner("正在從 Notion 抓取最新資料..."):
        try:
            notion = Client(auth=NOTION_TOKEN)
            all_tasks = []
            errors = []

            for db in DB_CONFIG:
                try:
                    resp = notion.databases.query(database_id=db["id"], page_size=100)
                    count = len(resp.get("results", []))
                    st.info(f"✅ {db['proj']}：抓到 {count} 筆資料")
                    
                    for page in resp.get("results", []):
                        p = page.get("properties", {})
                        task = {
                            "專案": db["proj"],
                            "任務": p.get("任務名稱", {}).get("title", [{}])[0].get("plain_text", "無名稱"),
                            "負責人": p.get("負責人", {}).get("people", [{}])[0].get("name", "") if p.get("負責人", {}).get("people") else "",
                            "優先順序": p.get("優先順序", {}).get("select", {}).get("name", "中"),
                            "狀態": p.get("狀態", {}).get("status", {}).get("name") or p.get("狀態", {}).get("select", {}).get("name", "未開始"),
                            "開始日期": p.get("開始日期", {}).get("date", {}).get("start"),
                            "結束日期": p.get("結束日期", {}).get("date", {}).get("start"),
                            "進度": p.get("進度", {}).get("formula", {}).get("number") or 0,
                            "須優先決議": p.get("須優先決議", {}).get("select", {}).get("name", "否"),
                            "決議說明": p.get("決議事項說明", {}).get("rich_text", [{}])[0].get("plain_text", "")
                        }
                        all_tasks.append(task)
                except Exception as e:
                    errors.append(db["proj"])

            st.session_state.tasks = all_tasks
            st.session_state.last_update = datetime.now().strftime("%Y/%m/%d %H:%M")
            st.success(f"✅ 總共抓到 {len(all_tasks)} 筆任務！")
            
            if errors:
                st.warning("部分專案失敗：" + ", ".join(errors))
                
        except Exception as e:
            st.error(f"連線錯誤：{str(e)}")

if "tasks" not in st.session_state:
    st.info("👆 請點擊上方「更新最新資料」按鈕開始載入")
    st.stop()

df = pd.DataFrame(st.session_state.tasks)
st.dataframe(df, use_container_width=True, hide_index=True)

if "last_update" in st.session_state:
    st.caption(f"最後更新：{st.session_state.last_update}")
