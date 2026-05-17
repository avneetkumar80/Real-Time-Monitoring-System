import streamlit as st
import psutil
import pandas as pd
from datetime import datetime

# ─── Page Config ───
st.set_page_config(
    page_title="Real-Time Process Monitoring",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─── Custom CSS for premium look ───
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Global */
    .stApp {
        background: linear-gradient(135deg, #0A0E27 0%, #1A1F3A 100%);
        font-family: 'Inter', sans-serif;
    }

    /* Header */
    .dashboard-header {
        background: linear-gradient(135deg, #1E3A8A, #3B82F6);
        border-radius: 16px;
        padding: 28px 36px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        box-shadow: 0 8px 32px rgba(59, 130, 246, 0.25);
    }
    .dashboard-header h1 {
        color: #F0F4F8;
        font-size: 28px;
        font-weight: 700;
        margin: 0;
    }
    .dashboard-header p {
        color: #93C5FD;
        font-size: 14px;
        margin: 4px 0 0 0;
    }

    /* Metric Cards */
    .metric-card {
        background: rgba(30, 39, 66, 0.85);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .metric-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    .metric-icon {
        font-size: 32px;
        margin-bottom: 8px;
    }
    .metric-label {
        color: #A0B4C8;
        font-size: 13px;
        font-weight: 500;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 36px;
        font-weight: 700;
        margin: 4px 0;
    }
    .metric-bar-bg {
        background: rgba(255,255,255,0.08);
        border-radius: 6px;
        height: 8px;
        margin-top: 12px;
        overflow: hidden;
    }
    .metric-bar {
        height: 100%;
        border-radius: 6px;
        transition: width 0.5s ease;
    }
    .color-green { color: #2ED573; }
    .color-blue { color: #5352ED; }
    .color-orange { color: #FFA502; }
    .color-red { color: #FF4757; }
    .bar-green { background: linear-gradient(90deg, #2ED573, #7BED9F); }
    .bar-blue { background: linear-gradient(90deg, #5352ED, #70A1FF); }
    .bar-orange { background: linear-gradient(90deg, #FFA502, #ECCC68); }
    .bar-red { background: linear-gradient(90deg, #FF4757, #FF6B81); }

    /* Section headers */
    .section-header {
        color: #F0F4F8;
        font-size: 20px;
        font-weight: 600;
        margin: 28px 0 16px 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    /* Table styling */
    .stDataFrame {
        border-radius: 12px;
        overflow: hidden;
    }
    div[data-testid="stDataFrame"] > div {
        border-radius: 12px;
        border: 1px solid rgba(255,255,255,0.06);
    }

    /* Footer */
    .footer {
        text-align: center;
        color: #64748B;
        font-size: 12px;
        padding: 20px 0 10px 0;
        border-top: 1px solid rgba(255,255,255,0.06);
        margin-top: 32px;
    }

    /* Hide default Streamlit elements for cleaner look */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1A1F3A;
    }
</style>
""", unsafe_allow_html=True)


# ─── Helper: color based on value ───
def get_color_class(value):
    if value < 40:
        return "green"
    elif value < 70:
        return "orange"
    else:
        return "red"


# ─── System Metrics ───
cpu = psutil.cpu_percent(interval=0.5)
memory = psutil.virtual_memory()
disk = psutil.disk_usage('/')
net = psutil.net_io_counters()
boot_time = datetime.fromtimestamp(psutil.boot_time())
uptime = datetime.now() - boot_time

# ─── Header ───
st.markdown(f"""
<div class="dashboard-header">
    <div>
        <h1>⚡ Real-Time Process Monitoring</h1>
        <p>System uptime: {str(uptime).split('.')[0]} &nbsp;|&nbsp; Last refreshed: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── Metric Cards ───
col1, col2, col3, col4 = st.columns(4)

metrics = [
    (col1, "🔥", "CPU Usage", cpu, "%"),
    (col2, "💾", "Memory", memory.percent, f"% — {memory.used // (1024**3)}/{memory.total // (1024**3)} GB"),
    (col3, "💿", "Disk", disk.percent, f"% — {disk.used // (1024**3)}/{disk.total // (1024**3)} GB"),
    (col4, "🌐", "Network ↑↓", 0, f"{net.bytes_sent // (1024**2)} / {net.bytes_recv // (1024**2)} MB"),
]

for col, icon, label, value, suffix in metrics:
    color = get_color_class(value) if value > 0 else "blue"
    with col:
        if label == "Network ↑↓":
            display_val = f"{net.bytes_sent // (1024**2)}/{net.bytes_recv // (1024**2)}"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value color-{color}">{display_val}</div>
                <div style="color: #A0B4C8; font-size: 12px;">MB sent / received</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-icon">{icon}</div>
                <div class="metric-label">{label}</div>
                <div class="metric-value color-{color}">{value:.1f}%</div>
                <div class="metric-bar-bg">
                    <div class="metric-bar bar-{color}" style="width: {value}%;"></div>
                </div>
                <div style="color: #64748B; font-size: 11px; margin-top: 6px;">{suffix}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='height: 8px'></div>", unsafe_allow_html=True)

# ─── Process Table ───
st.markdown('<div class="section-header">📋 Running Processes</div>', unsafe_allow_html=True)

# Filter controls
filter_col1, filter_col2, filter_col3 = st.columns([3, 1, 1])
with filter_col1:
    search = st.text_input("🔍 Filter by process name", placeholder="Type to search...", label_visibility="collapsed")
with filter_col2:
    sort_by = st.selectbox("Sort by", ["cpu_percent", "memory_mb", "pid", "name"], label_visibility="collapsed")
with filter_col3:
    sort_order = st.selectbox("Order", ["Descending", "Ascending"], label_visibility="collapsed")

# Gather process data
process_data = []
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username', 'status', 'create_time']):
    try:
        info = proc.info
        mem_mb = info['memory_info'].rss / (1024 * 1024) if info['memory_info'] else 0.0
        try:
            created = datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M') if info['create_time'] else "N/A"
        except (OSError, ValueError):
            created = "N/A"
        process_data.append({
            'PID': info['pid'],
            'Name': info['name'] or "N/A",
            'User': info['username'] or "N/A",
            'CPU %': round(info['cpu_percent'] or 0, 1),
            'Memory (MB)': round(mem_mb, 1),
            'Status': info['status'] or "N/A",
            'Created': created,
        })
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        continue

df = pd.DataFrame(process_data)

# Apply filter
if search:
    df = df[df['Name'].str.contains(search, case=False, na=False)]

# Apply sort
sort_col_map = {
    "cpu_percent": "CPU %",
    "memory_mb": "Memory (MB)",
    "pid": "PID",
    "name": "Name",
}
ascending = sort_order == "Ascending"
df = df.sort_values(by=sort_col_map[sort_by], ascending=ascending).reset_index(drop=True)

# Display
st.dataframe(
    df,
    use_container_width=True,
    height=460,
    column_config={
        "PID": st.column_config.NumberColumn("PID", width="small"),
        "Name": st.column_config.TextColumn("Name", width="medium"),
        "User": st.column_config.TextColumn("User", width="medium"),
        "CPU %": st.column_config.ProgressColumn("CPU %", min_value=0, max_value=100, format="%.1f%%"),
        "Memory (MB)": st.column_config.NumberColumn("Memory (MB)", format="%.1f"),
        "Status": st.column_config.TextColumn("Status", width="small"),
        "Created": st.column_config.TextColumn("Created", width="medium"),
    },
)

# Summary bar
st.markdown(f"""
<div style="display: flex; gap: 24px; color: #A0B4C8; font-size: 13px; margin-top: 4px;">
    <span>📊 Total processes: <strong style="color: #F0F4F8;">{len(process_data)}</strong></span>
    <span>🔥 High CPU (>50%): <strong style="color: #FF4757;">{len([p for p in process_data if p['CPU %'] > 50])}</strong></span>
    <span>💾 High Memory (>500MB): <strong style="color: #FFA502;">{len([p for p in process_data if p['Memory (MB)'] > 500])}</strong></span>
</div>
""", unsafe_allow_html=True)

# ─── Auto-refresh ───
st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
auto_refresh = st.checkbox("🔄 Auto-refresh (every 5 seconds)", value=False)

if auto_refresh:
    import time as _time
    _time.sleep(5)
    st.rerun()

# ─── Footer ───
st.markdown(f"""
<div class="footer">
    Built with ❤️ using Streamlit &nbsp;|&nbsp; System: {psutil.os.name.upper()} &nbsp;|&nbsp; Cores: {psutil.cpu_count(logical=True)}
</div>
""", unsafe_allow_html=True)
