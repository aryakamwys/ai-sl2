

import streamlit as st
import google.generativeai as genai
from datetime import datetime

# Konfigurasi halaman
st.set_page_config(
    page_title="Smart AQI Recommendation System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key dari Streamlit secrets atau hardcoded
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except:
    GEMINI_API_KEY = ""

# Configure Gemini
if GEMINI_API_KEY and GEMINI_API_KEY != "YOUR_GEMINI_API_KEY_HERE":
    genai.configure(api_key=GEMINI_API_KEY)
else:
    st.error("⚠️ API Key Gemini belum dikonfigurasi!")
    st.info("Edit file ini dan ganti GEMINI_API_KEY dengan API key Anda")
    st.stop()

# CSS Custom
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
    }
    .aqi-card {
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    .good { background: linear-gradient(135deg, #84fab0 0%, #8fd3f4 100%); }
    .moderate { background: linear-gradient(135deg, #ffecd2 0%, #fcb69f 100%); }
    .unhealthy-sensitive { background: linear-gradient(135deg, #ffb347 0%, #ffcc33 100%); }
    .unhealthy { background: linear-gradient(135deg, #ff6b6b 0%, #ee5a6f 100%); color: white; }
    .very-unhealthy { background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%); }
    .hazardous { background: linear-gradient(135deg, #8e44ad 0%, #c0392b 100%); color: white; }
</style>
""", unsafe_allow_html=True)


# ===== FUNGSI KATEGORISASI AQI =====
def get_aqi_category(aqi):
    """
    Kategorisasi AQI berdasarkan standar US EPA
    
    Args:
        aqi (int/float): Nilai AQI (0-500)
    
    Returns:
        dict: Informasi kategori AQI
    """
    if aqi <= 50:
        return {
            "category": "Good",
            "level": "Baik",
            "color": "Hijau",
            "css_class": "good",
            "icon": "😊",
            "pm25_range": "0-12.0 μg/m³",
            "health_impact": "Kualitas udara memuaskan, risiko minimal"
        }
    elif aqi <= 100:
        return {
            "category": "Moderate",
            "level": "Sedang",
            "color": "Kuning",
            "css_class": "moderate",
            "icon": "😐",
            "pm25_range": "12.1-35.4 μg/m³",
            "health_impact": "Kelompok sensitif perlu perhatian"
        }
    elif aqi <= 150:
        return {
            "category": "Unhealthy for Sensitive Groups",
            "level": "Tidak Sehat untuk Kelompok Sensitif",
            "color": "Orange",
            "css_class": "unhealthy-sensitive",
            "icon": "😷",
            "pm25_range": "35.5-55.4 μg/m³",
            "health_impact": "Kelompok sensitif akan mengalami dampak kesehatan"
        }
    elif aqi <= 200:
        return {
            "category": "Unhealthy",
            "level": "Tidak Sehat",
            "color": "Merah",
            "css_class": "unhealthy",
            "icon": "😨",
            "pm25_range": "55.5-150.4 μg/m³",
            "health_impact": "Semua orang mulai mengalami dampak kesehatan"
        }
    elif aqi <= 300:
        return {
            "category": "Very Unhealthy",
            "level": "Sangat Tidak Sehat",
            "color": "Ungu",
            "css_class": "very-unhealthy",
            "icon": "🤢",
            "pm25_range": "150.5-250.4 μg/m³",
            "health_impact": "Peringatan kesehatan: semua orang terdampak"
        }
    else:
        return {
            "category": "Hazardous",
            "level": "Berbahaya",
            "color": "Maroon",
            "css_class": "hazardous",
            "icon": "☠️",
            "pm25_range": "250.5+ μg/m³",
            "health_impact": "Darurat kesehatan: hindari aktivitas outdoor"
        }


# ===== FUNGSI REKOMENDASI UNTUK MASYARAKAT =====
def get_public_recommendation(aqi_value, additional_info=""):
    """
    Mendapatkan rekomendasi untuk masyarakat umum dari Gemini AI
    
    Args:
        aqi_value (int/float): Nilai AQI
        additional_info (str): Informasi tambahan (kondisi kesehatan, dll)
    
    Returns:
        str: Rekomendasi dari Gemini AI
    """
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "❌ API Key Gemini belum dikonfigurasi. Silakan setup terlebih dahulu."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        aqi_info = get_aqi_category(aqi_value)
        
        prompt = f"""
Sebagai ahli kesehatan lingkungan, berikan rekomendasi yang detail dan praktis untuk masyarakat umum.

DATA KUALITAS UDARA:
- Nilai AQI: {aqi_value}
- Kategori: {aqi_info['level']} ({aqi_info['category']})
- PM2.5 Range: {aqi_info['pm25_range']}
- Dampak Kesehatan: {aqi_info['health_impact']}

{f"INFORMASI TAMBAHAN: {additional_info}" if additional_info else ""}

Berikan rekomendasi dalam format berikut:

1. STATUS PERINGATAN
   Ringkasan singkat kondisi saat ini

2. KELOMPOK BERISIKO
   Siapa yang paling terpengaruh

3. REKOMENDASI AKTIVITAS
   - Aktivitas yang AMAN dilakukan
   - Aktivitas yang HARUS DIHINDARI
   
4. TIPS KESEHATAN PRAKTIS
   Minimal 5 tips untuk melindungi diri

5. PENGGUNAAN MASKER
   Jenis masker yang direkomendasikan

6. WAKTU TERBAIK UNTUK AKTIVITAS OUTDOOR
   Kapan sebaiknya keluar rumah

Gunakan bahasa Indonesia yang mudah dipahami. Berikan poin-poin yang jelas dan actionable.
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error mendapatkan rekomendasi: {str(e)}"


# ===== FUNGSI REKOMENDASI UNTUK INDUSTRI =====
def get_industry_recommendation(aqi_value, industry_type="Manufaktur", emission_sources=""):
    """
    Mendapatkan rekomendasi untuk industri dari Gemini AI
    
    Args:
        aqi_value (int/float): Nilai AQI
        industry_type (str): Jenis industri
        emission_sources (str): Sumber emisi utama
    
    Returns:
        str: Rekomendasi dari Gemini AI
    """
    if GEMINI_API_KEY == "YOUR_GEMINI_API_KEY_HERE":
        return "❌ API Key Gemini belum dikonfigurasi. Silakan setup terlebih dahulu."
    
    try:
        model = genai.GenerativeModel('gemini-pro')
        aqi_info = get_aqi_category(aqi_value)
        
        prompt = f"""
Sebagai konsultan lingkungan industri, berikan analisis dan rekomendasi profesional untuk industri.

DATA KUALITAS UDARA:
- Nilai AQI: {aqi_value}
- Kategori: {aqi_info['level']} ({aqi_info['category']})
- PM2.5 Range: {aqi_info['pm25_range']}

INFORMASI INDUSTRI:
- Jenis Industri: {industry_type}
- Sumber Emisi: {emission_sources if emission_sources else "Umum"}

Berikan analisis dan rekomendasi dalam format:

1. ANALISIS DAMPAK
   Bagaimana kondisi AQI ini berkaitan dengan emisi industri dan dampaknya

2. STATUS COMPLIANCE
   Status kepatuhan terhadap baku mutu emisi dan regulasi lingkungan

3. RISIKO OPERASIONAL
   Potensi dampak terhadap operasional, citra perusahaan, dan regulasi

4. ACTION PLAN SEGERA (Prioritas Tinggi)
   Minimal 5 tindakan konkret yang HARUS segera dilakukan

5. STRATEGI JANGKA MENENGAH (3-6 bulan)
   Program pengurangan emisi dan improvement

6. REKOMENDASI TEKNOLOGI
   Teknologi pengendalian pencemaran yang relevan untuk industri ini

7. ESTIMASI ROI
   Perkiraan return on investment dari program pengurangan emisi

8. PROGRAM CSR
   Inisiatif tanggung jawab sosial yang relevan

9. MONITORING & REPORTING
   Sistem pemantauan dan pelaporan yang direkomendasikan

Berikan angka spesifik jika memungkinkan. Gunakan bahasa profesional dalam Bahasa Indonesia.
"""
        
        response = model.generate_content(prompt)
        return response.text
        
    except Exception as e:
        return f"❌ Error mendapatkan rekomendasi: {str(e)}"


# ===== FUNGSI UTAMA STREAMLIT =====
def main():
    """
    Fungsi utama untuk menjalankan aplikasi Streamlit
    """
    # Header
    st.markdown("<h1 class='main-header'>🌍 Smart AQI Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("### Sistem Rekomendasi Kualitas Udara Berbasis AI")
    
    # Sidebar
    with st.sidebar:
        st.header("⚙️ Konfigurasi")
        
        # Pilih perspektif
        perspective = st.selectbox(
            "Pilih Perspektif:",
            ["👥 Masyarakat Umum", "🏭 Industri"],
            key="perspective"
        )
        
        st.markdown("---")
        
        # Input AQI
        st.subheader("📊 Input Data AQI")
        aqi_value = st.slider(
            "Nilai AQI",
            min_value=0,
            max_value=500,
            value=85,
            step=5,
            help="Geser untuk mengatur nilai AQI (0-500)"
        )
        
        st.markdown("---")
        
        # Informasi tambahan berdasarkan perspektif
        if perspective == "👥 Masyarakat Umum":
            st.subheader("ℹ️ Informasi Tambahan")
            has_condition = st.checkbox("Memiliki kondisi kesehatan khusus?")
            additional_info = ""
            if has_condition:
                condition = st.text_input("Kondisi kesehatan (contoh: asma, jantung)")
                additional_info = condition
        else:
            st.subheader("🏭 Informasi Industri")
            industry_type = st.selectbox(
                "Jenis Industri:",
                ["Manufaktur", "Petrokimia", "Pembangkit Listrik", "Semen", "Tekstil", "Lainnya"]
            )
            emission_sources = st.text_input(
                "Sumber Emisi Utama:",
                placeholder="Contoh: Boiler, Furnace, Generator"
            )
        
        st.markdown("---")
        st.info("💡 Sistem menggunakan Google Gemini AI untuk rekomendasi")
    
    # Main content
    # Tampilkan kategori AQI
    aqi_info = get_aqi_category(aqi_value)
    
    st.markdown(f"""
    <div class='aqi-card {aqi_info['css_class']}'>
        <h2>{aqi_info['icon']} {aqi_info['level']}</h2>
        <h3>AQI: {aqi_value}</h3>
        <p><strong>Kategori:</strong> {aqi_info['category']}</p>
        <p><strong>PM2.5 Range:</strong> {aqi_info['pm25_range']}</p>
        <p><strong>Dampak Kesehatan:</strong> {aqi_info['health_impact']}</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Tombol untuk mendapatkan rekomendasi
    if st.button("🔮 Dapatkan Rekomendasi AI", type="primary", use_container_width=True):
        with st.spinner("⏳ Menganalisis data dan menyusun rekomendasi..."):
            if perspective == "👥 Masyarakat Umum":
                recommendation = get_public_recommendation(aqi_value, additional_info)
            else:
                recommendation = get_industry_recommendation(aqi_value, industry_type, emission_sources)
            
            # Tampilkan rekomendasi
            st.markdown("## 📋 Rekomendasi AI (Gemini)")
            st.markdown(recommendation)
            
            # Tombol download
            st.download_button(
                label="📥 Download Rekomendasi",
                data=recommendation,
                file_name=f"rekomendasi_AQI{int(aqi_value)}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Footer
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("**🤖 AI Technology**")
        st.caption("Powered by Google Gemini")
    
    with col2:
        st.markdown("**📊 Data Standard**")
        st.caption("US EPA AQI Guidelines")
    
    with col3:
        st.markdown("**🇮🇩 Indonesia**")
        st.caption("Untuk udara yang lebih sehat")
    
    st.caption("© 2025 Smart AQI System")


# ===== FUNGSI HELPER UNTUK PENGGUNAAN PROGRAMMATIC =====
def get_recommendation(aqi_value, perspective='public', **kwargs):
    """
    Fungsi wrapper untuk mendapatkan rekomendasi secara programmatic
    
    Args:
        aqi_value (int/float): Nilai AQI
        perspective (str): 'public' atau 'industry'
        **kwargs: Parameter tambahan (additional_info, industry_type, emission_sources)
    
    Returns:
        dict: Dictionary berisi kategori AQI dan rekomendasi
    """
    aqi_info = get_aqi_category(aqi_value)
    
    if perspective.lower() == 'public':
        additional_info = kwargs.get('additional_info', '')
        recommendation = get_public_recommendation(aqi_value, additional_info)
    else:
        industry_type = kwargs.get('industry_type', 'Manufaktur')
        emission_sources = kwargs.get('emission_sources', '')
        recommendation = get_industry_recommendation(aqi_value, industry_type, emission_sources)
    
    return {
        'aqi_value': aqi_value,
        'category': aqi_info,
        'recommendation': recommendation,
        'timestamp': datetime.now().isoformat()
    }


# ===== JALANKAN PROGRAM =====
if __name__ == "__main__":
    main()
