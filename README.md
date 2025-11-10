# 🌍 Smart AQI Monitoring & Recommendation System

Sistem peringatan dan rekomendasi kualitas udara berbasis AI untuk masyarakat dan industri di Indonesia.

## 📋 Deskripsi

Sistem ini dirancang untuk memberikan peringatan dan rekomendasi tindakan terhadap Air Quality Index (AQI) yang didapat dari perangkat IoT. Sistem melayani dua perspektif pengguna:

### 👥 **Untuk Masyarakat Umum**
- 📊 Dashboard monitoring AQI real-time
- ⚠️ Peringatan kesehatan berdasarkan kategori AQI
- 🤖 Rekomendasi aktivitas harian berbasis AI
- 📈 Analisis dan prediksi trend AQI
- 💊 Tips kesehatan personal
- 📱 Sistem alert dan notifikasi
- 🏥 Informasi kesehatan lengkap

### 🏭 **Untuk Industri**
- 📊 Analisis dampak emisi dan compliance
- 🎯 Skor kepatuhan lingkungan
- 💡 Rekomendasi pengurangan polusi berbasis AI
- 📈 Monitoring trend dan prediksi
- 💰 Analisis biaya dampak polusi
- 📊 Perhitungan ROI investasi teknologi bersih
- 🌿 Informasi insentif dan program pemerintah
- 🔧 Rekomendasi teknologi pengendalian emisi

## 🚀 Fitur Utama

### 1. **AI-Powered Recommendations**
- Menggunakan Google Gemini AI untuk memberikan rekomendasi kontekstual
- Rekomendasi dipersonalisasi berdasarkan kondisi pengguna
- Analisis mendalam untuk keputusan strategis industri

### 2. **Real-time Monitoring**
- Input data dari IoT sensor atau manual
- Visualisasi gauge chart interaktif
- Dashboard responsif dengan Plotly

### 3. **Trend Analysis & Prediction**
- Grafik historis 7 hari terakhir
- Prediksi AQI untuk esok hari
- Statistik komprehensif (rata-rata, max, min, std dev)

### 4. **Kategori AQI Standar US EPA**
| Kategori | AQI Range | PM2.5 (μg/m³) | Keterangan |
|----------|-----------|---------------|------------|
| 😊 Good | 0-50 | 0-12.0 | Kualitas udara memuaskan |
| 😐 Moderate | 51-100 | 12.1-35.4 | Sensitif perlu perhatian |
| 😷 Unhealthy (Sensitive) | 101-150 | 35.5-55.4 | Risiko bagi kelompok sensitif |
| 😨 Unhealthy | 151-200 | 55.5-150.4 | Dampak bagi masyarakat umum |
| 🤢 Very Unhealthy | 201-300 | 150.5-250.4 | Batasi aktivitas outdoor |
| ☠️ Hazardous | 301+ | 250.5+ | Hindari aktivitas outdoor |

## 🛠️ Teknologi yang Digunakan

- **Frontend**: Streamlit (Python web framework)
- **AI Engine**: Google Gemini Pro
- **Data Visualization**: Plotly, Pandas
- **Data Processing**: NumPy, Pandas
- **API**: Google Generative AI

## 📦 Instalasi

### 1. Clone atau download repository ini

```bash
cd "AI SL2"
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Konfigurasi API Key Gemini

1. Dapatkan API key gratis di [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Buka file `.streamlit/secrets.toml`
3. Ganti `YOUR_GEMINI_API_KEY_HERE` dengan API key Anda:

```toml
GEMINI_API_KEY = "masukkan_api_key_anda_disini"
```

### 4. Jalankan aplikasi

```bash
streamlit run main.py
```

Aplikasi akan terbuka di browser pada `http://localhost:8501`

## 📱 Cara Penggunaan

### Untuk Masyarakat Umum:

1. **Pilih Perspektif**: Pilih "👥 Masyarakat Umum" di sidebar
2. **Input Data AQI**: 
   - Manual: Gunakan slider untuk input nilai AQI
   - IoT: Klik tombol "Ambil Data dari IoT" untuk simulasi pembacaan sensor
3. **Lihat Dashboard**: Gauge chart dan informasi kategori AQI akan ditampilkan
4. **Dapatkan Rekomendasi AI**: 
   - Masuk ke tab "🤖 Rekomendasi AI"
   - Tambahkan informasi kondisi kesehatan jika ada
   - Klik "Dapatkan Rekomendasi AI"
5. **Analisis Trend**: Lihat grafik historis dan prediksi di tab "📈 Analisis Trend"
6. **Setup Alert**: Konfigurasi notifikasi di tab "📱 Alert System"

### Untuk Industri:

1. **Pilih Perspektif**: Pilih "🏭 Industri" di sidebar
2. **Input Data**:
   - Input nilai AQI (manual atau IoT)
   - Pilih jenis industri
   - Pilih sumber emisi utama
3. **Dapatkan Rekomendasi AI**: 
   - Tab "🤖 Rekomendasi AI" untuk action plan dan strategi
   - Rekomendasi mencakup immediate actions dan long-term strategy
4. **Monitor Compliance**: Tab "🏭 Compliance" untuk status kepatuhan
5. **Analisis Biaya**: Tab "💰 Cost Analysis" untuk:
   - Estimasi biaya dampak polusi
   - Perhitungan ROI investasi teknologi bersih
   - Rekomendasi teknologi pengendalian emisi
   - Informasi insentif pemerintah

## 🔌 Integrasi IoT

Sistem ini dirancang untuk menerima input dari sensor IoT. Untuk integrasi penuh:

### Contoh Integrasi dengan MQTT:

```python
import paho.mqtt.client as mqtt

def on_message(client, userdata, message):
    aqi_value = float(message.payload.decode())
    st.session_state['aqi_value'] = aqi_value

client = mqtt.Client()
client.connect("broker.hivemq.com", 1883)
client.subscribe("aqi/sensor/location1")
client.on_message = on_message
client.loop_start()
```

### Contoh Integrasi dengan REST API:

```python
import requests

def fetch_aqi_from_iot():
    response = requests.get("http://your-iot-device/api/aqi")
    return response.json()['aqi']
```

## 📊 Struktur Data IoT yang Diharapkan

```json
{
  "timestamp": "2025-11-04T10:30:00Z",
  "location": "Jakarta, Indonesia",
  "aqi": 85,
  "pm25": 25.5,
  "pm10": 45.2,
  "temperature": 28.5,
  "humidity": 75
}
```

## 🎯 Fitur Tambahan yang Mendukung

### 1. **Download Rekomendasi**
- Export rekomendasi AI ke file TXT
- Simpan untuk dokumentasi atau laporan

### 2. **Multi-parameter Support**
- PM2.5, PM10, SO2, NO2, CO, O3
- Compliance checking untuk setiap parameter

### 3. **Cost-Benefit Analysis**
- Perhitungan biaya dampak polusi
- ROI calculator untuk investasi teknologi
- Payback period estimation

### 4. **Regulatory Compliance**
- Tracking status kepatuhan
- Reminder untuk kewajiban pelaporan
- Referensi peraturan terkini

### 5. **Educational Content**
- Informasi kelompok sensitif
- Tips kesehatan berdasarkan AQI
- Panduan penggunaan masker
- Kontak darurat

## 🌟 Keunggulan Sistem

1. **Dual Perspective**: Melayani masyarakat dan industri
2. **AI-Powered**: Rekomendasi kontekstual dari Gemini AI
3. **Real-time**: Monitoring dan alert langsung
4. **Predictive**: Forecasting untuk planning
5. **Comprehensive**: Dari kesehatan hingga business impact
6. **User-friendly**: Interface intuitif dengan Streamlit
7. **Actionable**: Rekomendasi praktis yang bisa langsung diterapkan
8. **Data-driven**: Visualisasi dan analytics lengkap

## 📈 Roadmap

- [ ] Integrasi dengan multiple IoT protocols (MQTT, CoAP, HTTP)
- [ ] Machine learning untuk prediksi lebih akurat
- [ ] Mobile app (iOS & Android)
- [ ] Multi-language support
- [ ] Integration dengan sistem ERP industri
- [ ] Blockchain untuk carbon credit tracking
- [ ] Community reporting system
- [ ] Advanced analytics dashboard

## 🤝 Kontribusi

Sistem ini dikembangkan untuk mendukung Indonesia yang lebih sehat dan berkelanjutan. Kontribusi dalam bentuk:
- Feature requests
- Bug reports
- Code improvements
- Documentation updates

sangat diterima!

## ⚖️ Regulasi Terkait

Sistem ini mengacu pada:
- **PP No. 22 Tahun 2021**: Perlindungan dan Pengelolaan Lingkungan Hidup
- **Permen LHK No. 13 Tahun 2020**: Baku Mutu Emisi
- **Permen LHK No. 7 Tahun 2021**: PROPER
- **US EPA AQI Standard**: Air Quality Index guidelines

## 📞 Support

Untuk pertanyaan atau dukungan:
- 📧 Email: help@smartaqi.id
- 📱 Hotline: 1500-AQI
- 🌐 Website: www.smartaqi.id

## 📄 Lisensi

© 2025 Smart AQI System. Untuk Indonesia yang lebih sehat 🇮🇩

---

**Dikembangkan dengan ❤️ untuk masyarakat dan industri Indonesia**
