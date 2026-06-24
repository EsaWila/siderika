import streamlit as st
import pickle
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NarkoScan | Sistem Deteksi Risiko",
    page_icon="https://cdn-icons-png.flaticon.com/512/2092/2092249.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── Base ── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #070D1A;
    color: #CBD5E1;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: #0D1526;
    border-right: 1px solid #1E293B;
}
[data-testid="stSidebar"] * { font-family: 'Inter', sans-serif; }

/* ── Main container ── */
.main .block-container {
    padding: 2rem 2.5rem;
    max-width: 1400px;
}

/* ── Header ── */
.page-header {
    display: flex;
    align-items: flex-start;
    gap: 1rem;
    padding: 1.5rem 0 1rem;
    border-bottom: 1px solid #1E293B;
    margin-bottom: 2rem;
}
.page-header .header-icon {
    width: 40px;
    height: 40px;
    flex-shrink: 0;
    opacity: 0.9;
}
.page-header h1 {
    font-size: 1.6rem;
    font-weight: 700;
    color: #F1F5F9;
    margin: 0;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.page-header p {
    font-size: 0.85rem;
    color: #64748B;
    margin: 0.3rem 0 0;
}

/* ── Stat cards ── */
.stat-row {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
}
.stat-card {
    background: #0D1526;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 1.1rem 1.25rem;
    position: relative;
    overflow: hidden;
}
.stat-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}
.stat-card.red::before  { background: #EF4444; }
.stat-card.amber::before { background: #F59E0B; }
.stat-card.green::before { background: #10B981; }

.stat-card .label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.5rem;
}
.stat-card .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 500;
    color: #F1F5F9;
    line-height: 1;
}
.stat-card .sub {
    font-size: 0.78rem;
    color: #475569;
    margin-top: 0.3rem;
}

/* ── Section card ── */
.section-card {
    background: #0D1526;
    border: 1px solid #1E293B;
    border-radius: 8px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.section-title {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #3B82F6;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* ── Result banner ── */
.result-banner {
    border-radius: 6px;
    padding: 1rem 1.25rem;
    margin-top: 1rem;
    border-left: 3px solid;
}
.result-banner.high   { background: rgba(239,68,68,.08);  border-color: #EF4444; }
.result-banner.medium { background: rgba(245,158,11,.08); border-color: #F59E0B; }
.result-banner.low    { background: rgba(16,185,129,.08); border-color: #10B981; }

.result-banner .risk-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 0.4rem;
}
.risk-label.high   { color: #EF4444; }
.risk-label.medium { color: #F59E0B; }
.risk-label.low    { color: #10B981; }

.result-banner .risk-desc {
    font-size: 0.85rem;
    color: #94A3B8;
    line-height: 1.5;
}

/* ── Threat meter ── */
.threat-meter {
    margin-top: 1rem;
    display: flex;
    align-items: center;
    gap: 0.75rem;
}
.meter-bar-bg {
    flex: 1;
    height: 6px;
    background: #1E293B;
    border-radius: 99px;
    overflow: hidden;
}
.meter-bar-fill {
    height: 100%;
    border-radius: 99px;
    transition: width 0.6s ease;
}
.meter-label {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    color: #475569;
    white-space: nowrap;
}

/* ── Textarea & inputs ── */
textarea, .stTextArea textarea {
    background: #111827 !important;
    border: 1px solid #1E293B !important;
    border-radius: 6px !important;
    color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    resize: vertical;
}
textarea:focus, .stTextArea textarea:focus {
    border-color: #3B82F6 !important;
    box-shadow: 0 0 0 2px rgba(59,130,246,.15) !important;
}

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: #1D4ED8 !important;
    border: none !important;
    border-radius: 6px !important;
    color: #fff !important;
    font-weight: 600 !important;
    font-size: 0.8rem !important;
    letter-spacing: 0.04em !important;
    padding: 0.55rem 1.25rem !important;
    transition: background .2s;
}
.stButton > button[kind="primary"]:hover {
    background: #2563EB !important;
}
.stButton > button[kind="secondary"] {
    background: transparent !important;
    border: 1px solid #1E293B !important;
    border-radius: 6px !important;
    color: #94A3B8 !important;
    font-size: 0.8rem !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent;
    border-bottom: 1px solid #1E293B;
    gap: 0;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    background: transparent;
    border: none;
    border-bottom: 2px solid transparent;
    color: #475569;
    font-size: 0.8rem;
    font-weight: 500;
    letter-spacing: 0.03em;
    padding: 0.6rem 1rem;
    margin-bottom: -1px;
}
[data-testid="stTabs"] [aria-selected="true"] {
    background: transparent !important;
    border-bottom-color: #3B82F6 !important;
    color: #F1F5F9 !important;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    background: #111827;
    border: 1px dashed #1E293B;
    border-radius: 6px;
    padding: 1rem;
}

/* ── Selectbox ── */
[data-testid="stSelectbox"] div {
    background: #111827 !important;
    border-color: #1E293B !important;
    color: #CBD5E1 !important;
    border-radius: 6px !important;
}

/* ── Download button ── */
[data-testid="stDownloadButton"] button {
    background: #111827 !important;
    border: 1px solid #1E293B !important;
    color: #94A3B8 !important;
    border-radius: 6px !important;
    font-size: 0.8rem !important;
}

/* ── Dataframe table ── */
[data-testid="stDataFrame"] { border: 1px solid #1E293B; border-radius: 6px; overflow: hidden; }

/* ── Metric ── */
[data-testid="stMetric"] {
    background: transparent !important;
}

/* ── Divider ── */
hr { border-color: #1E293B; margin: 1.5rem 0; }

/* ── Sidebar items ── */
.sidebar-metric {
    background: #111827;
    border: 1px solid #1E293B;
    border-radius: 6px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
}
.sidebar-metric .sm-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #475569;
    margin-bottom: 0.25rem;
}
.sidebar-metric .sm-value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.1rem;
    font-weight: 500;
    color: #10B981;
}
.sidebar-metric .sm-sub {
    font-size: 0.72rem;
    color: #475569;
}
.status-dot {
    display: inline-block;
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #10B981;
    margin-right: 6px;
    animation: pulse-dot 2s infinite;
    vertical-align: middle;
}
@keyframes pulse-dot {
    0%,100% { opacity:1; }
    50% { opacity:.35; }
}
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding: 1rem 0 0.5rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:1rem;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span style="font-size:0.95rem;font-weight:700;color:#F1F5F9;letter-spacing:-0.01em;">NarkoScan</span>
        </div>
        <p style="font-size:0.72rem;color:#475569;line-height:1.5;margin:0;">
            Sistem Deteksi Dini Penyalahgunaan Narkoba berbasis Machine Learning dari data media sosial.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1E293B;margin:0.75rem 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#475569;margin-bottom:0.5rem;">
        Status Sistem
    </p>
    <div class="sidebar-metric">
        <div class="sm-label">Model</div>
        <div class="sm-value" style="font-size:0.9rem;color:#CBD5E1;">SVM + TF-IDF</div>
        <div class="sm-sub">Word & Bigram Features</div>
    </div>
    <div class="sidebar-metric">
        <div class="sm-label">Akurasi</div>
        <div class="sm-value">97.45%</div>
        <div class="sm-sub">Balanced Class Optimized</div>
    </div>
    <div class="sidebar-metric">
        <div class="sm-label">Kondisi</div>
        <div class="sm-value" style="font-size:0.88rem;color:#10B981;">
            <span class="status-dot"></span>Operasional
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1E293B;margin:0.75rem 0;'>", unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:0.68rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#475569;margin-bottom:0.5rem;">
        Kategori Risiko
    </p>
    """, unsafe_allow_html=True)

    for color, label, desc in [
        ("#EF4444", "Risiko Tinggi",  "Konsumsi aktif / transaksi langsung"),
        ("#F59E0B", "Risiko Sedang",  "Pemberitaan hukum / laporan formal"),
        ("#10B981", "Risiko Rendah",  "Kampanye anti-narkoba / edukasi"),
    ]:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:0.6rem;margin-bottom:0.6rem;">
            <div style="width:8px;height:8px;border-radius:50%;background:{color};margin-top:4px;flex-shrink:0;"></div>
            <div>
                <div style="font-size:0.78rem;font-weight:600;color:#CBD5E1;">{label}</div>
                <div style="font-size:0.71rem;color:#475569;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1E293B;margin:0.75rem 0;'>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.68rem;color:#334155;text-align:center;'>Deteksi Dini Risiko Narkoba &copy; 2026</p>", unsafe_allow_html=True)

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <svg class="header-icon" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
    </svg>
    <div>
        <h1>Sistem Deteksi Dini Risiko Penyalahgunaan Narkoba</h1>
        <p>Klasifikasi teks media sosial berbasis Support Vector Machine — identifikasi tingkat risiko secara real-time maupun massal.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# ─── LOAD MODEL ───────────────────────────────────────────────────────────────
@st.cache_resource
def load_model():
    with open('tfidf_vectorizer_narkoba.pkl', 'rb') as f:
        tfidf = pickle.load(f)
    with open('model_svm_narkoba.pkl', 'rb') as f:
        model = pickle.load(f)
    return tfidf, model

try:
    tfidf, model_svm = load_model()
    model_loaded = True
except Exception as e:
    st.markdown(f"""
    <div style="background:rgba(239,68,68,.08);border:1px solid rgba(239,68,68,.25);border-left:3px solid #EF4444;border-radius:6px;padding:0.9rem 1.1rem;margin-bottom:1rem;">
        <div style="font-size:0.75rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#EF4444;margin-bottom:0.25rem;">Gagal Memuat Model</div>
        <div style="font-size:0.82rem;color:#94A3B8;">Pastikan file <code style="background:#1E293B;padding:0.1em 0.4em;border-radius:3px;">tfidf_vectorizer_narkoba.pkl</code> dan <code style="background:#1E293B;padding:0.1em 0.4em;border-radius:3px;">model_svm_narkoba.pkl</code> berada di direktori yang sama. Detail: {e}</div>
    </div>
    """, unsafe_allow_html=True)
    model_loaded = False

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def bersihkan_teks(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

RISK_MAP = {
    'Positif': {
        'label': 'RISIKO TINGGI',
        'class': 'high',
        'color': '#EF4444',
        'fill': 90,
        'desc': 'Indikasi konsumsi aktif, aktivitas penyalahgunaan langsung, atau transaksi narkoba terdeteksi dalam teks.',
        'icon': '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>'
    },
    'Netral': {
        'label': 'RISIKO SEDANG',
        'class': 'medium',
        'color': '#F59E0B',
        'fill': 50,
        'desc': 'Teks berkaitan dengan pemberitaan kasus hukum, razia kepolisian, atau laporan formal terkait narkoba.',
        'icon': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>'
    },
    'Negatif': {
        'label': 'RISIKO RENDAH',
        'class': 'low',
        'color': '#10B981',
        'fill': 12,
        'desc': 'Teks mengandung kampanye anti-narkoba, edukasi masyarakat, atau ajakan rehabilitasi.',
        'icon': '<polyline points="20 6 9 17 4 12"/>'
    },
}

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Analisis Teks Tunggal", "Analisis Massal (CSV)"])

# ══════════════════════════════════════════════════════════
# TAB 1 — SINGLE TEXT
# ══════════════════════════════════════════════════════════
with tab1:
    col_input, col_result = st.columns([1, 1], gap="large")

    with col_input:
        st.markdown("""
        <div class="section-title">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Input Teks
        </div>
        """, unsafe_allow_html=True)

        user_input = st.text_area(
            label="Teks input",
            label_visibility="collapsed",
            placeholder="Ketik atau tempel cuitan / kalimat yang ingin dianalisis...",
            height=140,
            key="tunggal"
        )

        st.markdown("""
        <p style="font-size:0.72rem;color:#334155;margin-top:0.4rem;">
            Sistem akan melakukan preprocessing otomatis sebelum klasifikasi.
        </p>
        """, unsafe_allow_html=True)

        run_btn = st.button("Jalankan Analisis", type="primary", disabled=not model_loaded)

    with col_result:
        st.markdown("""
        <div class="section-title">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            Hasil Klasifikasi
        </div>
        """, unsafe_allow_html=True)

        if run_btn:
            if not user_input.strip():
                st.markdown("""
                <div style="background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.2);border-radius:6px;padding:0.8rem 1rem;font-size:0.82rem;color:#94A3B8;">
                    Masukkan teks sebelum menjalankan analisis.
                </div>
                """, unsafe_allow_html=True)
            else:
                teks_bersih = bersihkan_teks(user_input)
                vektor_uji  = tfidf.transform([teks_bersih])
                prediksi    = model_svm.predict(vektor_uji)[0]
                r = RISK_MAP.get(prediksi, RISK_MAP['Netral'])

                st.markdown(f"""
                <div class="result-banner {r['class']}">
                    <div class="risk-label {r['class']}" style="display:flex;align-items:center;gap:0.5rem;">
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{r['color']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                            {r['icon']}
                        </svg>
                        {r['label']}
                    </div>
                    <div class="risk-desc">{r['desc']}</div>
                </div>

                <div class="threat-meter" style="margin-top:1rem;">
                    <span class="meter-label">INDEKS RISIKO</span>
                    <div class="meter-bar-bg">
                        <div class="meter-bar-fill" style="width:{r['fill']}%;background:{r['color']};"></div>
                    </div>
                    <span class="meter-label" style="color:{r['color']};font-weight:500;">{r['fill']}%</span>
                </div>

                <div style="margin-top:1rem;padding:0.75rem;background:#111827;border-radius:6px;">
                    <div style="font-size:0.68rem;font-weight:600;letter-spacing:0.08em;text-transform:uppercase;color:#334155;margin-bottom:0.35rem;">Teks Setelah Preprocessing</div>
                    <div style="font-family:'JetBrains Mono',monospace;font-size:0.75rem;color:#475569;line-height:1.5;">{teks_bersih if teks_bersih else '—'}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div style="height:180px;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0.6rem;border:1px dashed #1E293B;border-radius:8px;">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1E293B" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <span style="font-size:0.78rem;color:#1E293B;">Hasil analisis akan muncul di sini</span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — BULK CSV
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="section-title">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Upload File CSV
    </div>
    <p style="font-size:0.82rem;color:#475569;margin-bottom:1rem;">
        Analisis ratusan hingga ribuan baris teks sekaligus dari hasil scraping media sosial. Format yang didukung: <code style="background:#1E293B;padding:0.1em 0.4em;border-radius:3px;font-size:0.75rem;">.csv</code>
    </p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)

        st.markdown("""
        <div class="section-title" style="margin-top:1.5rem;">
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/><path d="M3 9h18M3 15h18M9 3v18"/>
            </svg>
            Pratinjau Data
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(
            df_input.head(5),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown(f"""
        <p style="font-size:0.72rem;color:#334155;margin-top:0.5rem;">
            Total baris terdeteksi: <span style="font-family:'JetBrains Mono',monospace;color:#475569;">{len(df_input):,}</span>
        </p>
        """, unsafe_allow_html=True)

        kolom_pilihan = st.selectbox(
            "Kolom teks yang akan dianalisis:",
            df_input.columns,
            help="Pilih kolom yang berisi teks tweet atau kalimat"
        )

        if st.button("Jalankan Analisis Massal", type="primary", disabled=not model_loaded):
            with st.spinner("Model sedang memproses seluruh dataset..."):
                df_input['teks_bersih']    = df_input[kolom_pilihan].apply(bersihkan_teks)
                vektor_massal              = tfidf.transform(df_input['teks_bersih'].fillna(''))
                df_input['Hasil_Sentimen'] = model_svm.predict(vektor_massal)

                def map_status(p):
                    return RISK_MAP.get(p, {}).get('label', 'Tidak Diketahui')
                df_input['Status_Risiko'] = df_input['Hasil_Sentimen'].apply(map_status)

            total  = len(df_input)
            tinggi = len(df_input[df_input['Hasil_Sentimen'] == 'Positif'])
            sedang = len(df_input[df_input['Hasil_Sentimen'] == 'Netral'])
            rendah = len(df_input[df_input['Hasil_Sentimen'] == 'Negatif'])

            # ── Summary cards ──
            st.markdown(f"""
            <div class="section-title" style="margin-top:1.5rem;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
                Ringkasan Distribusi
            </div>
            <div class="stat-row">
                <div class="stat-card red">
                    <div class="label">Risiko Tinggi</div>
                    <div class="value">{tinggi:,}</div>
                    <div class="sub">{tinggi/total*100:.1f}% dari total data</div>
                </div>
                <div class="stat-card amber">
                    <div class="label">Risiko Sedang</div>
                    <div class="value">{sedang:,}</div>
                    <div class="sub">{sedang/total*100:.1f}% dari total data</div>
                </div>
                <div class="stat-card green">
                    <div class="label">Risiko Rendah</div>
                    <div class="value">{rendah:,}</div>
                    <div class="sub">{rendah/total*100:.1f}% dari total data</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Charts ──
            st.markdown("""
            <div class="section-title">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2"/><line x1="8" y1="21" x2="16" y2="21"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                Visualisasi Hasil
            </div>
            """, unsafe_allow_html=True)

            COLORS = {'RISIKO TINGGI': '#EF4444', 'RISIKO SEDANG': '#F59E0B', 'RISIKO RENDAH': '#10B981'}

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
            fig.patch.set_facecolor('#0D1526')

            # Bar chart
            ax1.set_facecolor('#0D1526')
            cats  = ['RISIKO TINGGI', 'RISIKO SEDANG', 'RISIKO RENDAH']
            vals  = [tinggi, sedang, rendah]
            bars  = ax1.bar(cats, vals,
                            color=[COLORS[c] for c in cats],
                            width=0.45, zorder=3,
                            edgecolor='none')
            ax1.set_facecolor('#0D1526')
            ax1.tick_params(colors='#475569', labelsize=8)
            ax1.set_ylabel('Jumlah Data', color='#475569', fontsize=8)
            ax1.set_title('Distribusi Kategori Risiko', color='#CBD5E1', fontsize=9, pad=12, fontweight='600')
            ax1.spines[:].set_color('#1E293B')
            ax1.yaxis.grid(True, color='#1E293B', linewidth=0.5, zorder=0)
            ax1.set_axisbelow(True)
            for bar, val in zip(bars, vals):
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.01,
                         f'{val:,}', ha='center', va='bottom', color='#94A3B8', fontsize=8,
                         fontfamily='monospace')
            ax1.set_xticklabels(cats, fontsize=7.5, color='#475569')

            # Pie chart
            ax2.set_facecolor('#0D1526')
            sizes  = [v for v in vals if v > 0]
            labels = [c for c, v in zip(cats, vals) if v > 0]
            colors = [COLORS[l] for l in labels]
            wedges, texts, autotexts = ax2.pie(
                sizes, labels=None, autopct='%1.1f%%', startangle=140,
                colors=colors, pctdistance=0.78,
                wedgeprops=dict(width=0.55, edgecolor='#0D1526', linewidth=2)
            )
            for at in autotexts:
                at.set_color('#0D1526')
                at.set_fontsize(8)
                at.set_fontweight('600')
            ax2.set_title('Persentase Distribusi', color='#CBD5E1', fontsize=9, pad=12, fontweight='600')
            legend_patches = [mpatches.Patch(color=c, label=l) for l, c in zip(labels, colors)]
            ax2.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.12),
                       ncol=3, frameon=False, fontsize=7.5,
                       labelcolor='#475569')

            plt.tight_layout(pad=2)
            st.pyplot(fig)

            # ── Result table ──
            st.markdown("""
            <div class="section-title" style="margin-top:0.5rem;">
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <path d="M3 9h18M3 15h18M9 3v18"/>
                </svg>
                Data Hasil Klasifikasi
            </div>
            """, unsafe_allow_html=True)

            st.dataframe(
                df_input[[kolom_pilihan, 'Status_Risiko']].rename(
                    columns={kolom_pilihan: 'Teks Asli', 'Status_Risiko': 'Kategori Risiko'}
                ),
                use_container_width=True,
                hide_index=True,
            )

            # ── Export ──
            csv_hasil = df_input.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Unduh Hasil Analisis (.csv)",
                data=csv_hasil,
                file_name="hasil_prediksi_narkoba.csv",
                mime="text/csv",
            )
