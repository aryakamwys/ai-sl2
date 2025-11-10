# Panduan Setup dan Instalasi
# Smart AQI Monitoring & Recommendation System

## 🚀 Quick Start Guide

### Langkah 1: Persiapan Environment

#### Windows:
```powershell
# Buat virtual environment
python -m venv venv

# Aktifkan virtual environment
.\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### Linux/Mac:
```bash
# Buat virtual environment
python3 -m venv venv

# Aktifkan virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Langkah 2: Konfigurasi API Key

1. Buka browser dan kunjungi: https://makersuite.google.com/app/apikey
2. Login dengan Google Account
3. Klik "Create API Key"
4. Copy API key yang dihasilkan
5. Buka file `.streamlit/secrets.toml`
6. Ganti `YOUR_GEMINI_API_KEY_HERE` dengan API key Anda:

```toml
GEMINI_API_KEY = "AIzaSy..."  # Paste your actual API key here
```

### Langkah 3: Jalankan Aplikasi

```bash
streamlit run main.py
```

Aplikasi akan otomatis membuka di browser: http://localhost:8501

## 🔧 Troubleshooting

### Problem: Module not found error
**Solusi:**
```bash
pip install --upgrade -r requirements.txt
```

### Problem: Streamlit tidak bisa membuka browser
**Solusi:**
Buka browser manual dan akses: http://localhost:8501

### Problem: API Key error dari Gemini
**Solusi:**
1. Pastikan API key sudah benar di secrets.toml
2. Cek quota API di Google AI Studio
3. Pastikan tidak ada spasi atau karakter tersembunyi

### Problem: Port 8501 sudah digunakan
**Solusi:**
```bash
streamlit run main.py --server.port 8502
```

## 📦 Dependencies Lengkap

```
streamlit==1.29.0          # Web framework
google-generativeai==0.3.2 # Gemini AI SDK
pandas==2.1.4              # Data manipulation
plotly==5.18.0             # Interactive charts
```

### Optional dependencies untuk IoT integration:
```bash
pip install paho-mqtt        # MQTT protocol
pip install pyserial         # Serial communication
pip install websocket-client # WebSocket
pip install pymodbus         # Modbus TCP
```

## 🌐 Deployment ke Cloud

### Deploy ke Streamlit Cloud (Gratis):

1. Push code ke GitHub repository
2. Buka https://streamlit.io/cloud
3. Connect GitHub account
4. Deploy repository
5. Tambahkan secrets di dashboard:
   - Key: `GEMINI_API_KEY`
   - Value: Your API key

### Deploy ke Heroku:

1. Install Heroku CLI
2. Create Procfile:
```
web: streamlit run main.py --server.port $PORT
```

3. Deploy:
```bash
heroku create your-app-name
git push heroku main
heroku config:set GEMINI_API_KEY="your_api_key"
```

### Deploy ke Docker:

Create Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "main.py"]
```

Build dan run:
```bash
docker build -t smart-aqi .
docker run -p 8501:8501 -e GEMINI_API_KEY="your_key" smart-aqi
```

## 🔐 Security Best Practices

1. **Jangan commit API key ke Git:**
   - Add `.streamlit/secrets.toml` ke `.gitignore`
   - Gunakan environment variables untuk production

2. **Gunakan HTTPS:**
   - Untuk deployment production, aktifkan HTTPS
   - Streamlit Cloud sudah otomatis menggunakan HTTPS

3. **Rate Limiting:**
   - Implementasikan rate limiting untuk API calls
   - Monitor usage quota Gemini API

## 📊 Performance Optimization

### 1. Caching
Sudah diimplementasikan di code untuk:
- Hasil rekomendasi AI
- Data historis
- Kategori AQI

### 2. Lazy Loading
- Load Gemini AI hanya saat dibutuhkan
- Generate charts on-demand

### 3. Data Management
- Gunakan session state untuk menyimpan data
- Implementasi pagination untuk data besar

## 🔄 Update dan Maintenance

### Update dependencies:
```bash
pip install --upgrade streamlit google-generativeai pandas plotly
pip freeze > requirements.txt
```

### Check for security vulnerabilities:
```bash
pip install safety
safety check
```

## 📱 Mobile Optimization

Streamlit sudah responsive, tapi untuk pengalaman lebih baik:

1. Gunakan viewport meta tag (sudah include di Streamlit)
2. Test di berbagai ukuran layar
3. Pertimbangkan untuk membuat PWA (Progressive Web App)

## 🧪 Testing

### Manual Testing Checklist:
- [ ] Input AQI manual berfungsi
- [ ] Simulasi IoT berfungsi
- [ ] Gauge chart muncul dengan benar
- [ ] Rekomendasi AI generate response
- [ ] Grafik trend tampil
- [ ] Tab switching lancar
- [ ] Download rekomendasi works
- [ ] Responsive di mobile

### Automated Testing:
Create `test_main.py`:
```python
import pytest
from main import get_aqi_category, validate_aqi_data

def test_aqi_category_good():
    result = get_aqi_category(45)
    assert result['category'] == 'Good'

def test_aqi_category_hazardous():
    result = get_aqi_category(350)
    assert result['category'] == 'Hazardous'
```

Run tests:
```bash
pip install pytest
pytest test_main.py
```

## 🎨 Customization

### Mengubah Theme:
Edit `.streamlit/config.toml`:
```toml
[theme]
primaryColor = "#FF4B4B"        # Warna utama
backgroundColor = "#FFFFFF"      # Background
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"
```

### Menambah Logo:
Di `main.py`, ubah URL logo di sidebar:
```python
st.image("path/to/your/logo.png", width=100)
```

## 📈 Monitoring dan Analytics

### Implementasi Google Analytics:
1. Create GA4 property
2. Get measurement ID
3. Add tracking code di Streamlit

### Monitoring API Usage:
- Monitor Gemini API quota di Google Cloud Console
- Set up alerts untuk high usage

## 🤝 Support dan Community

### Getting Help:
1. Check README.md
2. Review code comments
3. Check Streamlit docs: https://docs.streamlit.io
4. Gemini AI docs: https://ai.google.dev/docs

### Reporting Issues:
Jika menemukan bug atau ada saran:
1. Dokumentasikan issue dengan detail
2. Include screenshot jika perlu
3. Sertakan error message lengkap

## 📚 Additional Resources

- Streamlit Documentation: https://docs.streamlit.io
- Google Gemini AI: https://ai.google.dev
- Plotly Documentation: https://plotly.com/python/
- Pandas Guide: https://pandas.pydata.org/docs/

## 🎓 Learning Resources

### Untuk memahami lebih dalam:
1. **AQI Standards**: https://www.epa.gov/aqi
2. **Air Quality Science**: World Health Organization guidelines
3. **IoT Integration**: MQTT, REST API, WebSocket tutorials
4. **Streamlit Development**: Official tutorials

## 💡 Tips Penggunaan

### Untuk Masyarakat:
- Set alert threshold sesuai kondisi kesehatan
- Check AQI sebelum beraktivitas outdoor
- Simpan rekomendasi untuk referensi

### Untuk Industri:
- Monitor compliance score secara rutin
- Review ROI calculator untuk planning investasi
- Dokumentasi untuk audit dan reporting
- Gunakan trend analysis untuk strategic planning

---

**Selamat menggunakan Smart AQI System! 🌍**

Jika ada pertanyaan atau butuh bantuan, jangan ragu untuk bertanya.
