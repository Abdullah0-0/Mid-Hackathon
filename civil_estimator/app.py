import pandas as pd
import streamlit as st

from utils.calculations import calc_brickwork, calc_plaster, calc_concrete, calc_steel
from utils.data import MORTAR_RATIOS, CONCRETE_RATIOS, WASTAGE_DEFAULTS, STEEL_BAR_SIZES_MM, CURRENCY_SYMBOL
from utils.groq_helper import ask_groq
from utils.style import inject_css, hero_html
from utils.export import results_to_csv_bytes, project_to_csv_bytes

st.set_page_config(page_title="Civil QuantEstimate", page_icon="🏗️", layout="wide")
inject_css(st)

# ---------------- Session state ----------------
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "last_module" not in st.session_state:
    st.session_state.last_module = None
if "page_results" not in st.session_state:
    st.session_state.page_results = {}  # per-module last computed results, so they survive reruns
if "project" not in st.session_state:
    st.session_state.project = []  # the running BOQ / project cart
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

MODULES = [
    "🏠 Home",
    "🧱 Brickwork",
    "🪣 Plaster",
    "🏗️ Concrete / RCC",
    "🔩 Steel / BBS",
    "📋 Project / BOQ",
    "🤖 AI Assistant",
]
if "nav_page" not in st.session_state:
    st.session_state.nav_page = MODULES[0]


def _set_nav(page_name: str):
    """Used as an on_click callback so the sidebar radio updates in a single
    click instead of needing a second rerun to catch up."""
    st.session_state.nav_page = page_name


# ---------------- Shared helpers ----------------
def show_results(title, results: dict):
    st.subheader(title)
    cols = st.columns(4)
    for i, (k, v) in enumerate(results.items()):
        cols[i % 4].metric(k, v)
    st.session_state.last_result = results
    st.session_state.last_module = title


def material_chart(labels_values: dict, y_title="Volume (m³)"):
    """Small bar chart comparing quantities that share the same unit."""
    df = pd.DataFrame({"Material": list(labels_values.keys()), y_title: list(labels_values.values())})
    df = df.set_index("Material")
    st.bar_chart(df)


def cost_inputs(module_key: str, fields: list):
    """
    Renders an optional expander of unit-rate inputs (defaults to 0 = skipped).
    fields: list of (rate_key, label) tuples.
    Returns a dict {rate_key: value}.
    """
    rates = {}
    with st.expander("💰 Optional — add unit rates for a rough cost estimate"):
        st.caption("Leave a rate at 0 to skip it. Nothing here assumes prices for you — enter your own local rates.")
        cols = st.columns(len(fields))
        for col, (rate_key, label) in zip(cols, fields):
            rates[rate_key] = col.number_input(label, min_value=0.0, value=0.0, step=1.0, key=f"rate_{module_key}_{rate_key}")
    return rates


def apply_cost(results: dict, rates: dict, mapping: list):
    """
    mapping: list of (rate_key, result_key_to_multiply, cost_line_label).
    Returns a NEW dict (results + any cost lines), original results dict is untouched.
    """
    out = dict(results)
    total = 0.0
    added = False
    for rate_key, result_key, cost_label in mapping:
        rate = rates.get(rate_key, 0)
        if rate and result_key in results:
            cost = results[result_key] * rate
            out[cost_label] = round(cost, 2)
            total += cost
            added = True
    if added:
        out[f"Estimated Total Cost ({CURRENCY_SYMBOL})"] = round(total, 2)
    return out


def render_result_actions(module_title: str, label: str, results: dict):
    c1, c2 = st.columns(2)
    if c1.button("➕ Add to Project", key=f"add_{module_title}"):
        st.session_state.project.append({
            "module": module_title,
            "label": label,
            "results": results,
        })
        st.toast(f"Added to project (#{len(st.session_state.project)})", icon="✅")
    csv_bytes = results_to_csv_bytes(module_title, label, results)
    c2.download_button(
        "⬇️ Download CSV",
        data=csv_bytes,
        file_name=f"{module_title.lower().replace(' ', '_').replace('/', '')}.csv",
        mime="text/csv",
        key=f"dl_{module_title}",
    )


# ---------------- Sidebar navigation ----------------
st.sidebar.title("🏗️ Civil QuantEstimate")
st.sidebar.caption("AI-assisted construction quantity takeoff")

# key="nav_page" lets Streamlit manage this widget's state natively — no
# manually-recomputed `index` here, which is what was causing the "click
# twice to switch page" lag.
page = st.sidebar.radio("Select a module", MODULES, key="nav_page")

# ---------------- Home ----------------
if page == "🏠 Home":
    st.markdown(
        hero_html(
            "Civil QuantEstimate",
            "AI-assisted quantity takeoff for civil engineering students, site engineers, and contractors.",
        ),
        unsafe_allow_html=True,
    )

    c1, c2, c3, c4 = st.columns(4)
    for col, (icon, text) in zip(
        [c1, c2, c3, c4],
        [
            ("🧮", "4 calculators — Brickwork, Plaster, Concrete, Steel"),
            ("💰", "Optional cost estimate using your own rates"),
            ("📋", "Build a project BOQ and export it as CSV"),
            ("🤖", "Ask the AI Assistant about any formula or result"),
        ],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"### {icon}")
                st.write(text)

    st.markdown("### How it works")
    s1, s2, s3 = st.columns(3)
    for col, (n, text) in zip(
        [s1, s2, s3],
        [
            ("1", "Pick a module from the sidebar and enter your dimensions."),
            ("2", "Get instant quantities — formulas stay visible so results can be hand-checked."),
            ("3", "Add results to your Project/BOQ, and export everything as one CSV."),
        ],
    ):
        with col:
            with st.container(border=True):
                st.markdown(f"**Step {n}**")
                st.write(text)

    st.markdown("### Jump to a module")
    m1, m2, m3, m4 = st.columns(4)
    for col, name in zip([m1, m2, m3, m4], ["🧱 Brickwork", "🪣 Plaster", "🏗️ Concrete / RCC", "🔩 Steel / BBS"]):
        with col:
            st.button(
                f"Open {name.split(' ', 1)[1]} →",
                key=f"home_{name}",
                use_container_width=True,
                on_click=_set_nav,
                args=(name,),
            )

    st.info("Current version calculates **quantities** with an **optional** cost estimate (cost is a future/enhanced phase).")

# ---------------- Brickwork ----------------
elif page == "🧱 Brickwork":
    st.markdown(hero_html("Brickwork / Masonry Calculator"), unsafe_allow_html=True)
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

    rates = cost_inputs("brick", [
        ("cement", f"Cement rate ({CURRENCY_SYMBOL}/bag)"),
        ("sand", f"Sand rate ({CURRENCY_SYMBOL}/cft)"),
        ("brick", f"Brick rate ({CURRENCY_SYMBOL}/piece)"),
    ])

    if st.button("Calculate Brickwork", type="primary"):
        results = calc_brickwork(length, height, thickness, quantity, mortar_ratio, wastage, opening_area)
        results = apply_cost(results, rates, [
            ("cement", "Cement Bags (50kg)", f"Cement Cost ({CURRENCY_SYMBOL})"),
            ("sand", "Sand Volume (cft)", f"Sand Cost ({CURRENCY_SYMBOL})"),
            ("brick", "Bricks Required (nos)", f"Brick Cost ({CURRENCY_SYMBOL})"),
        ])
        label = f"{length}m × {height}m × {thickness}m wall, ×{quantity}, mortar {mortar_ratio}"
        st.session_state.page_results["brickwork"] = (results, label)

    if "brickwork" in st.session_state.page_results:
        results, label = st.session_state.page_results["brickwork"]
        show_results("Brickwork Results", results)
        material_chart({"Cement": results["Cement Volume (m³)"], "Sand": results["Sand Volume (m³)"]})
        render_result_actions("Brickwork Results", label, results)

# ---------------- Plaster ----------------
elif page == "🪣 Plaster":
    st.markdown(hero_html("Plaster Calculator"), unsafe_allow_html=True)
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

    rates = cost_inputs("plaster", [
        ("cement", f"Cement rate ({CURRENCY_SYMBOL}/bag)"),
        ("sand", f"Sand rate ({CURRENCY_SYMBOL}/cft)"),
    ])

    if st.button("Calculate Plaster", type="primary"):
        results = calc_plaster(length, height, quantity, thickness_mm, mortar_ratio, wastage, opening_area)
        results = apply_cost(results, rates, [
            ("cement", "Cement Bags (50kg)", f"Cement Cost ({CURRENCY_SYMBOL})"),
            ("sand", "Sand Volume (cft)", f"Sand Cost ({CURRENCY_SYMBOL})"),
        ])
        label = f"{length}m × {height}m, ×{quantity}, {thickness_mm}mm, mortar {mortar_ratio}"
        st.session_state.page_results["plaster"] = (results, label)

    if "plaster" in st.session_state.page_results:
        results, label = st.session_state.page_results["plaster"]
        show_results("Plaster Results", results)
        material_chart({"Cement": results["Cement Volume (m³)"], "Sand": results["Sand Volume (m³)"]})
        render_result_actions("Plaster Results", label, results)

# ---------------- Concrete ----------------
elif page == "🏗️ Concrete / RCC":
    st.markdown(hero_html("Concrete / RCC Calculator"), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        length = st.number_input("Length (m)", min_value=0.0, value=5.0, step=0.1)
        width = st.number_input("Width (m)", min_value=0.0, value=0.3, step=0.05)
        thickness = st.number_input("Thickness (m)", min_value=0.0, value=0.15, step=0.01)
    with c2:
        quantity = st.number_input("Quantity (no. of elements)", min_value=1, value=1, step=1)
        mix_ratio = st.selectbox("Mix Ratio", list(CONCRETE_RATIOS.keys()), index=1)
        wastage = st.number_input("Wastage %", min_value=0.0, value=float(WASTAGE_DEFAULTS["concrete"]))

    rates = cost_inputs("concrete", [
        ("cement", f"Cement rate ({CURRENCY_SYMBOL}/bag)"),
        ("sand", f"Sand rate ({CURRENCY_SYMBOL}/cft)"),
        ("aggregate", f"Aggregate rate ({CURRENCY_SYMBOL}/cft)"),
    ])

    if st.button("Calculate Concrete", type="primary"):
        results = calc_concrete(length, width, thickness, quantity, mix_ratio, wastage)
        results = apply_cost(results, rates, [
            ("cement", "Cement Bags (50kg)", f"Cement Cost ({CURRENCY_SYMBOL})"),
            ("sand", "Sand Volume (cft)", f"Sand Cost ({CURRENCY_SYMBOL})"),
            ("aggregate", "Aggregate Volume (cft)", f"Aggregate Cost ({CURRENCY_SYMBOL})"),
        ])
        label = f"{length}m × {width}m × {thickness}m, ×{quantity}, mix {mix_ratio}"
        st.session_state.page_results["concrete"] = (results, label)

    if "concrete" in st.session_state.page_results:
        results, label = st.session_state.page_results["concrete"]
        show_results("Concrete / RCC Results", results)
        material_chart({
            "Cement": results["Cement Volume (m³)"],
            "Sand": results["Sand Volume (m³)"],
            "Aggregate": results["Aggregate Volume (m³)"],
        })
        render_result_actions("Concrete / RCC Results", label, results)

# ---------------- Steel ----------------
elif page == "🔩 Steel / BBS":
    st.markdown(hero_html("Steel / Bar Bending Schedule Calculator"), unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        bar_dia = st.selectbox("Bar Diameter (mm)", STEEL_BAR_SIZES_MM, index=3)
        bar_length = st.number_input("Bar Length (m)", min_value=0.0, value=6.0, step=0.1)
    with c2:
        no_of_bars = st.number_input("Number of Bars", min_value=1, value=10, step=1)
        wastage = st.number_input("Wastage %", min_value=0.0, value=float(WASTAGE_DEFAULTS["steel"]))

    rates = cost_inputs("steel", [
        ("steel", f"Steel rate ({CURRENCY_SYMBOL}/kg)"),
    ])

    if st.button("Calculate Steel", type="primary"):
        results = calc_steel(bar_dia, bar_length, no_of_bars, wastage)
        results = apply_cost(results, rates, [
            ("steel", "Total Steel Weight (kg)", f"Steel Cost ({CURRENCY_SYMBOL})"),
        ])
        label = f"{bar_dia}mm × {bar_length}m, ×{no_of_bars} bars"
        st.session_state.page_results["steel"] = (results, label)

    if "steel" in st.session_state.page_results:
        results, label = st.session_state.page_results["steel"]
        show_results("Steel / BBS Results", results)
        render_result_actions("Steel / BBS Results", label, results)

# ---------------- Project / BOQ ----------------
elif page == "📋 Project / BOQ":
    st.markdown(hero_html("Project / BOQ Summary", "Everything you've added from the calculators, in one place."), unsafe_allow_html=True)

    if not st.session_state.project:
        st.info("No items yet. Calculate something in a module, then click **➕ Add to Project**.")
    else:
        remove_at = None
        for i, item in enumerate(st.session_state.project, start=1):
            with st.container(border=True):
                c1, c2 = st.columns([6, 1])
                c1.markdown(f"**#{i} · {item['module']}**  \n{item['label']}")
                if c2.button("🗑️ Remove", key=f"del_{i}"):
                    remove_at = i - 1
                with st.expander("Details"):
                    for k, v in item["results"].items():
                        st.write(f"**{k}:** {v}")
        if remove_at is not None:
            st.session_state.project.pop(remove_at)
            st.rerun()

        st.divider()
        st.subheader("Grand Totals")
        totals = {}
        for item in st.session_state.project:
            for k, v in item["results"].items():
                if isinstance(v, (int, float)):
                    totals[k] = totals.get(k, 0) + v
        cols = st.columns(3)
        for i, (k, v) in enumerate(totals.items()):
            cols[i % 3].metric(k, round(v, 2))

        st.divider()
        colA, colB = st.columns(2)
        csv_bytes = project_to_csv_bytes(st.session_state.project)
        colA.download_button("⬇️ Download Full BOQ (CSV)", data=csv_bytes, file_name="project_boq.csv", mime="text/csv")
        if colB.button("🗑️ Clear Project"):
            st.session_state.project = []
            st.rerun()

# ---------------- AI Assistant ----------------
elif page == "🤖 AI Assistant":
    st.markdown(hero_html("AI Assistant (Groq)", "Ask about formulas, mix ratios, or your last calculated result."), unsafe_allow_html=True)

    if st.session_state.last_result:
        with st.expander(f"📎 Context available: last result from {st.session_state.last_module}"):
            st.json(st.session_state.last_result)

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    question = st.chat_input("e.g. Why do we multiply by 1.33 for dry mortar volume?")
    if question:
        st.session_state.chat_history.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)
        context = str(st.session_state.last_result) if st.session_state.last_result else ""
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                answer = ask_groq(question, context)
            st.markdown(answer)
        st.session_state.chat_history.append({"role": "assistant", "content": answer})

    if st.session_state.chat_history and st.button("🗑️ Clear chat"):
        st.session_state.chat_history = []
        st.rerun()

# ---------------- Sidebar footer ----------------
# Rendered last (after every page branch above) so it reflects any
# add/remove that happened earlier in THIS SAME run — otherwise it would
# lag one run behind and only update after a second interaction.
st.sidebar.divider()
n_items = len(st.session_state.project)
st.sidebar.caption(f"📋 Project items: **{n_items}**")
if n_items and st.sidebar.button("Clear project", key="sidebar_clear"):
    st.session_state.project = []
    st.rerun()
st.sidebar.divider()
st.sidebar.caption("Quantities only — cost fields are optional and use rates you enter yourself.")
