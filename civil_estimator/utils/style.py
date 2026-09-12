"""
Visual theme for the app: CSS injection + a reusable 'hero' banner.
Pure presentation — no calculation logic lives here.
"""

CSS = """
<style>
:root {
    --ce-primary: #0B3D91;
    --ce-primary-dark: #082A66;
    --ce-accent: #FF7A00;
    --ce-bg: #F4F6F8;
}

.stApp {
    background-color: var(--ce-bg);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0B3D91 0%, #10254a 100%);
}
[data-testid="stSidebar"] * {
    color: #F4F6F8 !important;
}
[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.2);
}

/* Sidebar buttons: the blanket light-text rule above would otherwise put
   near-white text on the button's default white background (invisible
   until hover). Give sidebar buttons their own explicit, readable colors. */
[data-testid="stSidebar"] .stButton > button {
    background-color: #0b3d91;
    border: 1px solid #c9c9c9;
    color: #ad1313 !important;
}
[data-testid="stSidebar"] .stButton > button:hover,
[data-testid="stSidebar"] .stButton > button:focus,
[data-testid="stSidebar"] .stButton > button:active {
    background-color: #082d6b !important;
    border-color: #082d6b !important;
    color: #ffffff !important;
}

/* Buttons */
.stButton > button {
    border-radius: 8px;
    font-weight: 600;
}
.stButton > button[kind="primary"] {
    background-color: var(--ce-accent);
    border-color: var(--ce-accent);
}
.stButton > button[kind="primary"]:hover {
    background-color: #e06c00;
    border-color: #e06c00;
}

/* Metric cards */
[data-testid="stMetric"] {
    background-color: white;
    border: 1px solid #E2E5E9;
    border-radius: 10px;
    padding: 12px 16px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}

/* Hero banner */
.ce-hero {
    padding: 1.4rem 1.8rem;
    border-radius: 14px;
    background: linear-gradient(120deg, #0B3D91 0%, #1857C4 100%);
    color: white;
    margin-bottom: 1.1rem;
}
.ce-hero h1 {
    margin: 0;
    color: white;
    font-size: 1.7rem;
}
.ce-hero p {
    margin: 0.35rem 0 0 0;
    color: #DCE6FA;
    font-size: 0.95rem;
}
</style>
"""


def inject_css(st):
    """Call once near the top of the app: inject_css(st)."""
    st.markdown(CSS, unsafe_allow_html=True)


def hero_html(title: str, subtitle: str = "") -> str:
    """Returns HTML for a themed page banner. Render with st.markdown(hero_html(...), unsafe_allow_html=True)."""
    sub = f"<p>{subtitle}</p>" if subtitle else ""
    return f'<div class="ce-hero"><h1>{title}</h1>{sub}</div>'
