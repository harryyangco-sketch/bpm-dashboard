from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components

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
      iframe {display: block;}
    </style>
    """,
    unsafe_allow_html=True,
)

# 關鍵：HTML/CSS/JS 全部放在 dashboard.html，不寫進 Python 檔
# （直接把 CSS 貼進 .py 就會出現 "invalid decimal literal"）
HTML_PATH = Path(__file__).parent / "dashboard.html"

if not HTML_PATH.exists():
    st.error(f"找不到 {HTML_PATH.name}，請確認它和 app.py 放在 repo 同一層。")
    st.stop()

html = HTML_PATH.read_text(encoding="utf-8")

# dashboard 內含 <script>，必須用 components.html（st.markdown 不會執行 JS）
components.html(html, height=3200, scrolling=True)
