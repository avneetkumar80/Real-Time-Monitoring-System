import streamlit as st
import psutil
import pandas as pd
from datetime import datetime
import time
from collections import deque

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


# ─── Session State ───
if "cpu_history" not in st.session_state:
    st.session_state.cpu_history = deque(maxlen=50)
if "memory_history" not in st.session_state:
    st.session_state.memory_history = deque(maxlen=50)
if "history_index" not in st.session_state:
    st.session_state.history_index = deque(maxlen=50)
if "cpu_threshold" not in st.session_state:
    st.session_state.cpu_threshold = 80
if "memory_threshold" not in st.session_state:
    st.session_state.memory_threshold = 85
if "last_alert_time" not in st.session_state:
    st.session_state.last_alert_time = 0.0
if "tick" not in st.session_state:
    st.session_state.tick = 0


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
st.session_state.tick += 1
st.session_state.history_index.append(st.session_state.tick)
st.session_state.cpu_history.append(cpu)
st.session_state.memory_history.append(memory.percent)

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
for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_info', 'username', 'status', 'create_time', 'nice']):
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
            'Priority': info['nice'] if info['nice'] is not None else "N/A",
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
        "Priority": st.column_config.TextColumn("Priority", width="small"),
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

# ─── Process Actions ───
st.markdown('<div class="section-header">⚙️ Process Controls</div>', unsafe_allow_html=True)

if not df.empty:
    process_options = {
        f"{row['Name']} (PID {row['PID']})": int(row["PID"])
        for _, row in df.iterrows()
    }
    selected_label = st.selectbox("Select a process", list(process_options.keys()))
    selected_pid = process_options[selected_label]
else:
    selected_pid = None
    st.info("No processes available for selection.")

action_col1, action_col2, action_col3, action_col4 = st.columns(4)

def run_process_action(action_name, fn):
    try:
        if selected_pid is None:
            st.warning("Select a process first.")
            return
        proc = psutil.Process(selected_pid)
        fn(proc)
        st.success(f"{action_name} succeeded for PID {selected_pid}.")
    except psutil.NoSuchProcess:
        st.error("That process no longer exists.")
    except psutil.AccessDenied:
        st.error("Access denied. Try running Streamlit as Administrator for this action.")
    except Exception as exc:
        st.error(f"{action_name} failed: {exc}")

with action_col1:
    if st.button("⚠️ Kill Process", use_container_width=True):
        run_process_action("Kill process", lambda proc: proc.terminate())

with action_col2:
    if st.button("↓ Lower Priority", use_container_width=True):
        def lower_priority(proc):
            if psutil.WINDOWS:
                proc.nice(psutil.BELOW_NORMAL_PRIORITY_CLASS)
            else:
                proc.nice(proc.nice() + 1)
        run_process_action("Lower priority", lower_priority)

with action_col3:
    if st.button("↑ Raise Priority", use_container_width=True):
        def raise_priority(proc):
            if psutil.WINDOWS:
                proc.nice(psutil.ABOVE_NORMAL_PRIORITY_CLASS)
            else:
                proc.nice(proc.nice() - 1)
        run_process_action("Raise priority", raise_priority)

with action_col4:
    csv_bytes = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇ Export Snapshot",
        data=csv_bytes,
        file_name=f"process_snapshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ─── Thresholds and Charts ───
left_col, right_col = st.columns([1, 2])

with left_col:
    st.markdown('<div class="section-header">🚨 Alert Thresholds</div>', unsafe_allow_html=True)
    st.session_state.cpu_threshold = st.slider("CPU threshold (%)", 1, 100, st.session_state.cpu_threshold)
    st.session_state.memory_threshold = st.slider("Memory threshold (%)", 1, 100, st.session_state.memory_threshold)

    now_ts = time.time()
    threshold_crossed = cpu >= st.session_state.cpu_threshold or memory.percent >= st.session_state.memory_threshold
    if threshold_crossed and now_ts - st.session_state.last_alert_time >= 45:
        reasons = []
        if cpu >= st.session_state.cpu_threshold:
            reasons.append(f"CPU {cpu:.1f}%")
        if memory.percent >= st.session_state.memory_threshold:
            reasons.append(f"Memory {memory.percent:.1f}%")
        st.warning("Threshold exceeded: " + " • ".join(reasons))
        st.session_state.last_alert_time = now_ts
    else:
        st.caption("Alerts use a 45-second cooldown to avoid noise.")

with right_col:
    st.markdown('<div class="section-header">📈 Resource Trends</div>', unsafe_allow_html=True)
    chart_df = pd.DataFrame(
        {
            "CPU Usage (%)": list(st.session_state.cpu_history),
            "Memory Usage (%)": list(st.session_state.memory_history),
        },
        index=list(st.session_state.history_index),
    )
    st.line_chart(chart_df, height=260)

# ─── Auto-refresh ───
st.markdown("<div style='height: 16px'></div>", unsafe_allow_html=True)
auto_refresh = st.checkbox("🔄 Auto-refresh (every 5 seconds)", value=False)

if auto_refresh:
    time.sleep(5)
    st.rerun()

# ─── Footer ───
st.markdown(f"""
<div class="footer">
    Built with ❤️ using Streamlit &nbsp;|&nbsp; System: {psutil.os.name.upper()} &nbsp;|&nbsp; Cores: {psutil.cpu_count(logical=True)}
</div>
""", unsafe_allow_html=True)
