import streamlit as st
import requests
import pandas as pd
from datetime import date

# ── 頁面設定 ──────────────────────────────────────────
st.set_page_config(page_title="BPM Team Dashboard", layout="wide", page_icon="📋")

# ── Notion 設定 ───────────────────────────────────────
NOTION_TOKEN = st.secrets["NOTION_TOKEN"]  # 放在 .streamlit/secrets.toml
DBS = {
    "ALPT ALPSG BPM 導入專案": "38146c131ee380938377fc08df63428b",
    "ALPM BPM 優化專案":       "38146c131ee38099ae66cdae04e36c92",
    "BPM 多語系專案":           "38146c131ee3809ebe63db8f72fb615d",
    "Ad-Hoc Project":          "38246c131ee3803299c4f30c7d3960f3",
}
STC = {"未開始": "#b9bccd", "進行中": "#6aa6f5", "已完成": "#57c4a3"}

# ── 資料拉取 ──────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_all_tasks():
    headers = {
        "Authorization": f"Bearer {NOTION_TOKEN}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }
    tasks = []
    for proj_name, db_id in DBS.items():
        try:
            url = f"https://api.notion.com/v1/databases/{db_id}/query"
            res = requests.post(url, headers=headers, json={})
            res.raise_for_status()
            results = res.json().get("results", [])

            for page in results:
                p = page["properties"]

                def txt(key):
                    v = p.get(key, {})
                    t = v.get("type")
                    if t == "title":     return "".join(r["plain_text"] for r in v.get("title", []))
                    if t == "rich_text": return "".join(r["plain_text"] for r in v.get("rich_text", []))
                    if t == "select":    return (v.get("select") or {}).get("name", "")
                    if t == "status":    return (v.get("status") or {}).get("name", "")
                    if t == "date":      return (v.get("date") or {}).get("start")
                    if t == "number":    return v.get("number")
                    return ""

                task_name = txt("任務名稱") or txt("專案名稱")
                start_val = p.get("起始值", {}).get("number") or 0
                end_val   = p.get("結束值", {}).get("number") or 100
                status    = txt("狀態")
                progress  = 100 if status == "已完成" else (0 if status == "未開始" else round(start_val / end_val * 100) if end_val else 0)

                tasks.append({
                    "專案":   proj_name,
                    "任務":   task_name,
                    "負責人": txt("負責人"),
                    "優先":   txt("優先順序"),
                    "狀態":   status,
                    "開始":   txt("開始日期"),
                    "結束":   txt("結束日期"),
                    "進度":   progress,
                    "決議":   txt("須優先決議"),
                    "說明":   txt("決議事項說明"),
                })
        except Exception as e:
            st.warning(f"⚠️ {proj_name} 讀取失敗：{e}")
    return pd.DataFrame(tasks)

# ── 工具函式 ──────────────────────────────────────────
def days_late(end_str, status):
    try:
        if not end_str or status == "已完成":
            return 0
        delta = (date.today() - date.fromisoformat(str(end_str)[:10])).days
        return delta if delta > 0 else 0
    except Exception:
        return 0

def prio_color(p):
    return {"高": "🔴", "中": "🟡", "低": "🟢"}.get(p, "⚪")

def status_dot(s):
    colors = {"未開始": "⚪", "進行中": "🔵", "已完成": "🟢"}
    return f"{colors.get(s,'')} {s}"

# ── 主畫面 ────────────────────────────────────────────
st.markdown("## 📋 BPM Team Dashboard")
st.caption(f"資料來源：Notion BPM Team · 更新時間：{pd.Timestamp.now().strftime('%m/%d %H:%M')}")

col_refresh, _ = st.columns([1, 9])
with col_refresh:
    if st.button("🔄 更新資料"):
        st.cache_data.clear()
        st.rerun()

with st.spinner("從 Notion 載入資料中..."):
    df = fetch_all_tasks()

if df.empty:
    st.error("無法載入資料，請確認 Notion Token 和資料庫 ID 是否正確。")
    st.stop()

# ── KPI ───────────────────────────────────────────────
st.divider()
k1, k2, k3, k4 = st.columns(4)
total   = len(df)
in_prog = len(df[df["狀態"] == "進行中"])
done    = len(df[df["狀態"] == "已完成"])
dec     = len(df[df["決議"] == "待決議"])
df["落後天數"] = df.apply(lambda r: days_late(r["結束"], r["狀態"]), axis=1)
overdue = len(df[df["落後天數"] > 0])

k1.metric("📋 總任務", total)
k2.metric("⏳ 進行中", in_prog)
k3.metric("⚠️ 待決議", dec,  delta=f"{dec} 筆" if dec else None, delta_color="inverse")
k4.metric("🔴 落後任務", overdue, delta=f"{overdue} 筆" if overdue else None, delta_color="inverse")

# ── 狀態分佈長條圖 ────────────────────────────────────
st.divider()
c1, c2 = st.columns(2)

with c1:
    st.markdown("**完成率與狀態分佈**")
    status_counts = df["狀態"].value_counts().reset_index()
    status_counts.columns = ["狀態", "數量"]
    st.bar_chart(status_counts.set_index("狀態"), color="#6aa6f5")

with c2:
    st.markdown("**各專案任務數**")
    proj_counts = df["專案"].value_counts().reset_index()
    proj_counts.columns = ["專案", "數量"]
    st.bar_chart(proj_counts.set_index("專案"), color="#8b7ef0")

# ── 待決議 ────────────────────────────────────────────
st.divider()
st.markdown("### ⚠️ 須優先決議")
dec_df = df[df["決議"] == "待決議"][["專案", "任務", "負責人", "說明"]]
if dec_df.empty:
    st.success("目前沒有待決議事項")
else:
    st.dataframe(dec_df, use_container_width=True, hide_index=True)

# ── 落後任務 ──────────────────────────────────────────
st.markdown("### 🕐 進度異常（已逾結束日）")
ov_df = df[df["落後天數"] > 0][["專案", "任務", "負責人", "結束", "落後天數"]].sort_values("落後天數", ascending=False)
if ov_df.empty:
    st.success("目前沒有落後任務")
else:
    st.dataframe(ov_df, use_container_width=True, hide_index=True)

# ── 各專案明細 ────────────────────────────────────────
st.divider()
st.markdown("### 📁 專案進度總覽")
for proj in DBS.keys():
    proj_df = df[df["專案"] == proj]
    if proj_df.empty:
        continue
    done_n = len(proj_df[proj_df["狀態"] == "已完成"])
    prog_n = len(proj_df[proj_df["狀態"] == "進行中"])
    avg_prog = int(proj_df["進度"].mean())
    with st.expander(f"**{proj}**　｜　{len(proj_df)} 個任務　·　完成 {done_n}　·　進行中 {prog_n}　·　平均進度 {avg_prog}%"):
        display_df = proj_df[["任務", "負責人", "狀態", "進度", "結束", "優先", "決議"]].copy()
        display_df["狀態"] = display_df["狀態"].apply(status_dot)
        display_df["優先"] = display_df["優先"].apply(lambda p: f"{prio_color(p)} {p}")
        display_df["進度"] = display_df["進度"].apply(lambda v: f"{v}%")
        st.dataframe(display_df, use_container_width=True, hide_index=True)

# ── 看板 ──────────────────────────────────────────────
st.divider()
st.markdown("### 🗂️ 工作看板")
cols = st.columns(3)
for i, status in enumerate(["未開始", "進行中", "已完成"]):
    with cols[i]:
        items = df[df["狀態"] == status]
        st.markdown(f"**{status}** `{len(items)}`")
        for _, row in items.iterrows():
            with st.container(border=True):
                st.markdown(f"**{row['任務']}**")
                st.caption(f"{row['專案']}")
                if status == "進行中":
                    st.progress(int(row["進度"]) / 100)
                    st.caption(f"{prio_color(row['優先'])} {row['優先']}　{row['進度']}%")
