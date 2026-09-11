import streamlit as st
from utils.calculations import calc_brickwork, calc_plaster, calc_concrete, calc_steel
from utils.data import MORTAR_RATIOS, CONCRETE_RATIOS, WASTAGE_DEFAULTS, STEEL_BAR_SIZES_MM
from utils.groq_helper import ask_groq

st.set_page_config(page_title="Civil QuantEstimate", page_icon="🏗️", layout="wide")

# Keep last result in session so the AI tab can reference it
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_module" not in st.session_state:
    st.session_state.last_module = None


def show_results(title, results: dict):
    st.subheader(title)
    cols = st.columns(3)
    for i, (k, v) in enumerate(results.items()):
        cols[i % 3].metric(k, v)
    st.session_state.last_result = results
    st.session_state.last_module = title


# ---------------- Sidebar navigation ----------------
st.sidebar.title("🏗️ Civil QuantEstimate")
st.sidebar.caption("AI-assisted construction quantity takeoff")
page = st.sidebar.radio(
    "Select a module",
    ["🏠 Home", "🧱 Brickwork", "🪣 Plaster", "🏗️ Concrete / RCC", "🔩 Steel / BBS", "🤖 AI Assistant"],
)

# ---------------- Home ----------------
if page == "🏠 Home":
    st.title("Civil QuantEstimate")
    st.write(
        "An AI-assisted quantity takeoff tool for civil engineering students, "
        "site engineers, and contractors. Pick a module from the sidebar, enter "
        "dimensions, and get instant material quantities — with formulas kept "
        "transparent so results can be checked by hand."
    )
    st.info("Current version calculates **quantities only** (cost estimation is a future phase).")
    st.markdown("**Modules available:** Brickwork · Plaster · Concrete/RCC · Steel/BBS · AI Assistant")

# ---------------- Brickwork ----------------
elif page == "🧱 Brickwork":
    st.title("Brickwork / Masonry Calculator")
    c1, c2 = st.columns(2)
    with c1:
        length = st.number_input("Wall Length (m)", min_value=0.0, value=10.0, step=0.1)
        height = st.number_input("Wall Height (m)", min_value=0.0, value=3.0, step=0.1)
        thickness = st.number_input("Wall Thickness (m)", min_value=0.0, value=0.23, step=0.01)
    with c2:
        quantity = st.number_input("Quantity (no. of walls)", min_value=1, value=1, step=1)
        mortar_ratio = st.selectbox("Mortar Ratio", list(MORTAR_RATIOS.keys()), index=2)
        wastage = st.number_input("Wastage %", min_value=0.0, value=float(WASTAGE_DEFAULTS["brickwork"]))

    st.markdown("**Openings (doors/windows) — total area to subtract**")
    opening_area = st.number_input("Total Opening Area (m²)", min_value=0.0, value=2.1, step=0.1)

    if st.button("Calculate Brickwork", type="primary"):
        results = calc_brickwork(length, height, thickness, quantity, mortar_ratio, wastage, opening_area)
        show_results("Brickwork Results", results)

# ---------------- Plaster ----------------
elif page == "🪣 Plaster":
    st.title("Plaster Calculator")
    c1, c2 = st.columns(2)
    with c1:
        length = st.number_input("Length (m)", min_value=0.0, value=10.0, step=0.1)
        height = st.number_input("Height (m)", min_value=0.0, value=3.0, step=0.1)
        quantity = st.number_input("Quantity (no. of surfaces)", min_value=1, value=1, step=1)
    with c2:
        thickness_mm = st.number_input("Thickness (mm)", min_value=1.0, value=12.0, step=1.0)
        mortar_ratio = st.selectbox("Mortar Ratio", list(MORTAR_RATIOS.keys()), index=1)
        wastage = st.number_input("Wastage %", min_value=0.0, value=float(WASTAGE_DEFAULTS["plaster"]))

    opening_area = st.number_input("Total Opening Area to Subtract (m²)", min_value=0.0, value=2.1, step=0.1)

    if st.button("Calculate Plaster", type="primary"):
        results = calc_plaster(length, height, quantity, thickness_mm, mortar_ratio, wastage, opening_area)
        show_results("Plaster Results", results)

# ---------------- Concrete ----------------
elif page == "🏗️ Concrete / RCC":
    st.title("Concrete / RCC Calculator")
    c1, c2 = st.columns(2)
    with c1:
        length = st.number_input("Length (m)", min_value=0.0, value=5.0, step=0.1)
        width = st.number_input("Width (m)", min_value=0.0, value=0.3, step=0.05)
        thickness = st.number_input("Thickness (m)", min_value=0.0, value=0.15, step=0.01)
    with c2:
        quantity = st.number_input("Quantity (no. of elements)", min_value=1, value=1, step=1)
        mix_ratio = st.selectbox("Mix Ratio", list(CONCRETE_RATIOS.keys()), index=1)
        wastage = st.number_input("Wastage %", min_value=0.0, value=float(WASTAGE_DEFAULTS["concrete"]))

    if st.button("Calculate Concrete", type="primary"):
        results = calc_concrete(length, width, thickness, quantity, mix_ratio, wastage)
        show_results("Concrete / RCC Results", results)

# ---------------- Steel ----------------
elif page == "🔩 Steel / BBS":
    st.title("Steel / Bar Bending Schedule Calculator")
    c1, c2 = st.columns(2)
    with c1:
        bar_dia = st.selectbox("Bar Diameter (mm)", STEEL_BAR_SIZES_MM, index=3)
        bar_length = st.number_input("Bar Length (m)", min_value=0.0, value=6.0, step=0.1)
    with c2:
        no_of_bars = st.number_input("Number of Bars", min_value=1, value=10, step=1)
        wastage = st.number_input("Wastage %", min_value=0.0, value=float(WASTAGE_DEFAULTS["steel"]))

    if st.button("Calculate Steel", type="primary"):
        results = calc_steel(bar_dia, bar_length, no_of_bars, wastage)
        show_results("Steel / BBS Results", results)

# ---------------- AI Assistant ----------------
elif page == "🤖 AI Assistant":
    st.title("AI Assistant (Groq)")
    st.caption("Ask about formulas, mix ratios, or your last calculated result.")

    if st.session_state.last_result:
        with st.expander(f"Context: last result from {st.session_state.last_module}"):
            st.json(st.session_state.last_result)

    question = st.text_area("Your question", placeholder="e.g. Why do we multiply by 1.33 for dry mortar volume?")
    if st.button("Ask", type="primary") and question.strip():
        context = str(st.session_state.last_result) if st.session_state.last_result else ""
        with st.spinner("Thinking..."):
            answer = ask_groq(question, context)
        st.markdown(answer)
