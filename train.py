import pandas as pd
import pickle
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report

print("⏳ Memulai PROSES TRAINING OPTIMASI TINGGI...")

# 1. Load Dataset
try:
    df = pd.read_csv('dataset_narkoba_final.csv')
    print(f"✅ Dataset berhasil dimuat! Total data: {len(df)} baris.")
except Exception as e:
    print(f"❌ Gagal membaca file CSV. Pastikan file 'dataset_narkoba_final.csv' ada di folder ini. Detail: {e}")
    exit()

kolom_teks = 'full_text'
kolom_label = 'sentimen'

# 2. UPGRADE: Fungsi Preprocessing yang Lebih Pintar
def bersihkan_teks(text):
    text = str(text).lower()
    # Hapus URL/Link website
    text = re.sub(r'http\S+|www\S+|https\S+', '', text, flags=re.MULTILINE)
    # Hapus Twitter Mentions (@user)
    text = re.sub(r'@\w+', '', text)
    # OPTIMASI: Hapus simbol '#' saja, kata kuncinya jangan dibuang (misal: #nyabu -> nyabu)
    text = re.sub(r'#(\w+)', r'\1', text)
    # Hapus karakter non-alfabet (angka & tanda baca)
    text = re.sub(r'[^a-z\s]', '', text)
    # Bersihkan spasi berlebih
    text = re.sub(r'\s+', ' ', text).strip()
    return text

print("🧹 Melakukan pembersihan teks tingkat lanjut...")
df['teks_bersih'] = df[kolom_teks].apply(bersihkan_teks)

# Hapus data kosong setelah preprocessing
df = df.dropna(subset=['teks_bersih'])
df = df[df['teks_bersih'] != '']

X = df['teks_bersih']
y = df[kolom_label]

# Membagi data (80:20)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# 3. UPGRADE: Fitur TF-IDF dengan Bigram (ngram_range=(1,2)) & Seleksi Kata Minimum
print("🔤 Mengonversi teks ke TF-IDF Pembobotan Frasa (N-gram 1,2)...")
tfidf = TfidfVectorizer(ngram_range=(1, 2), min_df=2, max_features=10000)
X_train_tfidf = tfidf.fit_transform(X_train)
X_test_tfidf = tfidf.transform(X_test)

# 4. UPGRADE: Model SVM dengan Bobot Kelas Seimbang (Class Balanced)
print("🧠 Melatih Model SVM Berakurasi Tinggi...")
model_svm = SVC(kernel='linear', C=1.0, class_weight='balanced', random_state=42)
model_svm.fit(X_train_tfidf, y_train)

# 5. Evaluasi Hasil Akhir
y_pred = model_svm.predict(X_test_tfidf)
print("\n================ 🔥 PERFORMA MODEL BARU 🔥 ================")
print(f"📊 Akurasi Model SVM Sekarang: {accuracy_score(y_test, y_pred) * 100:.2f}%")
print("\n📋 Laporan Detail Kategori (Precision, Recall, F1-Score):")
print(classification_report(y_test, y_pred))
print("===========================================================\n")

# 6. Menyimpan ke File .pkl Baru
print("💾 Menyimpan cetakan otak AI ke file .pkl baru...")
with open('tfidf_vectorizer_narkoba.pkl', 'wb') as f_tfidf:
    pickle.dump(tfidf, f_tfidf)

with open('model_svm_narkoba.pkl', 'wb') as f_model:
    pickle.dump(model_svm, f_model)

print("🎉 SUKSES! File .pkl berakurasi tinggi telah diperbarui!")