from __future__ import annotations

from io import StringIO

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from core import ALGORITHMS, compare_algorithms, parse_reference_string, simulate_page_replacement

st.set_page_config(
    page_title="Page Replacement Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# A dark, high-contrast visual system that works well on a projector.
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --bg:#080f1d; --panel:#111c30; --line:rgba(151,180,222,.16); --text:#edf4ff; --muted:#9aacc9; --teal:#5be7c4; --blue:#7aa8ff; --red:#ff718b; }
    html, body, [class*="css"] { font-family:'Manrope',sans-serif; }
    .stApp { background:radial-gradient(ellipse at 86% 0%,rgba(35,93,146,.25),transparent 35%),var(--bg); color:var(--text); }
    [data-testid="stSidebar"] { background:linear-gradient(180deg,#101b2e,#0a1120); border-right:1px solid var(--line); }
    [data-testid="stSidebar"] * { color:var(--text); }
    [data-testid="stHeader"] { background:rgba(8,15,29,.72); }
    h1,h2,h3 { letter-spacing:-.04em; }
    .eyebrow { color:var(--teal); font-family:'DM Mono',monospace; font-size:.72rem; font-weight:500; letter-spacing:.17em; text-transform:uppercase; }
    .hero { border:1px solid rgba(122,168,255,.28); border-radius:24px; padding:1.65rem 1.8rem; margin:.15rem 0 1.1rem; background:linear-gradient(112deg,rgba(25,48,82,.96),rgba(17,28,48,.95) 58%,rgba(17,69,73,.58)); position:relative; overflow:hidden; }
    .hero h1 { font-size:2.55rem; line-height:1.12; margin:.3rem 0 .55rem; font-weight:800; }
    .hero p { color:#c4d3e9; max-width:800px; margin:0; font-size:1rem; }
    .grad { background:linear-gradient(90deg,#5be7c4,#7aa8ff); -webkit-background-clip:text; background-clip:text; color:transparent; }
    .tag { display:inline-block; margin:.9rem .35rem 0 0; padding:.25rem .62rem; border-radius:100px; border:1px solid rgba(91,231,196,.26); background:rgba(91,231,196,.08); color:#9af3df; font-size:.72rem; font-family:'DM Mono',monospace; }
    .metric-card { padding:1rem 1.05rem; border:1px solid var(--line); border-radius:16px; background:linear-gradient(145deg,rgba(19,31,53,.96),rgba(13,23,40,.96)); min-height:118px; }
    .metric-label { font-size:.72rem; text-transform:uppercase; color:var(--muted); letter-spacing:.08em; font-family:'DM Mono',monospace; }
    .metric-value { color:#f3f7ff; font-weight:800; font-size:1.8rem; line-height:1.35; }
    .metric-note { color:#9aacc9; font-size:.78rem; }
    .panel { border:1px solid var(--line); border-radius:17px; padding:1rem 1.1rem; background:linear-gradient(145deg,rgba(18,30,50,.95),rgba(12,21,37,.95)); }
    .frame { border:1px solid rgba(91,231,196,.32); border-radius:13px; padding:1rem .25rem; text-align:center; background:linear-gradient(160deg,rgba(28,76,83,.54),rgba(17,35,53,.9)); }
    .frame-empty { border:1px dashed rgba(151,180,222,.28); border-radius:13px; padding:1rem .25rem; text-align:center; color:#7586a5; background:rgba(16,26,44,.5); }
    .frame-value { font-family:'DM Mono',monospace; font-size:1.75rem; color:#82f1db; font-weight:500; }
    .frame-label { font-size:.68rem; text-transform:uppercase; letter-spacing:.1em; color:#a4bad7; }
    .good { color:#75efce; font-weight:800; }
    .bad { color:#ff8fa2; font-weight:800; }
    .muted { color:var(--muted); font-size:.88rem; }
    .stButton button, .stDownloadButton button { border-radius:11px; border:1px solid rgba(91,231,196,.34); background:linear-gradient(90deg,rgba(91,231,196,.14),rgba(122,168,255,.14)); color:#effffc; font-weight:700; }
    .stButton button:hover, .stDownloadButton button:hover { border-color:var(--teal); color:white; }
    .stTextInput input, .stTextArea textarea, .stNumberInput input { background:#0d1728; color:#f1f6ff; border-color:var(--line); border-radius:10px; }
    div[data-baseweb="select"] > div { background:#0d1728; border-color:var(--line); border-radius:10px; }
    div[data-testid="stMetric"] { background:#111c30; border:1px solid var(--line); border-radius:14px; padding:.65rem .8rem; }
    div[data-testid="stMetricLabel"] { color:var(--muted); }
    div[data-testid="stMetricValue"] { color:#f2f7ff; }
    hr { border-color:var(--line); }
    </style>
    """,
    unsafe_allow_html=True,
)

# ------------------------------ Sidebar ------------------------------------
with st.sidebar:
    st.markdown("<div style='font-size:1.6rem;font-weight:800;letter-spacing:-.05em'>PAGE<span style='color:#5be7c4'>VAULT</span></div><div class='eyebrow'>PAGE REPLACEMENT LAB</div>", unsafe_allow_html=True)
    st.markdown("---")
    view = st.radio("LAB NAVIGATION", ["Command Center", "Step-by-step Simulator", "Algorithm Comparison", "Theory & Viva"], label_visibility="visible")
    st.markdown("---")
    st.markdown("<div class='eyebrow'>SIMULATION INPUTS</div>", unsafe_allow_html=True)
    raw_sequence = st.text_area("Page reference string", "7 0 1 2 0 3 0 4 2 3 0 3 2", height=96, help="Separate page IDs using spaces, commas, or new lines.")
    frame_count = st.slider("Number of memory frames", min_value=1, max_value=8, value=3)
    selected_algorithm = st.selectbox("Active algorithm", ALGORITHMS, index=0)
    st.caption("Educational simulation only — it does not change your computer's real RAM.")

try:
    pages = parse_reference_string(raw_sequence)
    selected_result = simulate_page_replacement(pages, frame_count, selected_algorithm)
    all_results = compare_algorithms(pages, frame_count)
except (TypeError, ValueError) as exc:
    st.error(str(exc))
    st.stop()

comparison_df = pd.DataFrame([
    {"Algorithm": item["algorithm"], "Page Faults": item["faults"], "Page Hits": item["hits"], "Hit Rate (%)": round(item["hit_rate"], 1), "Fault Rate (%)": round(item["fault_rate"], 1)}
    for item in all_results
])


def metric_card(label: str, value: str, note: str) -> None:
    st.markdown(f"<div class='metric-card'><div class='metric-label'>{label}</div><div class='metric-value'>{value}</div><div class='metric-note'>{note}</div></div>", unsafe_allow_html=True)


def chart_layout(fig: go.Figure, height: int = 330) -> go.Figure:
    fig.update_layout(
        height=height,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font={"family": "Manrope, sans-serif", "color": "#dce8fa"},
        margin={"l": 12, "r": 12, "t": 35, "b": 12},
        legend={"orientation": "h", "y": 1.13, "x": 0},
    )
    fig.update_xaxes(gridcolor="rgba(151,180,222,.10)", zerolinecolor="rgba(151,180,222,.10)")
    fig.update_yaxes(gridcolor="rgba(151,180,222,.10)", zerolinecolor="rgba(151,180,222,.10)")
    return fig


def show_hero(title: str, subtitle: str, badge: str) -> None:
    st.markdown(f"<div class='hero'><div class='eyebrow'>{badge}</div><h1>{title}</h1><p>{subtitle}</p><span class='tag'>FIFO</span><span class='tag'>LRU</span><span class='tag'>OPTIMAL</span><span class='tag'>PYTHON + STREAMLIT</span></div>", unsafe_allow_html=True)

# ------------------------------ Views --------------------------------------
if view == "Command Center":
    show_hero("Page Replacement <span class='grad'>Lab.</span>", "A visual Operating Systems simulator. Watch memory frames update, compare replacement policies, and understand why page faults happen.", "OPERATING SYSTEMS · MINI PROJECT · TOPIC 05")

    a, b, c, d = st.columns(4, gap="medium")
    with a: metric_card("Active policy", selected_algorithm, "Current simulation")
    with b: metric_card("Page faults", str(selected_result["faults"]), "A requested page was not resident")
    with c: metric_card("Page hits", str(selected_result["hits"]), "Requested page already in RAM")
    with d: metric_card("Hit rate", f"{selected_result['hit_rate']:.1f}%", f"{selected_result['reference_count']} total requests")

    left, right = st.columns([1.18, 1], gap="large")
    with left:
        st.markdown("### Memory activity overview")
        st.markdown("<div class='muted'>Every request is either a hit or a fault. A fault may force a replacement when all frames are occupied.</div>", unsafe_allow_html=True)
        trace_df = pd.DataFrame([{ "Step": row["Step"], "Requested page": row["Requested page"], "Result": row["Result"], "Evicted page": row["Evicted page"] } for row in selected_result["steps"]])
        colors = ["#5be7c4" if r == "HIT" else "#ff718b" for r in trace_df["Result"]]
        fig = go.Figure()
        fig.add_trace(go.Bar(x=trace_df["Step"], y=[1] * len(trace_df), marker_color=colors, text=trace_df["Requested page"], textposition="inside", hovertemplate="Step %{x}<br>Page %{text}<br>%{customdata}<extra></extra>", customdata=trace_df["Result"], name="Request"))
        fig.update_layout(yaxis={"visible": False, "fixedrange": True}, xaxis_title="Page request step", bargap=.22, showlegend=False)
        st.plotly_chart(chart_layout(fig, 290), use_container_width=True)
        st.caption("Teal = page hit · Coral = page fault")
    with right:
        st.markdown("### Compare all three policies")
        fault_fig = go.Figure(go.Bar(x=comparison_df["Algorithm"], y=comparison_df["Page Faults"], text=comparison_df["Page Faults"], textposition="outside", marker_color=["#7aa8ff", "#5be7c4", "#b3a1ff"]))
        fault_fig.update_layout(yaxis_title="Number of page faults", showlegend=False)
        st.plotly_chart(chart_layout(fault_fig, 290), use_container_width=True)
        st.caption("Lower page faults are generally better for this reference sequence.")

    st.markdown("### Current memory frames — final state")
    frame_cols = st.columns(frame_count, gap="small")
    for i, page in enumerate(selected_result["final_frames"]):
        with frame_cols[i]:
            value = page if page is not None else "EMPTY"
            klass = "frame" if page is not None else "frame-empty"
            st.markdown(f"<div class='{klass}'><div class='frame-label'>FRAME {i + 1}</div><div class='frame-value' style='font-size:1.55rem'>{value}</div></div>", unsafe_allow_html=True)

    st.markdown("### Experiment report")
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    csv = comparison_df.to_csv(index=False).encode("utf-8")
    st.download_button("Download comparison as CSV", data=csv, file_name="page_replacement_comparison.csv", mime="text/csv")

elif view == "Step-by-step Simulator":
    show_hero("Watch every <span class='grad'>memory decision.</span>", "Move through the page references one step at a time. See whether the page hits, faults, or evicts another page.", "INTERACTIVE TRACE")
    algorithm = selected_algorithm
    result = simulate_page_replacement(pages, frame_count, algorithm)
    max_step = len(result["steps"])
    step_number = st.slider("Choose a request step", min_value=1, max_value=max_step, value=min(4, max_step), key="trace_step")
    row = result["steps"][step_number - 1]
    status_class = "good" if row["Result"] == "HIT" else "bad"
    st.markdown(f"<div class='panel'><div class='eyebrow'>STEP {step_number} OF {max_step}</div><div style='font-size:1.25rem;font-weight:800;margin:.3rem 0'>Requested page <span class='grad'>{row['Requested page']}</span> &nbsp;·&nbsp; <span class='{status_class}'>{row['Result']}</span></div><div class='muted'>Algorithm: {algorithm} &nbsp; | &nbsp; Evicted page: {row['Evicted page']}</div></div>", unsafe_allow_html=True)
    st.markdown("### RAM frame view")
    frame_cols = st.columns(frame_count, gap="small")
    for i, page in enumerate(row["frame_values"]):
        with frame_cols[i]:
            value = page if page is not None else "EMPTY"
            klass = "frame" if page is not None else "frame-empty"
            st.markdown(f"<div class='{klass}'><div class='frame-label'>FRAME {i + 1}</div><div class='frame-value'>{value}</div></div>", unsafe_allow_html=True)
    st.progress(step_number / max_step, text=f"{step_number} of {max_step} references processed")
    st.markdown("### Trace up to this step")
    display_rows = []
    for item in result["steps"][:step_number]:
        clean = {k: v for k, v in item.items() if k != "frame_values"}
        display_rows.append(clean)
    st.dataframe(pd.DataFrame(display_rows), use_container_width=True, hide_index=True)
    st.info("A HIT means the requested page was already in a frame. A FAULT means it had to be loaded; if memory was full, the selected algorithm chose a victim page.")
    full_csv = pd.DataFrame([{k: v for k, v in item.items() if k != "frame_values"} for item in result["steps"]]).to_csv(index=False).encode("utf-8")
    st.download_button("Download full step trace (CSV)", data=full_csv, file_name=f"{algorithm.lower()}_step_trace.csv", mime="text/csv")

elif view == "Algorithm Comparison":
    show_hero("Three policies. <span class='grad'>One workload.</span>", "Use exactly the same reference string and number of frames to compare FIFO, LRU and Optimal fairly.", "SIDE-BY-SIDE ANALYSIS")
    best = min(all_results, key=lambda item: item["faults"])
    st.markdown(f"<div class='panel'><div class='eyebrow'>LOWEST FAULT COUNT FOR THIS INPUT</div><div style='font-size:1.35rem;font-weight:800;margin-top:.25rem'>{best['algorithm']} <span class='grad'>· {best['faults']} faults</span></div><div class='muted'>This conclusion applies to the current input only. Optimal uses future knowledge and is a theoretical benchmark.</div></div>", unsafe_allow_html=True)
    comp_fig = go.Figure()
    comp_fig.add_trace(go.Bar(name="Page faults", x=comparison_df["Algorithm"], y=comparison_df["Page Faults"], marker_color="#ff718b"))
    comp_fig.add_trace(go.Bar(name="Page hits", x=comparison_df["Algorithm"], y=comparison_df["Page Hits"], marker_color="#5be7c4"))
    comp_fig.update_layout(barmode="group", yaxis_title="Requests", legend={"orientation":"h", "y":1.12, "x":0})
    st.plotly_chart(chart_layout(comp_fig, 390), use_container_width=True)
    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
    st.markdown("### How to interpret the result")
    st.markdown(f"- **FIFO:** {all_results[0]['faults']} faults. Removes the page that entered memory earliest.\n- **LRU:** {all_results[1]['faults']} faults. Removes the page that has been unused for the longest time in the past.\n- **Optimal:** {all_results[2]['faults']} faults. Removes the page whose next use is farthest away. It is a benchmark because future requests are not normally known in advance.")
    st.download_button("Download comparison as CSV", data=comparison_df.to_csv(index=False).encode("utf-8"), file_name="algorithm_comparison.csv", mime="text/csv")

else:
    show_hero("Understand it. <span class='grad'>Explain it.</span>", "A compact theory guide and viva practice for the Page Replacement Algorithm mini-project.", "CONCEPTS · COMPLEXITY · VIVA")
    st.markdown("## Why do page-replacement algorithms exist?")
    st.markdown("A process requests virtual-memory pages. If a requested page is absent from RAM, a **page fault** occurs. When every available frame is occupied, the operating system must choose a resident page to remove. A page-replacement policy defines that choice.")
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("### FIFO — First In, First Out")
        st.markdown("Evicts the page that arrived first. Easy to implement with a queue, but it ignores how recently a page was used.")
        st.markdown("**Typical bookkeeping:** insertion order / queue.")
        st.markdown("### LRU — Least Recently Used")
        st.markdown("Evicts the page whose most recent access is oldest. It uses the past as a clue for future use.")
        st.markdown("**Typical bookkeeping:** last-used timestamp or ordered structure.")
    with c2:
        st.markdown("### Optimal")
        st.markdown("Evicts the page whose next use lies farthest in the future. If a page is never used again, it is a strong candidate for removal.")
        st.markdown("**Typical bookkeeping:** inspect future references; useful as a lower-bound benchmark for this workload.")
        st.markdown("### Important formulas")
        st.latex(r"\text{Hit Rate} = \frac{\text{Page Hits}}{\text{Total Requests}} \times 100\%")
        st.latex(r"\text{Fault Rate} = \frac{\text{Page Faults}}{\text{Total Requests}} \times 100\%")
    st.markdown("---")
    st.markdown("## Viva questions")
    questions = [
        ("What is a page?", "A fixed-size unit of virtual memory used by a process."),
        ("What is a frame?", "A fixed-size slot in physical memory (RAM) that can hold one page."),
        ("What is a page fault?", "An event that occurs when a requested page is not currently present in RAM and must be handled."),
        ("What is a page hit?", "The requested page is already in one of the available frames."),
        ("Which algorithm is best?", "There is no single winner for every workload. Optimal gives the minimum faults for a known reference string, while FIFO and LRU are practical policies with different behavior."),
        ("Why can't a real OS use Optimal directly?", "It would need to know future page requests exactly, which are not available in advance."),
        ("What is the project's input and output?", "Input: page-reference string, frame count and policy. Output: frame-by-frame trace, hit/fault counts, rates and comparison charts."),
        ("What technologies are used?", "Python for the algorithms, Streamlit for the dashboard, Pandas for tabular results, and Plotly for interactive charts."),
        ("Does this project change actual RAM?", "No. It is a simulator for learning page replacement behavior."),
    ]
    for question, answer in questions:
        with st.expander(question):
            st.write(answer)

st.markdown("<div style='margin-top:2.2rem;border-top:1px solid rgba(151,180,222,.16);padding-top:.8rem;color:#7e90ae;font-family:DM Mono,monospace;font-size:.72rem'>PAGEVAULT · PAGE REPLACEMENT ALGORITHM · PYTHON MINI PROJECT</div>", unsafe_allow_html=True)
