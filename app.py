from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from core import compression_report, parse_items, predict_next_page, run_page_replacement, simulate_allocation


# -----------------------------------------------------------------------------
# MemoraX — Smart Memory Lab
# A Python-first educational simulator for OS memory-management concepts.
# -----------------------------------------------------------------------------

st.set_page_config(
    page_title="MemoraX | Smart Memory Lab",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

INK = "#0A1020"
PANEL = "#111B30"
TEAL = "#50E3C2"
BLUE = "#75A7FF"
MUTED = "#9AABC8"

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --mx-bg:#0a1020; --mx-panel:#111b30; --mx-line:rgba(164,190,232,.15); --mx-text:#f2f6ff; --mx-muted:#9aabc8; --mx-teal:#50e3c2; --mx-blue:#75a7ff; }
    html, body, [class*="css"] { font-family: 'Manrope', sans-serif; }
    .stApp { background: radial-gradient(ellipse at 80% 0%, rgba(39,86,142,.22), transparent 38%), var(--mx-bg); color:var(--mx-text); }
    [data-testid="stSidebar"] { background: linear-gradient(180deg,#101a2e,#0b1221); border-right:1px solid var(--mx-line); }
    [data-testid="stSidebar"] * { color:var(--mx-text); }
    [data-testid="stHeader"] { background:rgba(10,16,32,.76); }
    h1,h2,h3 { letter-spacing:-.035em; }
    h1 { font-weight:800 !important; }
    p, label, li { color:#d8e2f6; }
    .mx-eyebrow { text-transform:uppercase; color:var(--mx-teal); font-family:'DM Mono',monospace; letter-spacing:.16em; font-size:.72rem; font-weight:500; }
    .mx-hero { padding:1.7rem 1.8rem; border:1px solid rgba(117,167,255,.25); border-radius:24px; background:linear-gradient(115deg,rgba(26,46,79,.96),rgba(17,27,48,.93) 58%,rgba(16,61,70,.70)); position:relative; overflow:hidden; margin-bottom:1.15rem; }
    .mx-hero:after { content:'MEMORY / INTELLIGENCE'; position:absolute; right:1rem; bottom:.45rem; color:rgba(215,234,255,.07); font-family:'DM Mono',monospace; font-weight:600; font-size:1.15rem; letter-spacing:.14em; }
    .mx-hero h1 { font-size:2.65rem; margin:.28rem 0 .32rem 0; line-height:1.08; }
    .mx-hero p { max-width:760px; color:#c2d0e7; font-size:1rem; margin-bottom:0; }
    .mx-gradient { background:linear-gradient(90deg,#50e3c2,#75a7ff); -webkit-background-clip:text; background-clip:text; color:transparent; }
    .mx-card { border:1px solid var(--mx-line); background:linear-gradient(145deg,rgba(19,31,53,.95),rgba(14,23,40,.96)); border-radius:17px; padding:1.0rem 1.05rem; min-height:112px; box-shadow:0 9px 25px rgba(0,0,0,.10); }
    .mx-card .kicker { color:var(--mx-muted); font-family:'DM Mono',monospace; font-size:.72rem; text-transform:uppercase; letter-spacing:.08em; }
    .mx-card .value { font-size:1.75rem; line-height:1.2; font-weight:800; margin:.24rem 0 .12rem; color:#f5f8ff; }
    .mx-card .note { font-size:.78rem; color:#a4b7d5; }
    .mx-section { font-size:1.25rem; font-weight:800; margin:.55rem 0 .7rem 0; }
    .mx-subtle { color:#9aabc8; font-size:.9rem; }
    .mx-pill { display:inline-block; border:1px solid rgba(80,227,194,.28); background:rgba(80,227,194,.08); color:#77efd6; padding:.25rem .55rem; border-radius:99px; font-family:'DM Mono',monospace; font-size:.72rem; margin-right:.25rem; }
    .mx-code { font-family:'DM Mono',monospace; color:#8cebd7; }
    div[data-testid="stMetric"] { background:linear-gradient(145deg,rgba(19,31,53,.95),rgba(14,23,40,.96)); border:1px solid var(--mx-line); padding:1rem 1.1rem; border-radius:15px; }
    div[data-testid="stMetricLabel"] { color:var(--mx-muted); }
    div[data-testid="stMetricValue"] { color:#f5f8ff; }
    div[data-testid="stMetricDelta"] { font-size:.82rem; }
    .stButton button { border-radius:10px; border:1px solid rgba(80,227,194,.35); background:linear-gradient(90deg,rgba(80,227,194,.14),rgba(117,167,255,.12)); color:#edfffb; font-weight:700; }
    .stButton button:hover { border-color:var(--mx-teal); color:white; }
    .stTextInput input, .stTextArea textarea, .stNumberInput input { background:#0d1729; color:#f5f8ff; border-color:var(--mx-line); border-radius:10px; }
    div[data-baseweb="select"] > div { background:#0d1729; border-color:var(--mx-line); border-radius:10px; }
    div[data-testid="stDataFrame"] { border:1px solid var(--mx-line); border-radius:12px; overflow:hidden; }
    hr { border-color:var(--mx-line); }
    .mx-footer { color:#7286a8; font-family:'DM Mono',monospace; font-size:.72rem; border-top:1px solid var(--mx-line); padding-top:1rem; margin-top:2rem; }
    </style>
    """,
    unsafe_allow_html=True,
)


# ---- Core algorithms, separated from UI so they can be unit-tested. ---------

def html_card(title: str, value: str, note: str = "") -> str:
    return f'<div class="mx-card"><div class="kicker">{title}</div><div class="value">{value}</div><div class="note">{note}</div></div>'


def page_header(eyebrow: str, title: str, subtitle: str) -> None:
    st.markdown(f'<div class="mx-eyebrow">{eyebrow}</div><h1 style="margin-top:.22rem">{title}</h1><p class="mx-subtle" style="margin-top:-.35rem;margin-bottom:1.2rem">{subtitle}</p>', unsafe_allow_html=True)


def show_algorithm_note(title: str, description: str, complexity: str) -> None:
    st.markdown(f'<div class="mx-card" style="min-height:auto"><div class="kicker">CONCEPT NOTE</div><div style="font-size:1.06rem;font-weight:800;margin:.22rem 0">{title}</div><div class="note" style="font-size:.9rem;line-height:1.6">{description}<br><span class="mx-code">Complexity: {complexity}</span></div></div>', unsafe_allow_html=True)


# ---- Sidebar / navigation ----------------------------------------------------
with st.sidebar:
    st.markdown("<div style='display:flex;align-items:center;gap:12px;margin:.3rem 0 1rem'><div style='font-size:2rem'>◈</div><div><div style='font-size:1.25rem;font-weight:800;letter-spacing:-.04em'>Memora<span style='color:#50e3c2'>X</span></div><div style='font-size:.68rem;color:#9aabc8;letter-spacing:.13em'>SMART MEMORY LAB</div></div></div>", unsafe_allow_html=True)
    st.markdown("<div class='mx-pill'>PYTHON EDITION</div><div style='height:15px'></div>", unsafe_allow_html=True)
    section = st.radio(
        "NAVIGATION",
        ["Overview", "Page Replacement", "Memory Allocation", "Compression Lab", "Intelligent Prefetching", "ML Integration", "Project & Viva"],
        label_visibility="visible",
    )
    st.markdown("---")
    st.markdown("<div class='mx-eyebrow'>CORE MODULES</div>", unsafe_allow_html=True)
    st.markdown("<div style='line-height:2.05;font-size:.87rem;color:#c2d0e7'>01 &nbsp; Page replacement<br>02 &nbsp; Memory allocation<br>03 &nbsp; Compression techniques<br>04 &nbsp; Intelligent prefetching<br>05 &nbsp; ML framework integration</div>", unsafe_allow_html=True)
    st.markdown("---")
    st.caption("A learning simulator — not a tool that modifies the computer's actual RAM.")


# ---- Overview ---------------------------------------------------------------
if section == "Overview":
    st.markdown(
        """
        <div class="mx-hero">
          <div class="mx-eyebrow">OPERATING SYSTEMS · MINI PROJECT</div>
          <h1>Memory, made <span class="mx-gradient">intelligent.</span></h1>
          <p>Explore how operating systems store, allocate, compress, and predict memory — with live simulations and measurable outcomes.</p>
          <div style="margin-top:1.15rem"><span class="mx-pill">5 EXPERIMENTS</span><span class="mx-pill">LIVE SIMULATIONS</span><span class="mx-pill">PYTHON + STREAMLIT</span></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    c1, c2, c3, c4 = st.columns(4)
    for col, title, value, note in [
        (c1, "Learning modules", "05", "Covers every listed topic"),
        (c2, "Replacement policies", "03", "FIFO · LRU · Optimal"),
        (c3, "Allocation strategies", "03", "First · Best · Worst Fit"),
        (c4, "Runtime", "Python", "Local browser dashboard"),
    ]:
        with col:
            st.markdown(html_card(title, value, note), unsafe_allow_html=True)
    st.markdown("<div class='mx-section'>Explore the lab</div>", unsafe_allow_html=True)
    overview_cols = st.columns(3, gap="medium")
    modules = [
        ("01", "Page replacement", "Watch memory frames change on each page reference. Compare page faults and hit rates."),
        ("02", "Memory allocation", "See how process sizes fit into available memory blocks under three placement strategies."),
        ("03", "Compression lab", "Measure real zlib compression and inspect repeated tokens in your sample text."),
        ("04", "Intelligent prefetching", "Infer likely future pages from patterns in a memory-access sequence."),
        ("05", "ML integration", "Train a small scikit-learn model on page histories and inspect its next-page prediction."),
        ("06", "Viva prep", "Use the included project summary, limitations, and likely teacher questions."),
    ]
    for i, (num, title, desc) in enumerate(modules):
        with overview_cols[i % 3]:
            st.markdown(f'<div class="mx-card" style="margin-bottom:.8rem;min-height:155px"><div class="kicker">MODULE {num}</div><div style="font-size:1.04rem;font-weight:800;margin:.35rem 0">{title}</div><div class="note" style="font-size:.86rem;line-height:1.55">{desc}</div></div>', unsafe_allow_html=True)
    st.markdown("<div class='mx-section'>Start with a quick experiment</div>", unsafe_allow_html=True)
    with st.container(border=True):
        a, b, c = st.columns([2, 1, 1])
        with a:
            demo_sequence = st.text_input("Page-reference string", "A B C A B D A B C D", key="overview_seq")
        with b:
            demo_frames = st.number_input("Frames", 1, 8, 3, key="overview_frames")
        with c:
            demo_algorithm = st.selectbox("Algorithm", ["FIFO", "LRU", "Optimal"], key="overview_alg")
        if st.button("Run quick simulation", type="primary", use_container_width=True):
            parsed = parse_items(demo_sequence)
            if not parsed:
                st.warning("Enter at least one page reference.")
            else:
                result = run_page_replacement(parsed, int(demo_frames), demo_algorithm)
                m1, m2, m3 = st.columns(3)
                m1.metric("Page faults", result["faults"])
                m2.metric("Page hits", result["hits"])
                m3.metric("Hit rate", f'{result["hit_rate"]:.1f}%')
                st.dataframe(pd.DataFrame(result["steps"]), use_container_width=True, hide_index=True)
    st.markdown("<div class='mx-footer'>MEMORAX / PYTHON EDITION · BUILT FOR DEMONSTRATION & LEARNING</div>", unsafe_allow_html=True)


# ---- Page Replacement --------------------------------------------------------
elif section == "Page Replacement":
    page_header("MODULE 01 / OPERATING SYSTEMS", "Page Replacement Studio", "Compare FIFO, LRU, and Optimal as page references flow through a limited set of memory frames.")
    with st.container(border=True):
        left, right = st.columns([2.4, 1])
        with left:
            sequence_text = st.text_input("Page-reference string", "7 0 1 2 0 3 0 4 2 3 0 3 2", help="Use spaces or commas between page labels.")
        with right:
            frame_count = st.slider("Number of frames", 1, 6, 3)
        algorithms = st.multiselect("Algorithms to compare", ["FIFO", "LRU", "Optimal"], default=["FIFO", "LRU", "Optimal"])
        run_replacement = st.button("Run comparison", type="primary", use_container_width=True)
    sequence = parse_items(sequence_text)
    # Cache by the full input signature so changing frames or algorithms refreshes
    # results immediately, even when the reference-string length stays the same.
    page_signature = (tuple(sequence), int(frame_count), tuple(algorithms))
    if run_replacement or st.session_state.get("page_signature") != page_signature:
        st.session_state["page_results"] = [run_page_replacement(sequence, int(frame_count), name) for name in algorithms] if sequence and algorithms else []
        st.session_state["page_signature"] = page_signature
    results = st.session_state.get("page_results", [])
    if not sequence:
        st.warning("Enter at least one page reference to begin.")
    elif not results:
        st.info("Select at least one algorithm and click Run comparison.")
    else:
        summary = pd.DataFrame([{"Algorithm": r["algorithm"], "Hits": r["hits"], "Faults": r["faults"], "Hit rate (%)": round(r["hit_rate"], 1), "Fault rate (%)": round(r["fault_rate"], 1)} for r in results])
        best = min(results, key=lambda x: x["faults"])
        met1, met2, met3, met4 = st.columns(4)
        met1.metric("References", len(sequence))
        met2.metric("Frames", frame_count)
        met3.metric("Lowest faults", f'{best["faults"]} · {best["algorithm"]}')
        met4.metric("Best hit rate", f'{max(r["hit_rate"] for r in results):.1f}%')
        st.markdown("<div class='mx-section'>Policy comparison</div>", unsafe_allow_html=True)
        fig = px.bar(summary, x="Algorithm", y="Faults", color="Algorithm", text="Faults", template="plotly_dark", title="Page faults by algorithm")
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, margin=dict(l=10, r=10, t=55, b=10), font_color="#dce7fa")
        fig.update_traces(textposition="outside")
        st.plotly_chart(fig, use_container_width=True)
        selected = st.selectbox("Inspect step-by-step frames", [r["algorithm"] for r in results])
        result = next(r for r in results if r["algorithm"] == selected)
        display = pd.DataFrame(result["steps"])
        frame_columns = [f"Frame {i}" for i in range(1, frame_count + 1)]
        st.dataframe(display[["Step", "Page", *frame_columns, "Result", "Evicted"]], use_container_width=True, hide_index=True)
        st.markdown("<div class='mx-section'>How the algorithms choose a victim</div>", unsafe_allow_html=True)
        n1, n2, n3 = st.columns(3)
        with n1:
            show_algorithm_note("FIFO", "Evicts the page that has been in memory the longest. Simple, but it may remove a frequently used page.", "O(1) victim selection with a queue")
        with n2:
            show_algorithm_note("LRU", "Evicts the page that has not been used for the longest time in the past.", "O(1) with a suitable data structure; this demo uses a small scan")
        with n3:
            show_algorithm_note("Optimal", "Evicts the page whose next use is farthest in the future. This is a theoretical benchmark because future requests are not normally known.", "O(n × frames) in this teaching implementation")


# ---- Memory Allocation -------------------------------------------------------
elif section == "Memory Allocation":
    page_header("MODULE 02 / PARTITIONING", "Memory Allocation Arena", "Place processes into free memory blocks and compare how each fit strategy uses the available space.")
    with st.container(border=True):
        left, right = st.columns(2)
        with left:
            block_text = st.text_input("Memory block sizes", "100, 500, 200, 300, 600", help="Enter positive sizes separated by commas.")
        with right:
            process_text = st.text_input("Process sizes", "212, 417, 112, 426", help="Enter process sizes in the same units as memory blocks.")
        strategy = st.radio("Allocation strategy", ["First Fit", "Best Fit", "Worst Fit"], horizontal=True)
        run_allocation = st.button("Allocate processes", type="primary", use_container_width=True)
    try:
        blocks = [int(x) for x in parse_items(block_text)]
        processes = [int(x) for x in parse_items(process_text)]
        if not blocks or not processes or any(x <= 0 for x in blocks + processes):
            raise ValueError("Enter positive sizes for at least one block and one process.")
        allocation_result = simulate_allocation(blocks, processes, strategy)
        st.session_state["allocation_result"] = allocation_result
        st.session_state["allocation_strategy"] = strategy
    except ValueError as exc:
        st.error(str(exc) if str(exc) else "Please enter valid integer sizes.")
        allocation_result = None
    if allocation_result:
        a, b, c, d = st.columns(4)
        a.metric("Allocated", f'{allocation_result["allocated_count"]}/{len(processes)}')
        b.metric("Unallocated", allocation_result["failed_count"])
        c.metric("Memory used", f'{allocation_result["used_memory"]} units')
        d.metric("Memory free", f'{allocation_result["free_memory"]} units')
        st.markdown("<div class='mx-section'>Memory map</div>", unsafe_allow_html=True)
        block_df = pd.DataFrame(allocation_result["blocks"])
        fig = go.Figure()
        fig.add_trace(go.Bar(y=block_df["Block"], x=block_df["Used"], name="Allocated", orientation="h", marker_color="#50e3c2", text=block_df["Used"], textposition="inside"))
        fig.add_trace(go.Bar(y=block_df["Block"], x=block_df["Free"], name="Free", orientation="h", marker_color="#304466", text=block_df["Free"], textposition="inside"))
        fig.update_layout(barmode="stack", title="Allocated vs free space in each block", xaxis_title="Memory units", yaxis_title="Memory block", template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dce7fa", margin=dict(l=10, r=10, t=55, b=10), legend=dict(orientation="h", y=1.12))
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("<div class='mx-section'>Process allocation results</div>", unsafe_allow_html=True)
        st.dataframe(pd.DataFrame(allocation_result["allocations"]), use_container_width=True, hide_index=True)
        with st.expander("View block-by-block details"):
            st.dataframe(block_df, use_container_width=True, hide_index=True)
        st.caption("This model uses variable-sized partitions: a process takes space from a block, leaving the remaining space available for later processes.")
    st.markdown("<div class='mx-section'>Strategy guide</div>", unsafe_allow_html=True)
    cols = st.columns(3)
    notes = [
        ("First Fit", "Choose the first free block large enough for the process. Usually quick; early blocks can become fragmented."),
        ("Best Fit", "Choose the smallest available block that can fit the process. It may leave tiny leftover spaces."),
        ("Worst Fit", "Choose the largest available block. It tries to leave a larger remainder for later allocations."),
    ]
    for col, (title, desc) in zip(cols, notes):
        with col:
            show_algorithm_note(title, desc, "O(processes × blocks) in this demo")


# ---- Compression -------------------------------------------------------------
elif section == "Compression Lab":
    page_header("MODULE 03 / STORAGE EFFICIENCY", "Compression Lab", "Run real lossless compression with Python's built-in zlib, then inspect repeated words that make good teaching examples for dictionary coding.")
    sample = "Memory management helps an operating system use memory efficiently. Efficient memory management allocates memory to processes and reclaims memory when processes finish. A memory page may be loaded, replaced, or stored again."
    text_input = st.text_area("Text to compress", sample, height=180, help="Use a longer repeated sample for a more illustrative compression ratio.")
    if st.button("Compress sample", type="primary", use_container_width=True):
        st.session_state["compression_result"] = compression_report(text_input)
    report = st.session_state.get("compression_result")
    # Show a report on first open without requiring the button.
    if report is None:
        report = compression_report(text_input)
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Original size", f'{report["original_bytes"]} B')
    c2.metric("Compressed size", f'{report["compressed_bytes"]} B')
    c3.metric("Space saved", f'{report["saved_bytes"]} B', delta=f'{report["saved_percent"]:.1f}% vs original' if report["original_bytes"] else None)
    c4.metric("Compression ratio", f'{report["ratio"]:.2f}×')
    if report["saved_bytes"] < 0:
        st.info("For this short sample, compression metadata can make the compressed output larger than the original. Try repeating a sentence or using a longer sample.")
    else:
        st.success(f'Round-trip check: {"passed" if report["round_trip_ok"] else "failed"} — decompression exactly restores the original text.')
    st.markdown("<div class='mx-section'>Size comparison</div>", unsafe_allow_html=True)
    size_df = pd.DataFrame({"Representation": ["Original", "zlib compressed"], "Bytes": [report["original_bytes"], report["compressed_bytes"]]})
    fig = px.bar(size_df, x="Representation", y="Bytes", text="Bytes", color="Representation", template="plotly_dark", title="Actual UTF-8 bytes")
    fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", showlegend=False, font_color="#dce7fa", margin=dict(l=10, r=10, t=55, b=10))
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)
    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("<div class='mx-section'>Repeated-token dictionary preview</div>", unsafe_allow_html=True)
        if report["repeated_tokens"]:
            st.dataframe(pd.DataFrame(report["repeated_tokens"]), use_container_width=True, hide_index=True)
        else:
            st.info("No repeated word tokens were found. Add repeated words to see a dictionary preview.")
    with right:
        st.markdown("<div class='mx-section'>What is happening?</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="mx-card" style="min-height:auto;line-height:1.7">
        <b>1 · Read bytes</b><br><span class="note">The text is encoded as UTF-8.</span><br>
        <b>2 · Compress losslessly</b><br><span class="note">Python's zlib applies DEFLATE-style compression. Repeated patterns can be represented more compactly.</span><br>
        <b>3 · Verify the result</b><br><span class="note">The compressed bytes are decompressed and compared with the original bytes.</span><br><br>
        <span class="note">The repeated-token table is an explanatory preview; zlib does not use this exact visible word dictionary. Compression depends on the data and can expand very short inputs.</span>
        </div>
        """, unsafe_allow_html=True)
    with st.expander("Inspect compressed-byte preview (hexadecimal)"):
        st.code(report["compressed_preview"] or "(empty input)", language="text")


# ---- Intelligent prefetching -------------------------------------------------
elif section == "Intelligent Prefetching":
    page_header("MODULE 04 / PREDICTIVE ACCESS", "Intelligent Prefetching", "Learn page-access transitions and rank which page is most likely to be requested next. This is a small, explainable predictor — not a guarantee.")
    with st.container(border=True):
        sequence_text = st.text_input("Observed page history", "A B C A B C A B D A B C A B", key="prefetch_seq")
        context_size = st.select_slider("Context window", options=[1, 2, 3], value=2, help="Use the last 1–3 observed pages as the context for a prediction.")
        st.caption("Tip: repeat a pattern such as A B C A B C to make transitions easy to spot.")
    sequence = parse_items(sequence_text)
    result = predict_next_page(sequence, int(context_size))
    if len(sequence) < 2:
        st.warning("Enter at least two page references to learn a pattern.")
    else:
        top_prediction = result["predictions"][0] if result["predictions"] else None
        a, b, c = st.columns(3)
        a.metric("History length", len(sequence))
        b.metric("Current context", " → ".join(result["context"]))
        c.metric("Top prediction", top_prediction["Next page"] if top_prediction else "—", delta=f'{top_prediction["Probability"]:.1f}% observed share' if top_prediction else None)
        st.markdown("<div class='mx-section'>Next-page likelihood</div>", unsafe_allow_html=True)
        if result["predictions"]:
            pred_df = pd.DataFrame(result["predictions"])
            fig = px.bar(pred_df, x="Next page", y="Probability", text="Probability", color="Probability", color_continuous_scale=["#304466", "#50e3c2"], template="plotly_dark", title="Prediction scores from observed transitions")
            fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dce7fa", coloraxis_showscale=False, margin=dict(l=10, r=10, t=55, b=10), yaxis_title="Observed transition share (%)")
            fig.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
            st.plotly_chart(fig, use_container_width=True)
            st.dataframe(pred_df, use_container_width=True, hide_index=True)
        st.markdown(f'<div class="mx-card" style="min-height:auto"><div class="kicker">MODEL EXPLANATION</div><div style="font-size:1.05rem;font-weight:800;margin:.3rem 0">{result["method"]}</div><div class="note" style="font-size:.9rem;line-height:1.6">The simulator counts what page(s) tended to follow the current context in the supplied history. It ranks those candidates by observed frequency. If the exact context has not appeared, it falls back to a shorter context and then overall frequencies.</div></div>', unsafe_allow_html=True)
        st.markdown("<div class='mx-section'>Observed sequence</div>", unsafe_allow_html=True)
        st.markdown(" ".join([f'<span class="mx-pill">{i+1:02d} · {page}</span>' for i, page in enumerate(sequence)]), unsafe_allow_html=True)
    st.info("Why prefetch? If the prediction is right, the OS may load a page before the program asks for it, reducing perceived wait time. Incorrect prefetching can waste bandwidth and memory.")


# ---- ML integration ----------------------------------------------------------
elif section == "ML Integration":
    page_header("MODULE 05 / ML FRAMEWORK", "Machine Learning Integration", "Train a real scikit-learn classifier on a small page-history dataset, then use recent accesses to predict the next page.")
    st.markdown("""
    <div class="mx-card" style="min-height:auto;margin-bottom:1rem">
      <div class="kicker">PIPELINE</div>
      <div style="font-size:1rem;font-weight:800;margin:.3rem 0">Access history → features → Random Forest → next-page scores</div>
      <div class="note" style="font-size:.9rem;line-height:1.65">The model treats the previous page and current page as categorical features, with the following page as the label. The demo trains on the sequence provided below. Short histories create very small training sets, so predictions should be treated as a classroom demonstration.</div>
    </div>
    """, unsafe_allow_html=True)
    ml_sequence_text = st.text_input("Training page history", "A B C A B C A B D A B C A B C", key="ml_sequence")
    ml_sequence = parse_items(ml_sequence_text)
    if len(ml_sequence) < 4:
        st.warning("Add at least four page references to create training examples.")
    else:
        training_rows = []
        labels = []
        for i in range(2, len(ml_sequence)):
            training_rows.append({"previous_page": ml_sequence[i - 2], "current_page": ml_sequence[i - 1]})
            labels.append(ml_sequence[i])
        data = pd.DataFrame(training_rows)
        m1, m2, m3 = st.columns(3)
        m1.metric("Training examples", len(training_rows))
        m2.metric("Distinct page labels", len(set(labels)))
        m3.metric("Feature columns", 2)
        try:
            from sklearn.ensemble import RandomForestClassifier
            from sklearn.feature_extraction import DictVectorizer

            vectorizer = DictVectorizer(sparse=False)
            query = {"previous_page": ml_sequence[-2], "current_page": ml_sequence[-1]}
            # Include query feature categories in the encoder vocabulary, but do not
            # use the query row to train the classifier.
            all_features = vectorizer.fit_transform(training_rows + [query])
            X = all_features[:-1]
            pred_X = all_features[-1].reshape(1, -1)
            model = RandomForestClassifier(n_estimators=120, random_state=42, max_depth=6, class_weight="balanced")
            model.fit(X, labels)
            predicted = str(model.predict(pred_X)[0])
            probabilities = model.predict_proba(pred_X)[0]
            score_rows = sorted([{"Candidate page": str(label), "Model probability (%)": round(float(prob) * 100, 1)} for label, prob in zip(model.classes_, probabilities)], key=lambda row: row["Model probability (%)"], reverse=True)
            q1, q2 = st.columns([1, 1.4])
            with q1:
                st.markdown("<div class='mx-section'>Prediction</div>", unsafe_allow_html=True)
                st.markdown(html_card("Next-page prediction", predicted, f'Context: {query["previous_page"]} → {query["current_page"]}'), unsafe_allow_html=True)
                st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
                st.success("scikit-learn model trained successfully.")
            with q2:
                st.markdown("<div class='mx-section'>Class probabilities</div>", unsafe_allow_html=True)
                score_df = pd.DataFrame(score_rows)
                fig = px.bar(score_df, x="Candidate page", y="Model probability (%)", text="Model probability (%)", template="plotly_dark", color="Model probability (%)", color_continuous_scale=["#304466", "#50e3c2"])
                fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color="#dce7fa", coloraxis_showscale=False, margin=dict(l=10, r=10, t=20, b=10))
                fig.update_traces(textposition="outside")
                st.plotly_chart(fig, use_container_width=True)
            st.markdown("<div class='mx-section'>Training data preview</div>", unsafe_allow_html=True)
            data["next_page_label"] = labels
            st.dataframe(data, use_container_width=True, hide_index=True)
            with st.expander("Technical details"):
                st.write("**Framework:** scikit-learn")
                st.write("**Estimator:** RandomForestClassifier (120 trees, fixed random seed for reproducibility)")
                st.write("**Feature encoding:** DictVectorizer converts page labels into categorical indicator features.")
                st.write("**Important limitation:** Because the training examples come from the same short sequence being explored, this demo is not evidence of real-world predictive accuracy. A practical system would need larger, held-out traces and performance/latency tests.")
        except ImportError:
            st.error("scikit-learn is not installed in this Python environment. Run `python -m pip install -r requirements.txt`, then restart Streamlit.")
        except Exception as exc:
            st.error(f"The ML experiment could not be trained for this input: {exc}")
    st.markdown("<div class='mx-section'>How this connects to an ML framework</div>", unsafe_allow_html=True)
    st.write("The rest of the project is built with Python. This module demonstrates integration with scikit-learn: feature preparation, model fitting, inference, and confidence scores. It is intentionally small enough to understand and explain in a viva.")


# ---- Project documentation / viva -------------------------------------------
elif section == "Project & Viva":
    page_header("PROJECT NOTES / PRESENTATION", "Project & Viva Guide", "A presentation-ready summary of the problem, solution, methods, and limitations.")
    st.markdown("<div class='mx-section'>Problem statement</div>", unsafe_allow_html=True)
    st.write("Operating systems must manage limited memory efficiently. Poor page-replacement or allocation choices can increase page faults, waste free space, or slow program execution. Compression and prefetching provide additional ways to use resources more efficiently.")
    st.markdown("<div class='mx-section'>Objectives</div>", unsafe_allow_html=True)
    for item in [
        "Visualize FIFO, LRU, and Optimal page replacement and compare page-fault counts.",
        "Demonstrate First Fit, Best Fit, and Worst Fit memory allocation.",
        "Measure lossless compression using Python's zlib library.",
        "Predict likely future page accesses from observed transitions.",
        "Integrate scikit-learn to train a simple page-history classifier.",
    ]:
        st.markdown(f"- {item}")
    st.markdown("<div class='mx-section'>Suggested 2-minute demonstration</div>", unsafe_allow_html=True)
    steps = [
        ("0:00–0:20", "Introduction", "Introduce MemoraX as a visual simulator for memory-management concepts."),
        ("0:20–0:50", "Page replacement", "Keep three frames, run FIFO/LRU/Optimal, and point out that the page-fault count can differ."),
        ("0:50–1:15", "Memory allocation", "Change a process size and compare First Fit with Best Fit or Worst Fit."),
        ("1:15–1:35", "Compression and prefetching", "Show the real byte comparison, then show a likely next-page prediction."),
        ("1:35–2:00", "ML integration", "Train the Random Forest and explain the input features and predicted next page."),
    ]
    for time, title, desc in steps:
        with st.expander(f"{time} · {title}", expanded=False):
            st.write(desc)
    st.markdown("<div class='mx-section'>Likely viva questions</div>", unsafe_allow_html=True)
    questions = [
        ("What is a page fault?", "A page fault occurs when a requested page is not currently in main memory and must be brought in or otherwise handled by the operating system."),
        ("What is Belady's anomaly?", "For some page-reference strings, FIFO can produce more page faults when the number of frames increases."),
        ("Why is Optimal mainly theoretical?", "It requires knowing future page references, which a normal operating system cannot know exactly."),
        ("Which allocation strategy is best?", "There is no universally best strategy; the result depends on block sizes and process requests. This simulator makes that trade-off visible."),
        ("What is lossless compression?", "Compression is lossless if decompressing the output reconstructs the original input exactly."),
        ("Why can prefetching be harmful?", "Wrong predictions consume memory and I/O bandwidth and may evict data that is actually needed."),
        ("What does the ML model learn?", "It learns a mapping from the previous two page labels to a likely next page, using the examples in the supplied sequence."),
        ("Is this controlling real RAM?", "No. It is an educational simulation that models memory-management decisions and visualizes their consequences."),
    ]
    for question, answer in questions:
        with st.expander(question):
            st.write(answer)
    st.markdown("<div class='mx-section'>Technologies</div>", unsafe_allow_html=True)
    tech1, tech2, tech3, tech4 = st.columns(4)
    tech1.markdown(html_card("Language", "Python", "Application and algorithms"), unsafe_allow_html=True)
    tech2.markdown(html_card("Interface", "Streamlit", "Interactive dashboard"), unsafe_allow_html=True)
    tech3.markdown(html_card("Visualization", "Plotly", "Charts and comparisons"), unsafe_allow_html=True)
    tech4.markdown(html_card("Machine learning", "scikit-learn", "Random Forest classifier"), unsafe_allow_html=True)
    st.warning("Be accurate in your presentation: the page replacement, allocation, compression, and transition prediction are simulations. The Random Forest is genuinely trained in Python, but its sample dataset is small and is not intended for production OS decisions.")


st.markdown("<div class='mx-footer'>MEMORAX · SMART MEMORY LAB · PYTHON / STREAMLIT / PLOTLY / SCIKIT-LEARN</div>", unsafe_allow_html=True)
