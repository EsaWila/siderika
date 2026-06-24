import streamlit as st
import pickle
import re
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# ─── PAGE CONFIG ──────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="NarkoScan | Deteksi Risiko Narkoba",
    page_icon="https://cdn-icons-png.flaticon.com/512/2092/2092249.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── GLOBAL CSS ───────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #070D1A;
    color: #CBD5E1;
}
[data-testid="stSidebar"] {
    background: #0D1526;
    border-right: 1px solid #1E293B;
}
.main .block-container { padding: 2rem 2.5rem; max-width: 1400px; }

/* ── Page header ── */
.page-header {
    display: flex; align-items: flex-start; gap: 1rem;
    padding: 1.25rem 0 1rem; border-bottom: 1px solid #1E293B; margin-bottom: 2rem;
}
.page-header h1 { font-size: 1.5rem; font-weight: 700; color: #F1F5F9; margin: 0; letter-spacing: -0.02em; line-height: 1.2; }
.page-header p  { font-size: 0.82rem; color: #64748B; margin: 0.3rem 0 0; }

/* ── Section title ── */
.section-title {
    font-size: 0.7rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase;
    color: #3B82F6; margin-bottom: 0.85rem; display: flex; align-items: center; gap: 0.45rem;
}

/* ── Stat cards ── */
.stat-row { display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 1.5rem; }
.stat-card {
    background: #0D1526; border: 1px solid #1E293B; border-radius: 8px;
    padding: 1rem 1.2rem; position: relative; overflow: hidden;
}
.stat-card::before { content:''; position:absolute; top:0; left:0; right:0; height:2px; }
.stat-card.red::before   { background: #EF4444; }
.stat-card.amber::before { background: #F59E0B; }
.stat-card.green::before { background: #10B981; }
.stat-card .label { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #475569; margin-bottom: 0.4rem; }
.stat-card .value { font-family: 'JetBrains Mono', monospace; font-size: 1.9rem; font-weight: 500; color: #F1F5F9; line-height: 1; }
.stat-card .sub   { font-size: 0.75rem; color: #475569; margin-top: 0.3rem; }

/* ── Result banner ── */
.result-banner { border-radius: 6px; padding: 1rem 1.2rem; margin-top: 0.75rem; border-left: 3px solid; }
.result-banner.high   { background: rgba(239,68,68,.07);  border-color: #EF4444; }
.result-banner.medium { background: rgba(245,158,11,.07); border-color: #F59E0B; }
.result-banner.low    { background: rgba(16,185,129,.07); border-color: #10B981; }

.risk-label { font-family: 'JetBrains Mono', monospace; font-size: 0.72rem; font-weight: 500; letter-spacing: 0.12em; text-transform: uppercase; margin-bottom: 0.4rem; display: flex; align-items: center; gap: 0.45rem; }
.risk-label.high   { color: #EF4444; }
.risk-label.medium { color: #F59E0B; }
.risk-label.low    { color: #10B981; }
.risk-desc { font-size: 0.83rem; color: #94A3B8; line-height: 1.55; margin-top: 0.3rem; }

/* ── Threat meter ── */
.threat-meter { margin-top: 0.9rem; display: flex; align-items: center; gap: 0.75rem; }
.meter-bar-bg { flex: 1; height: 5px; background: #1E293B; border-radius: 99px; overflow: hidden; }
.meter-bar-fill { height: 100%; border-radius: 99px; }
.meter-label { font-family: 'JetBrains Mono', monospace; font-size: 0.68rem; color: #475569; white-space: nowrap; }

/* ── Info grid (detail box) ── */
.info-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 0.5rem 1rem;
    background: #111827; border-radius: 6px; padding: 0.85rem 1rem; margin-top: 0.75rem;
}
.info-item .info-key   { font-size: 0.67rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #334155; margin-bottom: 0.15rem; }
.info-item .info-val   { font-family: 'JetBrains Mono', monospace; font-size: 0.78rem; color: #64748B; }
.info-item.full        { grid-column: 1 / -1; }

/* ── Preprocessed text box ── */
.preproc-box {
    background: #111827; border-radius: 6px; padding: 0.75rem 1rem; margin-top: 0.75rem;
}
.preproc-box .box-label { font-size: 0.67rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #334155; margin-bottom: 0.35rem; }
.preproc-box .box-text  { font-family: 'JetBrains Mono', monospace; font-size: 0.76rem; color: #475569; line-height: 1.55; word-break: break-all; }

/* ── Badge ── */
.badge { display: inline-block; padding: 0.2em 0.6em; border-radius: 4px; font-size: 0.7rem; font-weight: 600; letter-spacing: 0.05em; font-family: 'JetBrains Mono', monospace; }
.badge.high   { background: rgba(239,68,68,.15); color: #EF4444; }
.badge.medium { background: rgba(245,158,11,.15); color: #F59E0B; }
.badge.low    { background: rgba(16,185,129,.15); color: #10B981; }

/* ── Error banner ── */
.error-banner { background: rgba(239,68,68,.07); border: 1px solid rgba(239,68,68,.22); border-left: 3px solid #EF4444; border-radius: 6px; padding: 0.85rem 1rem; margin-bottom: 1rem; }
.error-banner .err-title { font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase; color: #EF4444; margin-bottom: 0.25rem; }
.error-banner .err-body  { font-size: 0.82rem; color: #94A3B8; }

/* ── Warning (empty input) ── */
.warn-box { background: rgba(245,158,11,.06); border: 1px solid rgba(245,158,11,.18); border-radius: 6px; padding: 0.75rem 1rem; font-size: 0.82rem; color: #94A3B8; }

/* ── Empty state ── */
.empty-state { height: 200px; display: flex; flex-direction: column; align-items: center; justify-content: center; gap: 0.6rem; border: 1px dashed #1E293B; border-radius: 8px; }
.empty-state span { font-size: 0.78rem; color: #1E293B; }

/* ── Inputs / selects ── */
textarea, .stTextArea textarea {
    background: #111827 !important; border: 1px solid #1E293B !important;
    border-radius: 6px !important; color: #CBD5E1 !important;
    font-family: 'Inter', sans-serif !important; font-size: 0.875rem !important;
}
textarea:focus, .stTextArea textarea:focus { border-color: #3B82F6 !important; box-shadow: 0 0 0 2px rgba(59,130,246,.12) !important; }
[data-testid="stSelectbox"] > div > div { background: #111827 !important; border-color: #1E293B !important; border-radius: 6px !important; color: #CBD5E1 !important; }
[data-testid="stFileUploader"] { background: #111827; border: 1px dashed #1E293B; border-radius: 6px; padding: 0.75rem; }

/* ── Buttons ── */
.stButton > button[kind="primary"] {
    background: #1D4ED8 !important; border: none !important; border-radius: 6px !important;
    color: #fff !important; font-weight: 600 !important; font-size: 0.8rem !important;
    letter-spacing: 0.04em !important; padding: 0.52rem 1.2rem !important;
}
.stButton > button[kind="primary"]:hover { background: #2563EB !important; }
.stButton > button[kind="secondary"] {
    background: transparent !important; border: 1px solid #1E293B !important;
    border-radius: 6px !important; color: #94A3B8 !important; font-size: 0.8rem !important;
}
[data-testid="stDownloadButton"] button {
    background: #111827 !important; border: 1px solid #1E293B !important;
    color: #94A3B8 !important; border-radius: 6px !important; font-size: 0.8rem !important;
}

/* ── Tabs ── */
[data-testid="stTabs"] [data-baseweb="tab-list"] { background: transparent; border-bottom: 1px solid #1E293B; gap: 0; }
[data-testid="stTabs"] [data-baseweb="tab"] { background: transparent; border: none; border-bottom: 2px solid transparent; color: #475569; font-size: 0.8rem; font-weight: 500; padding: 0.6rem 1rem; margin-bottom: -1px; }
[data-testid="stTabs"] [aria-selected="true"] { background: transparent !important; border-bottom-color: #3B82F6 !important; color: #F1F5F9 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] { border: 1px solid #1E293B; border-radius: 6px; overflow: hidden; }

/* ── Sidebar items ── */
.sidebar-metric { background: #111827; border: 1px solid #1E293B; border-radius: 6px; padding: 0.7rem 1rem; margin-bottom: 0.65rem; }
.sidebar-metric .sm-label { font-size: 0.67rem; font-weight: 600; letter-spacing: 0.1em; text-transform: uppercase; color: #475569; margin-bottom: 0.2rem; }
.sidebar-metric .sm-value { font-family: 'JetBrains Mono', monospace; font-size: 1rem; font-weight: 500; color: #10B981; }
.sidebar-metric .sm-sub   { font-size: 0.7rem; color: #475569; }
.status-dot { display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: #10B981; margin-right: 5px; animation: pulse-dot 2s infinite; vertical-align: middle; }
@keyframes pulse-dot { 0%,100%{opacity:1} 50%{opacity:.3} }

hr { border-color: #1E293B; margin: 1.2rem 0; }
</style>
""", unsafe_allow_html=True)

# ─── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="padding:1rem 0 0.5rem;">
        <div style="display:flex;align-items:center;gap:0.6rem;margin-bottom:0.75rem;">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
            </svg>
            <span style="font-size:0.95rem;font-weight:700;color:#F1F5F9;letter-spacing:-0.01em;">NarkoScan</span>
        </div>
        <p style="font-size:0.72rem;color:#475569;line-height:1.55;margin:0;">
            Sistem deteksi dini penyalahgunaan narkoba berbasis SVM dari data Twitter/X Indonesia.
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:0.67rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#475569;margin-bottom:0.5rem;">Status Sistem</p>
    <div class="sidebar-metric">
        <div class="sm-label">Model</div>
        <div class="sm-value" style="font-size:0.88rem;color:#CBD5E1;">SVM + TF-IDF</div>
        <div class="sm-sub">Word & Bigram Features, Balanced Class</div>
    </div>
    <div class="sidebar-metric">
        <div class="sm-label">Akurasi</div>
        <div class="sm-value">97.45%</div>
        <div class="sm-sub">Optimized on 1.372 tweet</div>
    </div>
    <div class="sidebar-metric">
        <div class="sm-label">Kondisi</div>
        <div class="sm-value" style="font-size:0.85rem;color:#10B981;">
            <span class="status-dot"></span>Operasional
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("""
    <p style="font-size:0.67rem;font-weight:600;letter-spacing:0.1em;text-transform:uppercase;color:#475569;margin-bottom:0.5rem;">Kategori Risiko</p>
    """, unsafe_allow_html=True)
    for color, label, desc in [
        ("#EF4444", "Risiko Tinggi",  "Konsumsi aktif / transaksi langsung"),
        ("#F59E0B", "Risiko Sedang",  "Pemberitaan hukum / laporan resmi"),
        ("#10B981", "Risiko Rendah",  "Kampanye anti-narkoba / edukasi"),
    ]:
        st.markdown(f"""
        <div style="display:flex;align-items:flex-start;gap:0.55rem;margin-bottom:0.55rem;">
            <div style="width:7px;height:7px;border-radius:50%;background:{color};margin-top:4px;flex-shrink:0;"></div>
            <div>
                <div style="font-size:0.77rem;font-weight:600;color:#CBD5E1;">{label}</div>
                <div style="font-size:0.7rem;color:#475569;">{desc}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<p style='font-size:0.67rem;color:#1E293B;text-align:center;'>Deteksi Dini Risiko Narkoba &copy; 2026</p>", unsafe_allow_html=True)

# ─── PAGE HEADER ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="#3B82F6" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" style="flex-shrink:0;margin-top:2px;">
        <circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/>
        <line x1="11" y1="8" x2="11" y2="14"/><line x1="8" y1="11" x2="14" y2="11"/>
    </svg>
    <div>
        <h1>Sistem Deteksi Dini Risiko Penyalahgunaan Narkoba</h1>
        <p>Klasifikasi teks Twitter/X berbasis Support Vector Machine — analisis tunggal atau massal dari file CSV hasil scraping.</p>
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

model_loaded = False
try:
    tfidf, model_svm = load_model()
    model_loaded = True
except Exception as e:
    st.markdown(f"""
    <div class="error-banner">
        <div class="err-title">Gagal Memuat Model</div>
        <div class="err-body">
            Pastikan <code style="background:#1E293B;padding:.1em .35em;border-radius:3px;">tfidf_vectorizer_narkoba.pkl</code>
            dan <code style="background:#1E293B;padding:.1em .35em;border-radius:3px;">model_svm_narkoba.pkl</code>
            ada di direktori yang sama dengan file ini.<br>
            <span style="color:#334155;">Detail: {e}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ─── HELPERS ──────────────────────────────────────────────────────────────────
def bersihkan_teks(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text)
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def format_tanggal(raw):
    try:
        dt = datetime.strptime(raw, "%a %b %d %H:%M:%S +0000 %Y")
        return dt.strftime("%d %b %Y, %H:%M UTC")
    except:
        return raw

RISK = {
    'Positif': {
        'label': 'RISIKO TINGGI', 'class': 'high', 'color': '#EF4444', 'fill': 90,
        'badge': 'Risiko Tinggi',
        'desc': 'Teks mengandung indikasi konsumsi aktif, aktivitas penyalahgunaan langsung, atau transaksi narkoba.',
        'icon_path': '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/>',
    },
    'Netral': {
        'label': 'RISIKO SEDANG', 'class': 'medium', 'color': '#F59E0B', 'fill': 50,
        'badge': 'Risiko Sedang',
        'desc': 'Teks berkaitan dengan pemberitaan kasus hukum, razia kepolisian, atau laporan formal terkait narkoba.',
        'icon_path': '<circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/>',
    },
    'Negatif': {
        'label': 'RISIKO RENDAH', 'class': 'low', 'color': '#10B981', 'fill': 12,
        'badge': 'Risiko Rendah',
        'desc': 'Teks mengandung kampanye anti-narkoba, edukasi pencegahan, atau ajakan rehabilitasi.',
        'icon_path': '<polyline points="20 6 9 17 4 12"/>',
    },
}

# ─── TABS ─────────────────────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["Analisis Teks Tunggal", "Analisis Massal (CSV)"])

# ══════════════════════════════════════════════════════════
# TAB 1 — SINGLE TEXT
# ══════════════════════════════════════════════════════════
with tab1:
    col_in, col_out = st.columns([1, 1], gap="large")

    with col_in:
        st.markdown("""
        <div class="section-title">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/>
                <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/>
            </svg>
            Masukkan Teks
        </div>
        """, unsafe_allow_html=True)

        user_input = st.text_area(
            label="teks", label_visibility="collapsed",
            placeholder="Tempel atau ketik teks tweet yang ingin dianalisis...\n\nContoh: satresnarkoba berhasil mengungkap kasus peredaran sabu di wilayah tersebut",
            height=150, key="tunggal"
        )

    with col_out:
        st.markdown("""
        <div class="section-title">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
            </svg>
            Hasil Klasifikasi
        </div>
        """, unsafe_allow_html=True)

        if run:
            if not user_input.strip():
                st.markdown('<div class="warn-box">Masukkan teks terlebih dahulu sebelum menjalankan analisis.</div>', unsafe_allow_html=True)
            else:
                teks_bersih = bersihkan_teks(user_input)
                if not teks_bersih:
                    st.markdown('<div class="warn-box">Teks tidak mengandung karakter yang dapat diproses setelah preprocessing.</div>', unsafe_allow_html=True)
                else:
                    prediksi = model_svm.predict(tfidf.transform([teks_bersih]))[0]
                    r = RISK.get(prediksi, RISK['Netral'])

                    # ── Result banner ──
                    st.markdown(f"""
                    <div class="result-banner {r['class']}">
                        <div class="risk-label {r['class']}">
                            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="{r['color']}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">{r['icon_path']}</svg>
                            {r['label']}
                        </div>
                        <div class="risk-desc">{r['desc']}</div>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Threat meter ──
                    st.markdown(f"""
                    <div class="threat-meter">
                        <span class="meter-label">INDEKS RISIKO</span>
                        <div class="meter-bar-bg">
                            <div class="meter-bar-fill" style="width:{r['fill']}%;background:{r['color']};"></div>
                        </div>
                        <span class="meter-label" style="color:{r['color']};font-weight:600;">{r['fill']}%</span>
                    </div>
                    """, unsafe_allow_html=True)

                    # ── Metadata grid ──
                    tgl_fmt  = format_tanggal(meta_tanggal) if meta_tanggal.strip() else "—"
                    url_html = f'<a href="{meta_url}" target="_blank" style="color:#3B82F6;font-size:0.75rem;text-decoration:none;">Buka Tweet</a>' if meta_url.strip() else "—"

                    st.markdown(f"""
                    <div class="info-grid">
                        <div class="info-item">
                            <div class="info-key">Tanggal Tweet</div>
                            <div class="info-val">{tgl_fmt}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-key">Label Prediksi</div>
                            <div class="info-val"><span class="badge {r['class']}">{r['badge']}</span></div>
                        </div>
                        <div class="info-item">
                            <div class="info-key">Like / Retweet / Reply</div>
                            <div class="info-val">{meta_like:,} &nbsp;/&nbsp; {meta_rt:,} &nbsp;/&nbsp; {meta_reply:,}</div>
                        </div>
                        <div class="info-item">
                            <div class="info-key">Sumber</div>
                            <div class="info-val">{url_html}</div>
                        </div>
                        <div class="info-item full">
                            <div class="info-key">Teks Setelah Preprocessing</div>
                            <div class="info-val" style="word-break:break-all;line-height:1.55;">{teks_bersih}</div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="empty-state">
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#1E293B" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
                </svg>
                <span>Hasil analisis akan muncul di sini</span>
            </div>
            """, unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════
# TAB 2 — BULK CSV
# ══════════════════════════════════════════════════════════
with tab2:
    st.markdown("""
    <div class="section-title">
        <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
            <polyline points="17 8 12 3 7 8"/>
            <line x1="12" y1="3" x2="12" y2="15"/>
        </svg>
        Upload File CSV
    </div>
    <p style="font-size:0.82rem;color:#475569;margin-bottom:1rem;">
        Upload file CSV hasil scraping Twitter/X. Sistem akan otomatis mendeteksi kolom teks dan mengklasifikasikan setiap baris.
        Format kolom yang dikenali: <code style="background:#1E293B;padding:.1em .35em;border-radius:3px;font-size:0.74rem;">full_text</code>,
        <code style="background:#1E293B;padding:.1em .35em;border-radius:3px;font-size:0.74rem;">text</code>, atau pilih manual.
    </p>
    """, unsafe_allow_html=True)

    uploaded_file = st.file_uploader("Upload CSV", type=["csv"], label_visibility="collapsed")

    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)

        # ── Preview ──
        st.markdown("""
        <div class="section-title" style="margin-top:1.25rem;">
            <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <rect x="3" y="3" width="18" height="18" rx="2"/>
                <path d="M3 9h18M3 15h18M9 3v18"/>
            </svg>
            Pratinjau Data
        </div>
        """, unsafe_allow_html=True)

        st.dataframe(df.head(5), use_container_width=True, hide_index=True)
        st.markdown(f"<p style='font-size:0.71rem;color:#334155;margin-top:0.4rem;'>Total baris: <span style='font-family:JetBrains Mono,monospace;color:#475569;'>{len(df):,}</span> &nbsp;|&nbsp; Total kolom: <span style='font-family:JetBrains Mono,monospace;color:#475569;'>{len(df.columns)}</span></p>", unsafe_allow_html=True)

        # Auto-detect text column
        auto_col = next((c for c in ['full_text', 'text', 'tweet', 'content'] if c in df.columns), df.columns[0])
        kolom = st.selectbox("Pilih kolom teks yang akan dianalisis:", df.columns, index=list(df.columns).index(auto_col))

        if st.button("Jalankan Analisis Massal", type="primary", disabled=not model_loaded):
            with st.spinner("Model SVM sedang mengklasifikasikan seluruh data..."):
                df['teks_bersih']    = df[kolom].apply(bersihkan_teks)
                preds                = model_svm.predict(tfidf.transform(df['teks_bersih'].fillna('')))
                df['Prediksi']       = preds
                df['Kategori Risiko'] = df['Prediksi'].map(lambda p: RISK.get(p, {}).get('badge', '—'))

            total  = len(df)
            tinggi = (df['Prediksi'] == 'Positif').sum()
            sedang = (df['Prediksi'] == 'Netral').sum()
            rendah = (df['Prediksi'] == 'Negatif').sum()

            # ── Summary cards ──
            st.markdown(f"""
            <div class="section-title" style="margin-top:1.5rem;">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/>
                    <line x1="6" y1="20" x2="6" y2="14"/>
                </svg>
                Ringkasan Distribusi
            </div>
            <div class="stat-row">
                <div class="stat-card red">
                    <div class="label">Risiko Tinggi</div>
                    <div class="value">{tinggi:,}</div>
                    <div class="sub">{tinggi/total*100:.1f}% dari {total:,} data</div>
                </div>
                <div class="stat-card amber">
                    <div class="label">Risiko Sedang</div>
                    <div class="value">{sedang:,}</div>
                    <div class="sub">{sedang/total*100:.1f}% dari {total:,} data</div>
                </div>
                <div class="stat-card green">
                    <div class="label">Risiko Rendah</div>
                    <div class="value">{rendah:,}</div>
                    <div class="sub">{rendah/total*100:.1f}% dari {total:,} data</div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            # ── Charts ──
            st.markdown("""
            <div class="section-title">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="2" y="3" width="20" height="14" rx="2"/>
                    <line x1="8" y1="21" x2="16" y2="21"/>
                    <line x1="12" y1="17" x2="12" y2="21"/>
                </svg>
                Visualisasi Distribusi
            </div>
            """, unsafe_allow_html=True)

            BG    = '#0D1526'
            COLORS = {'Risiko Tinggi': '#EF4444', 'Risiko Sedang': '#F59E0B', 'Risiko Rendah': '#10B981'}
            cats  = ['Risiko Tinggi', 'Risiko Sedang', 'Risiko Rendah']
            vals  = [tinggi, sedang, rendah]

            fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 4.5))
            fig.patch.set_facecolor(BG)

            # Bar
            ax1.set_facecolor(BG)
            bar_colors = [COLORS[c] for c in cats]
            bars = ax1.bar(cats, vals, color=bar_colors, width=0.42, zorder=3, edgecolor='none')
            ax1.tick_params(colors='#475569', labelsize=8)
            ax1.set_ylabel('Jumlah Data', color='#475569', fontsize=8)
            ax1.set_title('Jumlah Tweet per Kategori Risiko', color='#CBD5E1', fontsize=9, pad=12, fontweight='600')
            for sp in ax1.spines.values(): sp.set_color('#1E293B')
            ax1.yaxis.grid(True, color='#1E293B', linewidth=0.5, zorder=0)
            ax1.set_axisbelow(True)
            ax1.set_xticklabels(cats, fontsize=8, color='#475569')
            for bar, val in zip(bars, vals):
                if val > 0:
                    ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(vals)*0.012,
                             f'{val:,}', ha='center', va='bottom', color='#94A3B8', fontsize=8,
                             fontfamily='monospace')

            # Donut
            ax2.set_facecolor(BG)
            nz_vals   = [v for v in vals if v > 0]
            nz_labels = [c for c, v in zip(cats, vals) if v > 0]
            nz_colors = [COLORS[l] for l in nz_labels]
            wedges, _, autotexts = ax2.pie(
                nz_vals, labels=None, autopct='%1.1f%%', startangle=140,
                colors=nz_colors, pctdistance=0.75,
                wedgeprops=dict(width=0.52, edgecolor=BG, linewidth=2.5)
            )
            for at in autotexts:
                at.set_color('#0D1526'); at.set_fontsize(8.5); at.set_fontweight('700')
            ax2.set_title('Persentase Distribusi Risiko', color='#CBD5E1', fontsize=9, pad=12, fontweight='600')
            legend_patches = [mpatches.Patch(color=c, label=l) for l, c in zip(nz_labels, nz_colors)]
            ax2.legend(handles=legend_patches, loc='lower center', bbox_to_anchor=(0.5, -0.1),
                       ncol=3, frameon=False, fontsize=7.5, labelcolor='#64748B')

            plt.tight_layout(pad=2.2)
            st.pyplot(fig)

            # ── Tabel hasil lengkap ──
            st.markdown("""
            <div class="section-title" style="margin-top:0.5rem;">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <rect x="3" y="3" width="18" height="18" rx="2"/>
                    <path d="M3 9h18M3 15h18M9 3v18"/>
                </svg>
                Tabel Hasil Klasifikasi
            </div>
            """, unsafe_allow_html=True)

            # Pilih kolom output yang tersedia di dataset ini
            output_cols_wanted = ['full_text', 'created_at', 'favorite_count', 'retweet_count',
                                  'reply_count', 'quote_count', 'tweet_url', 'Kategori Risiko']
            output_cols = [c for c in output_cols_wanted if c in df.columns]
            if 'Kategori Risiko' not in output_cols:
                output_cols.append('Kategori Risiko')

            rename_map = {
                'full_text':      'Teks Tweet',
                'created_at':     'Tanggal',
                'favorite_count': 'Like',
                'retweet_count':  'Retweet',
                'reply_count':    'Reply',
                'quote_count':    'Quote',
                'tweet_url':      'URL',
                'Kategori Risiko':'Kategori Risiko',
            }
            df_tampil = df[output_cols].rename(columns=rename_map).copy()

            # Format tanggal jika ada
            if 'Tanggal' in df_tampil.columns:
                df_tampil['Tanggal'] = df_tampil['Tanggal'].apply(format_tanggal)

            st.dataframe(df_tampil, use_container_width=True, hide_index=True, height=380)

            # ── Filter per kategori ──
            st.markdown("""
            <div class="section-title" style="margin-top:1rem;">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <polygon points="22 3 2 3 10 12.46 10 19 14 21 14 12.46 22 3"/>
                </svg>
                Filter Data per Kategori
            </div>
            """, unsafe_allow_html=True)

            filter_opt = st.radio(
                "Tampilkan:", ["Semua", "Risiko Tinggi", "Risiko Sedang", "Risiko Rendah"],
                horizontal=True, label_visibility="collapsed"
            )
            df_filter = df_tampil if filter_opt == "Semua" else df_tampil[df_tampil['Kategori Risiko'] == filter_opt]
            st.dataframe(df_filter, use_container_width=True, hide_index=True, height=300)
            st.markdown(f"<p style='font-size:0.71rem;color:#334155;'>Menampilkan <span style='font-family:JetBrains Mono,monospace;color:#475569;'>{len(df_filter):,}</span> baris dari total {total:,}.</p>", unsafe_allow_html=True)

            # ── Export ──
            st.markdown("""
            <div class="section-title" style="margin-top:1rem;">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                    <polyline points="7 10 12 15 17 10"/>
                    <line x1="12" y1="15" x2="12" y2="3"/>
                </svg>
                Ekspor Hasil
            </div>
            """, unsafe_allow_html=True)

            csv_out = df_tampil.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Unduh Hasil Analisis Lengkap (.csv)",
                data=csv_out,
                file_name="hasil_prediksi_risiko_narkoba.csv",
                mime="text/csv",
            )
