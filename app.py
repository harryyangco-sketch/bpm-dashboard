import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="BPM Team Dashboard", layout="wide")

st.title("💼 BPM Team Dashboard (Notion 即時同步版)")
st.caption("後端 Python 直連，已打通連線，為您即時渲染圖表")

# 1. 密鑰設定
DEFAULT_TOKEN = "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"

st.sidebar.header("🔑 Notion 連線設定")
project_choice = st.sidebar.selectbox(
    "📂 請選擇要同步的專案資料庫",
    ["BPM 多語系專案", "ALPM BPM 優化專案", "ALPT ALPSG BPM 導入專案", "Ad-Hoc Project"]
)

if project_choice == "BPM 多語系專案":
    DEFAULT_DB_ID = "38146c131ee3809ebe63db8f72fb615d"
elif project_choice == "ALPM BPM 優化專案":
    DEFAULT_DB_ID = "38146c131ee38099ae66cdae04e36c92"
elif project_choice == "ALPT ALPSG BPM 導入專案":
    DEFAULT_DB_ID = "38146c131ee380938377fc08df63428b"
else:
    DEFAULT_DB_ID = "38246c131ee3803299c4f30c7d3960f3"

NOTION_TOKEN = st.sidebar.text_input("Notion Secret Token", value=DEFAULT_TOKEN, type="password").strip()
DATABASE_ID = st.sidebar.text_input("Database ID", value=DEFAULT_DB_ID).strip()

def fetch_notion_data(token, db_id):
    url = f"https://api.notion.com/v1/databases/{db_id}/query"
    headers = {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json"
    }
    response = requests.post(url, headers=headers, json={})
    return response

# 💡 新增：將 Notion 繁複的 JSON 格式轉換為乾淨的 Pandas DataFrame 表格
def parse_notion_to_dataframe(raw_data):
    results = raw_data.get("results", [])
    parsed_list = []
    
    for page in results:
        properties = page.get("properties", {})
        
        # 1. 嘗試抓取任務名稱 (常見為 Name 或 標題)
        title_obj = properties.get("Name", properties.get("Task Name", properties.get("專案名稱", {})))
        title = ""
        if title_obj and title_obj.get("title"):
            title = title_obj["title"][0].get("plain_text", "")
            
        # 2. 嘗試抓取狀態 (常見為 Status 或 Select 類型的狀態)
        status_obj = properties.get("Status", properties.get("狀態", {}))
        status = "未開始"
        if status_obj:
            if status_obj.get("status"):
                status = status_obj["status"].get("name", "未開始")
            elif status_obj.get("select"):
                status = status_obj["select"].get("name", "未開始")
                
        # 3. 嘗試抓取優先順序
        priority_obj = properties.get("Priority", properties.get("優先順序", {}))
        priority = "-"
        if priority_obj and priority_obj.get("select"):
            priority = priority_obj["select"].get("name", "-")
            
        parsed_list.append({
            "任務/專案名稱": title,
            "目前狀態": status,
            "優先順序": priority
        })
        
    return pd.DataFrame(parsed_list)

# 4. 主要互動按鈕與圖表繪製
if st.sidebar.button("🔄 立即同步最新資料"):
    with st.spinner(f"正在抓取【{project_choice}】並繪製圖表中..."):
        res = fetch_notion_data(NOTION_TOKEN, DATABASE_ID)
        
        if res.status_code == 200:
            raw_data = res.json()
            df = parse_notion_to_dataframe(raw_data)
            
            if not df.empty:
                st.success(f"✅ 【{project_choice}】數據渲染完成！")
                
                # 📊 第一層：數據小卡 (Metrics)
                total_tasks = len(df)
                completed_tasks = len(df[df["目前狀態"].isin(["已完成", "Done", "Complete"])])
                in_progress_tasks = len(df[df["目前狀態"].isin(["進行中", "In Progress"])])
                
                col1, col2, col3 = st.columns(3)
                col1.metric("總任務/專案數", f"{total_tasks} 筆")
                col2.metric("進行中任務", f"{in_progress_tasks} 筆")
                col3.metric("已完成項目", f"{completed_tasks} 筆")
                
                st.markdown("---")
                
                # 📈 第二層：狀態分佈統計
                st.subheader("📊 各狀態任務數統計")
                status_counts = df["目前狀態"].value_counts()
                st.bar_chart(status_counts) # 自動畫出長條圖！
                
                st.markdown("---")
                
                # 📋 第三層：詳細任務資料表
                st.subheader("📋 任務清單明細表")
                st.dataframe(df, use_container_width=True) # 漂亮的互動式表格
                
            else:
                st.warning("⚠️ 成功連線，但該資料庫內目前沒有任何任務資料。")
                
            with st.expander("🔍 點此檢視原始 JSON 開發後台"):
                st.json(raw_data)
        else:
            st.error(f"❌ Notion API 錯誤：{res.status_code}")
            st.json(res.json())
else:
    st.info(f"💡 目前就緒：【{project_choice}】。請點擊左側按鈕，立刻為您畫出統計圖表！")
