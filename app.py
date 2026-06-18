import streamlit as st
import requests
import pandas as pd

st.set_page_config(page_title="BPM Team Dashboard", layout="wide")

st.title("💼 BPM Team Dashboard (Notion 即時同步版)")
st.caption("後端 Python 直連，已完美對齊您的 Notion 實際欄位")

# 1. 安全密鑰
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
    return response = requests.post(url, headers=headers, json={})

# 💡 精準解讀你截圖中的 Notion 欄位格式
def parse_notion_to_dataframe(raw_data):
    results = raw_data.get("results", [])
    parsed_list = []
    
    for page in results:
        properties = page.get("properties", {})
        
        # 1. 任務名稱 (Title)
        title_obj = properties.get("任務名稱", {})
        title = title_obj["title"][0].get("plain_text", "") if title_obj.get("title") else ""
            
        # 2. 負責人 (Multi-select 或 People，先嘗試抓取名字列表)
        people_obj = properties.get("負責人", {})
        people = "-"
        if people_obj:
            if people_obj.get("people"):
                people = ", ".join([p.get("name", "") for p in people_obj["people"]])
            elif people_obj.get("multi_select"):
                people = ", ".join([p.get("name", "") for p in people_obj["multi_select"]])
                
        # 3. 優先順序 (Select)
        priority_obj = properties.get("優先順序", {})
        priority = priority_obj["select"].get("name", "-") if priority_obj.get("select") else "-"
            
        # 4. 狀態 (Status)
        status_obj = properties.get("狀態", {})
        status = "未開始"
        if status_obj:
            if status_obj.get("status"):
                status = status_obj["status"].get("name", "未開始")
            elif status_obj.get("select"):
                status = status_obj["select"].get("name", "未開始")

        # 5. 進度 (Formula 或 Number)
        progress_obj = properties.get("進度", {})
        progress = 0.0
        if progress_obj:
            if progress_obj.get("number") is not None:
                progress = float(progress_obj["number"])
            elif progress_obj.get("formula"):
                progress = float(progress_obj["formula"].get("number", 0))
        # 處理百分比顯示 (如果是像 100 代表 100%，除以 100 方便後續進度條計算)
        if progress > 1:
            progress = progress / 100.0

        # 6. 須優先決議 (Select / Status)
        decision_obj = properties.get("須優先決議", {})
        decision = "-"
        if decision_obj and decision_obj.get("select"):
            decision = decision_obj["select"].get("name", "-")
            
        parsed_list.append({
            "任務名稱": title,
            "負責人": people,
            "優先順序": priority,
            "狀態": status,
            "進度": progress,
            "須優先決議": decision
        })
        
    return pd.DataFrame(parsed_list)

# 4. 畫面渲染
if st.sidebar.button("🔄 立即同步最新資料"):
    with st.spinner(f"正在抓取【{project_choice}】並繪製圖表中..."):
        res = fetch_notion_data(NOTION_TOKEN, DATABASE_ID)
        
        if res.status_code == 200:
            raw_data = res.json()
            df = parse_notion_to_dataframe(raw_data)
            
            if not df.empty:
                st.success(f"✅ 【{project_choice}】數據渲染完成！")
                
                # 📊 第一層：數據小卡
                total_tasks = len(df)
                completed_tasks = len(df[df["狀態"].isin(["已完成", "Done"])])
                pending_decisions = len(df[df["須優先決議"].isin(["待決議", "是"])])
                
                # 計算整體平均進度
                avg_progress = df["進度"].mean() if "進度" in df else 0.0
                
                col1, col2, col3 = st.columns(3)
                col1.metric("總任務筆数", f"{total_tasks} 筆")
                col2.metric("專案整體總進度", f"{int(avg_progress * 100)}%")
                col3.metric("⚠️ 待決議事項", f"{pending_decisions} 筆", delta="- 需注意" if pending_decisions > 0 else "正常")
                
                st.markdown("---")
                
                # 📈 第二層：並排排版（左邊圓餅圖分佈、右邊待決議事項）
                left_col, right_col = st.columns([1, 1])
                
                with left_col:
                    st.subheader("📊 任務狀態分佈")
                    status_counts = df["狀態"].value_counts()
                    st.bar_chart(status_counts)
                    
                with right_col:
                    st.subheader("⚠️ 須優先決議清單")
                    urgent_df = df[df["須優先決議"].isin(["待決議", "是"])][["任務名稱", "負責人", "須優先決議"]]
                    if not urgent_df.empty:
                        st.dataframe(urgent_df, use_container_width=True, hide_index=True)
                    else:
                        st.success("目前沒有待決議事項，專案推進順利！")
                
                st.markdown("---")
                
                # 📋 第三層：詳細任務資料表（帶進度條）
                st.subheader("📋 專案工作總覽明細表")
                
                # 使用 Streamlit 內建強大的 column_config 功能，直接把小數點變成網頁進度條！
                st.data_editor(
                    df,
                    column_config={
                        "進度": st.column_config.ProgressColumn(
                            "目前進度",
                            help="從 Notion 同步過來的實際完成百分比",
                            format="%.0f%%",
                            min_value=0.0,
                            max_value=1.0,
                        ),
                    },
                    use_container_width=True,
                    disabled=True, # 唯讀模式
                    hide_index=True
                )
                
            else:
                st.warning("⚠️ 連線成功，但該資料庫內沒有撈到任何任務資料。")
        else:
            st.error(f"❌ Notion API 錯誤：{res.status_code}")
            st.json(res.json())
else:
    st.info(f"💡 目前就緒：【{project_choice}】。請點擊左側按鈕，立刻為您還原專案儀表板！")
