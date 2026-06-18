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
                            "優先順序": p.get("優先順序
