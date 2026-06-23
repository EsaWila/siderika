import streamlit as st
import pickle
import re
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Konfigurasi Tampilan Halaman Web (Wide Layout)
st.set_page_config(page_title="Dashboard Deteksi Narkoba", page_icon="🕵️‍♂️", layout="wide")

# ==================== SIDEBAR ====================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/2092/2092249.png", width=100)
    st.title("🛡️ Info Sistem")
    st.info("""
    **Metode di-Upgrade:**
    * **Fitur:** TF-IDF (Word & Bigram)
    * **Klasifikasi:** SVM (Balanced Class)
    """)
    st.success("""
    **📊 Performa Model SVM:**
    * **Akurasi Sistem:** **97.45%** (Optimized)
    * **Status:** Siap Digunakan
    """)
    st.write("---")
    st.caption("Aplikasi Deteksi Dini Risiko Penyalahgunaan Narkoba © 2026")

# ==================== HALAMAN UTAMA ====================
st.title("🕵️‍♂️ Dashboard Deteksi Dini Risiko Penyalahgunaan Narkoba")
st.markdown("Sistem cerdas berbasis *Machine Learning* untuk mengidentifikasi tingkat risiko teks media sosial.")
st.write("---")

# 2. Memuat Model SVM dan TF-IDF dari file Pickle (.pkl)
@st.cache_resource
def load_model():
    with open('tfidf_vectorizer_narkoba.pkl', 'rb') as f_tfidf:
        tfidf = pickle.load(f_tfidf)
    with open('model_svm_narkoba.pkl', 'rb') as f_model:
        model = pickle.load(f_model)
    return tfidf, model

try:
    tfidf, model_svm = load_model()
except Exception as e:
    st.error(f"Gagal memuat model. Pastikan file .pkl ada di folder yang sama. Detail: {e}")

# 3. Fungsi Preprocessing (Harus SAMA PERSIS dengan train.py agar Akurat)
def bersihkan_teks(text):
    text = str(text).lower()
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    text = re.sub(r'@\w+', '', text)
    text = re.sub(r'#(\w+)', r'\1', text) # Mempertahankan isi hashtag
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def petakan_risiko(prediksi):
    if prediksi == 'Positif': return "🔴 RISIKO TINGGI"
    elif prediksi == 'Netral': return "🟡 RISIKO SEDANG"
    elif prediksi == 'Negatif': return "🟢 RISIKO RENDAH"
    return "Tidak Diketahui"

# 4. Menu Navigasi Berbasis TAB
tab1, tab2 = st.tabs(["📑 Input Manual (Teks Tunggal)", "📊 Upload Dataset (File CSV)"])

# ==================== TAB 1: INPUT MANUAL ====================
with tab1:
    st.subheader("🔮 Uji Kalimat Secara Real-Time")
    user_input = st.text_area("Ketik atau tempel (paste) cuitan/kalimat di sini:", 
                              placeholder="Contoh: lagi nyabu bareng temen berasa melayang bro...", key="tunggal")
    
    if st.button("Analisis Teks", type="primary"):
        if user_input.strip() == "":
            st.warning("Silakan masukkan teks terlebih dahulu!")
        else:
            teks_bersih = bersihkan_teks(user_input)
            vektor_uji = tfidf.transform([teks_bersih])
            hasil_prediksi = model_svm.predict(vektor_uji)[0]
            status_risiko = petakan_risiko(hasil_prediksi)
            
            st.write("### 📌 Hasil Analisis Kasus:")
            if hasil_prediksi == 'Positif':
                st.error(f"**{status_risiko}**\n\n*Indikasi: Konsumsi aktif, aktivitas penyalahgunaan langsung, atau transaksi narkoba.*")
            elif hasil_prediksi == 'Netral':
                st.warning(f"**{status_risiko}**\n\n*Indikasi: Pemberitaan kasus hukum, razia kepolisian, atau laporan edukasi formal.*")
            elif hasil_prediksi == 'Negatif':
                st.success(f"**{status_risiko}**\n\n*Indikasi: Kampanye anti-narkoba, edukasi masyarakat, atau ajakan rehabilitasi.*")

# ==================== TAB 2: UPLOAD CSV ====================
with tab2:
    st.subheader("📂 Analisis Massal via Upload CSV")
    st.markdown("Gunakan fitur ini untuk menganalisis ratusan hingga ribuan tweet sekaligus dari file hasil scraping.")
    
    uploaded_file = st.file_uploader("Unggah file CSV kamu di sini", type=["csv"])
    
    if uploaded_file is not None:
        df_input = pd.read_csv(uploaded_file)
        st.write("📄 **Pratinjau 5 Data Teratas:**", df_input.head(5))
        
        kolom_pilihan = st.selectbox("Pilih kolom yang berisi teks tweet/kalimat:", df_input.columns)
        
        if st.button("Proses Analisis Massal", type="primary"):
            with st.spinner('Model SVM sedang membaca dan mengklasifikasikan data...'):
                df_input['teks_bersih'] = df_input[kolom_pilihan].apply(bersihkan_teks)
                vektor_massal = tfidf.transform(df_input['teks_bersih'].fillna(''))
                df_input['Hasil_Sentimen'] = model_svm.predict(vektor_massal)
                df_input['Status_Risiko'] = df_input['Hasil_Sentimen'].apply(petakan_risiko)
                
                st.success("✅ Analisis Massal Selesai!")
                
                # Menghitung Statistik
                total_data = len(df_input)
                tinggi = len(df_input[df_input['Hasil_Sentimen'] == 'Positif'])
                sedang = len(df_input[df_input['Hasil_Sentimen'] == 'Netral'])
                rendah = len(df_input[df_input['Hasil_Sentimen'] == 'Negatif'])
                
                # Tampilan Widget Angka Ringkasan
                st.write("### 📈 Ringkasan Distribusi Tingkat Risiko")
                col1, col2, col3 = st.columns(3)
                col1.metric("🔴 Risiko Tinggi", f"{tinggi} data", f"{tinggi/total_data*100:.1f}%")
                col2.metric("🟡 Risiko Sedang", f"{sedang} data", f"{sedang/total_data*100:.1f}%")
                col3.metric("🟢 Risiko Rendah", f"{rendah} data", f"{rendah/total_data*100:.1f}%")
                
                # Visualisasi Dual Grafik (Bar Chart + Pie Chart)
                st.write("### 📊 Visualisasi Grafik Hasil Analisis")
                fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
                
                # 1. Bar Chart
                sns.countplot(x='Status_Risiko', data=df_input, 
                              order=['🔴 RISIKO TINGGI', '🟡 RISIKO SEDANG', '🟢 RISIKO RENDAH'], 
                              palette=['#ef4444', '#eab308', '#22c55e'], ax=ax1)
                ax1.set_ylabel("Jumlah Tweet")
                ax1.set_xlabel("Tingkat Risiko")
                ax1.set_title("Grafik Jumlah Data per Kategori")
                
                # 2. Pie Chart
                labels = ['Risiko Tinggi', 'Risiko Sedang', 'Risiko Rendah']
                sizes = [tinggi, sedang, rendah]
                labels = [l for l, s in zip(labels, sizes) if s > 0]
                sizes = [s for s in sizes if s > 0]
                
                ax2.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140, 
                        colors=['#ef4444', '#eab308', '#22c55e'][:len(sizes)])
                ax2.axis('equal')
                ax2.set_title("Persentase Distribusi Risiko")
                
                st.pyplot(fig)
                
                # Tombol Download Hasil
                st.write("### 💾 Ekspor Hasil")
                csv_hasil = df_input.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="📥 Download File Hasil Analisis (.csv)",
                    data=csv_hasil,
                    file_name="hasil_prediksi_risiko_narkoba.csv",
                    mime="text/csv"
                )