from pathlib import Path
from datetime import date, datetime
import json

import streamlit as st
import streamlit.components.v1 as components
import requests

st.set_page_config(
    page_title="BPM Team Project Management Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# 隱藏 Streamlit 預設的 header/footer，讓 dashboard 滿版呈現
st.markdown(
    """
    <style>
      #MainMenu, header, footer {visibility: hidden;}
      .block-container {padding: 0 !important; max-width: 100% !important;}
      iframe {display: block; width: 100%; border: none;}
    </style>
    """,
    unsafe_allow_html=True,
)

NOTION_TOKEN = st.secrets["NOTION_TOKEN"]
NOTION_HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}

# ── 按下畫面上的「更新資料」按鈕時，網址會帶上 ?refresh=時間戳 ──
# 偵測到這個參數就清空快取，確保這次一定重新打 Notion API，不會被
# 下面 5 分鐘的 cache 擋下、回傳舊資料。
if "refresh" in st.query_params:
    st.cache_data.clear()


@st.cache_data(ttl=300)
def fetch_db_list():
    """自動探索所有已分享給這個 Notion Integration 的資料庫。"""
    dbs = {}
    has_more = True
    cursor = None
    while has_more:
        body = {"filter": {"value": "database", "property": "object"}, "page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        res = requests.post("https://api.notion.com/v1/search", headers=NOTION_HEADERS, json=body)
        res.raise_for_status()
        data = res.json()
        for db in data.get("results", []):
            title = "".join(t["plain_text"] for t in db.get("title", []))
            if title:
                dbs[title] = db["id"].replace("-", "")
        has_more = data.get("has_more", False)
        cursor = data.get("next_cursor")
    return dbs


@st.cache_data(ttl=300)
def fetch_all_tasks():
    dbs = fetch_db_list()
    tasks = []
    errors = []

    for proj_name, db_id in dbs.items():
        try:
            url = f"https://api.notion.com/v1/databases/{db_id}/query"
            res = requests.post(url, headers=NOTION_HEADERS, json={})
            res.raise_for_status()
            results = res.json().get("results", [])
            if not results:
                continue

            for page in results:
                p = page["properties"]

                def txt(key):
                    v = p.get(key, {})
                    t = v.get("type")
                    if t == "title":
                        return "".join(r["plain_text"] for r in v.get("title", []))
                    if t == "rich_text":
                        return "".join(r["plain_text"] for r in v.get("rich_text", []))
                    if t == "select":
                        return (v.get("select") or {}).get("name", "")
                    if t == "status":
                        return (v.get("status") or {}).get("name", "")
                    if t == "date":
                        return (v.get("date") or {}).get("start")
                    if t == "number":
                        return v.get("number")
                    return ""

                task_name = txt("任務名稱") or txt("專案名稱")
                if not task_name:
                    # 這個資料庫看起來不是任務清單（沒有對應欄位），略過整個資料庫
                    break

                start_val = p.get("起始值", {}).get("number") or 0
                end_val = p.get("結束值", {}).get("number") or 100
                status = txt("狀態")
                progress = (
                    100 if status == "已完成"
                    else (0 if status == "未開始" else round(start_val / end_val * 100) if end_val else 0)
                )
                tasks.append({
                    "proj": proj_name,
                    "task": task_name,
                    "owner": txt("負責人"),
                    "prio": txt("優先順序"),
                    "status": status or "未開始",
                    "start": txt("開始日期"),
                    "end": txt("結束日期"),
                    "progress": progress,
                    "decide": txt("須優先決議") or "否",
                    "note": txt("決議事項說明"),
                    "prog_note": txt("進度說明"),  # 選填欄位，若資料庫沒有此欄位則自動回傳空字串
                    "actual_end": None,
                })
        except Exception as e:
            errors.append(f"{proj_name}: {e}")

    return tasks, errors


with st.spinner("從 Notion 載入資料中..."):
    tasks, errors = fetch_all_tasks()

for e in errors:
    st.warning(f"⚠️ {e}")

if not tasks:
    st.error("無法載入任何任務資料，請確認 Notion Token 是否正確、資料庫是否已分享給 Integration。")
    st.stop()

today_str = date.today().isoformat()
tasks_json = json.dumps(tasks, ensure_ascii=False)
# 防護：若 Notion 欄位內容剛好包含 "</script>"，未跳脫會提前關閉整段 <script>，
# 導致頁面壞掉甚至有 XSS 風險，因此把 "</" 轉成 JS 可安全解析的 "<\/"。
tasks_json = tasks_json.replace("</", "<\\/")

HTML_PATH = Path(__file__).parent / "dashboard.html"
if not HTML_PATH.exists():
    st.error(f"找不到 {HTML_PATH.name}，請確認它和 app.py 放在 repo 同一層。")
    st.stop()

html = HTML_PATH.read_text(encoding="utf-8")
html = html.replace("__SNAPSHOT_DATE__", today_str)
html = html.replace("__TASKS_JSON__", tasks_json)

# scrolling=False + dashboard.html 內建的自動調整高度腳本，
# 讓 iframe 高度跟著內容撐開，只留瀏覽器外層一條滑軌（不會有內外兩條）。
components.html(html, height=600, scrolling=False)
