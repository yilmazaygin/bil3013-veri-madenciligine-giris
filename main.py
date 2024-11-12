import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt

# Backend'i değiştirerek GUI hatasını önlüyoruz
plt.switch_backend('Agg')

# 1. Veri Okuma
data = pd.read_csv("output_csv.csv")

# 2. Fiyat Sütununu Temizleme
data['Fiyat'] = data['listing_price'].str.replace(' TL', '', regex=True).str.replace('.', '', regex=True).astype(float)

# 3. Eksik Değerleri Temizleme
data_cleaned = data.dropna(subset=['Fiyat'])

# 4. Uç Değerleri Temizleme (%95 Üzerini Çıkarma)
q95 = data_cleaned['Fiyat'].quantile(0.95)
data_filtered = data_cleaned[data_cleaned['Fiyat'] <= q95].copy()  # .copy() ekledik

# 5. Fiyatları Normalleştirme
fiyatlar_filtered = data_filtered[['Fiyat']].values
scaler = StandardScaler()
fiyatlar_filtered_normalize = scaler.fit_transform(fiyatlar_filtered)

# 6. K-means Kümeleme
kmeans = KMeans(n_clusters=3, random_state=0)
data_filtered['Kume'] = kmeans.fit_predict(fiyatlar_filtered_normalize)

# 7. Küme İstatistiklerini Hesaplama
kume_istatistikleri = data_filtered.groupby('Kume')['Fiyat'].agg(['count', 'min', 'max', 'mean', 'std'])
print("Küme İstatistikleri:")
print(kume_istatistikleri)

# 8. Grafiksel Görselleştirme
plt.figure(figsize=(10, 6))
for kume_no in range(3):
    plt.hist(data_filtered[data_filtered['Kume'] == kume_no]['Fiyat'], bins=20, alpha=0.5, label=f'Küme {kume_no}')

plt.xlabel('Fiyat')
plt.ylabel('Frekans')
plt.title('Fiyat Dağılımı - Küme Analizi')
plt.legend()
plt.savefig("kume_analizi_histogram.png")  # Grafiği dosyaya kaydediyoruz

# 9. Temizlenmiş Veriyi Kaydetme
data_filtered.to_csv("temizlenmis_veriseti_sonuclu.csv", index=False)
