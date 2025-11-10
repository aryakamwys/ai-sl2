import streamlit as st
import google.generativeai as genai
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import time

# Konfigurasi halaman
st.set_page_config(
    page_title="Smart AQI Monitoring & Recommendation System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Konfigurasi Gemini API
GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)

# CSS Custom untuk styling
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
    .metric-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Fungsi untuk mengkategorikan AQI
def get_aqi_category(aqi):
    """Mengkategorikan nilai AQI berdasarkan standar US EPA"""
    if aqi <= 50:
        return {
            "category": "Good",
            "color": "good",
            "pm25_range": "0-12.0",
            "health_implication": "Air quality is satisfactory and poses little or no risk.",
            "icon": "😊"
        }
    elif aqi <= 100:
        return {
            "category": "Moderate",
            "color": "moderate",
            "pm25_range": "12.1-35.4",
            "health_implication": "Sensitive individuals should avoid outdoor activity as they may experience respiratory symptoms.",
            "icon": "😐"
        }
    elif aqi <= 150:
        return {
            "category": "Unhealthy for Sensitive Groups",
            "color": "unhealthy-sensitive",
            "pm25_range": "35.5-55.4",
            "health_implication": "General public and sensitive individuals are at risk to experience irritation and respiratory problems.",
            "icon": "😷"
        }
    elif aqi <= 200:
        return {
            "category": "Unhealthy",
            "color": "unhealthy",
            "pm25_range": "55.5-150.4",
            "health_implication": "Increased likelihood of adverse effects and aggravation to heart and lungs among general public.",
            "icon": "😨"
        }
    elif aqi <= 300:
        return {
            "category": "Very Unhealthy",
            "color": "very-unhealthy",
            "pm25_range": "150.5-250.4",
            "health_implication": "General public will be noticeably affected. Sensitive groups should restrict outdoor activities.",
            "icon": "🤢"
        }
    else:
        return {
            "category": "Hazardous",
            "color": "hazardous",
            "pm25_range": "250.5+",
            "health_implication": "General public at high risk of experiencing strong irritations and adverse health effects. Should avoid outdoor activities.",
            "icon": "☠️"
        }

# Fungsi untuk mendapatkan rekomendasi dari Gemini
def get_gemini_recommendation(aqi_value, user_type, additional_context=""):
    """Mendapatkan rekomendasi dari Gemini AI"""
    if not GEMINI_API_KEY:
        return "⚠️ API Key Gemini belum dikonfigurasi. Silakan tambahkan GEMINI_API_KEY di secrets."
    
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        aqi_info = get_aqi_category(aqi_value)
        
        if user_type == "public":
            prompt = f"""
            Sebagai ahli kesehatan lingkungan, berikan rekomendasi yang detail dan praktis untuk masyarakat umum.
            
            Data Kualitas Udara Saat Ini:
            - Nilai AQI: {aqi_value}
            - Kategori: {aqi_info['category']}
            - PM2.5 Range: {aqi_info['pm25_range']} μg/m³
            - Dampak Kesehatan: {aqi_info['health_implication']}
            
            Konteks Tambahan: {additional_context}
            
            Berikan rekomendasi dalam format berikut:
            1. **Status Peringatan** - Ringkasan singkat kondisi
            2. **Kelompok Berisiko** - Siapa yang paling terpengaruh
            3. **Rekomendasi Aktivitas** - Apa yang boleh dan tidak boleh dilakukan
            4. **Tips Kesehatan** - Cara melindungi diri (minimal 5 tips praktis)
            5. **Penggunaan Masker** - Jenis masker yang direkomendasikan
            6. **Aktivitas Indoor** - Saran kegiatan di dalam ruangan
            7. **Waktu Terbaik Keluar** - Kapan sebaiknya melakukan aktivitas outdoor
            
            Gunakan bahasa Indonesia yang mudah dipahami dan berikan bullet points untuk memudahkan pembacaan.
            """
        else:  # industry
            prompt = f"""
            Sebagai konsultan lingkungan industri, berikan analisis dan rekomendasi untuk industri/pabrik.
            
            Data Kualitas Udara Saat Ini:
            - Nilai AQI: {aqi_value}
            - Kategori: {aqi_info['category']}
            - PM2.5 Range: {aqi_info['pm25_range']} μg/m³
            
            Konteks Tambahan: {additional_context}
            
            Berikan analisis dan rekomendasi dalam format:
            1. **Analisis Dampak** - Bagaimana kondisi AQI ini berkaitan dengan emisi industri
            2. **Compliance Status** - Status kepatuhan terhadap baku mutu emisi
            3. **Risiko Operasional** - Potensi dampak terhadap operasional dan citra perusahaan
            4. **Action Plan Immediate** - Tindakan segera yang harus dilakukan (minimal 5 poin)
            5. **Strategi Jangka Menengah** - Program pengurangan emisi 3-6 bulan
            6. **Investasi Teknologi** - Rekomendasi teknologi pengendalian pencemaran
            7. **Perhitungan ROI** - Estimasi return on investment dari program pengurangan emisi
            8. **Corporate Social Responsibility** - Program CSR yang relevan
            9. **Monitoring & Reporting** - Sistem pemantauan yang direkomendasikan
            
            Sertakan angka dan data spesifik jika memungkinkan. Gunakan bahasa profesional dalam Bahasa Indonesia.
            """
        
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"❌ Error mendapatkan rekomendasi: {str(e)}"

# Fungsi untuk membuat gauge chart AQI
def create_aqi_gauge(aqi_value):
    """Membuat gauge chart untuk visualisasi AQI"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Air Quality Index", 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#84fab0'},
                {'range': [50, 100], 'color': '#ffecd2'},
                {'range': [100, 150], 'color': '#ffb347'},
                {'range': [150, 200], 'color': '#ff6b6b'},
                {'range': [200, 300], 'color': '#a8edea'},
                {'range': [300, 500], 'color': '#8e44ad'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': aqi_value
            }
        }
    ))
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20))
    return fig

# Fungsi untuk simulasi data historis
def generate_historical_data(current_aqi, days=7):
    """Generate data historis untuk trend analysis"""
    dates = [datetime.now() - timedelta(days=x) for x in range(days, 0, -1)]
    dates.append(datetime.now())
    
    # Simulasi data dengan variasi realistis
    import random
    base_values = [current_aqi + random.randint(-30, 30) for _ in range(days)]
    base_values.append(current_aqi)
    
    # Pastikan tidak negatif
    values = [max(0, v) for v in base_values]
    
    df = pd.DataFrame({
        'Date': dates,
        'AQI': values,
        'Category': [get_aqi_category(v)['category'] for v in values]
    })
    
    return df

# Fungsi untuk prediksi trend sederhana
def predict_aqi_trend(historical_data):
    """Prediksi trend AQI sederhana menggunakan moving average"""
    if len(historical_data) < 3:
        return None
    
    recent_values = historical_data['AQI'].tail(3).values
    trend = recent_values[-1] - recent_values[0]
    predicted_aqi = recent_values[-1] + (trend / 2)
    
    return max(0, min(500, predicted_aqi))

# Fungsi untuk menghitung emisi karbon dari polutan
def calculate_carbon_emissions(pollutants_data):
    """
    Menghitung emisi karbon berdasarkan data polutan
    
    Args:
        pollutants_data (dict): Dictionary berisi data polutan (PM2.5, PM10, SO2, NO2, CO)
    
    Returns:
        dict: Hasil perhitungan emisi karbon dan breakdown
    """
    # Faktor konversi ke CO2 equivalent (ton CO2e per ton polutan)
    # Sumber: IPCC Guidelines dan EPA Emission Factors
    conversion_factors = {
        'PM2.5': 0.05,   # Particulate matter
        'PM10': 0.03,
        'SO2': 1.2,      # Sulfur dioxide
        'NO2': 1.57,     # Nitrogen dioxide (sebagai NOx)
        'CO': 0.57,      # Carbon monoxide
        'VOC': 1.0       # Volatile Organic Compounds
    }
    
    total_co2e = 0
    breakdown = {}
    
    for pollutant, amount_kg_per_day in pollutants_data.items():
        if pollutant in conversion_factors:
            # Konversi ke ton/hari
            amount_ton_per_day = amount_kg_per_day / 1000
            # Hitung CO2 equivalent per tahun
            co2e_per_year = amount_ton_per_day * conversion_factors[pollutant] * 365
            breakdown[pollutant] = {
                'emission_kg_per_day': amount_kg_per_day,
                'emission_ton_per_year': amount_ton_per_day * 365,
                'co2e_ton_per_year': co2e_per_year
            }
            total_co2e += co2e_per_year
    
    # Tambahan emisi dari konsumsi energi (estimasi)
    energy_emission = pollutants_data.get('energy_kwh_per_day', 0) * 0.85 / 1000 * 365  # 0.85 kg CO2/kWh
    
    return {
        'total_co2e_ton_per_year': total_co2e + energy_emission,
        'breakdown': breakdown,
        'energy_emission_ton_per_year': energy_emission,
        'equivalent_trees': int((total_co2e + energy_emission) * 50)  # 1 ton CO2 = ~50 pohon
    }

# Fungsi untuk menghitung carbon credit
def calculate_carbon_credit(current_emission, target_reduction_percent, carbon_price_per_ton=15):
    """
    Menghitung potensi carbon credit
    
    Args:
        current_emission (float): Emisi saat ini (ton CO2e/tahun)
        target_reduction_percent (float): Target pengurangan (%)
        carbon_price_per_ton (float): Harga carbon credit per ton (USD)
    
    Returns:
        dict: Hasil perhitungan carbon credit
    """
    reduction_amount = current_emission * (target_reduction_percent / 100)
    credit_value_usd = reduction_amount * carbon_price_per_ton
    credit_value_idr = credit_value_usd * 15700  # Asumsi kurs USD to IDR
    
    return {
        'reduction_ton_co2e': reduction_amount,
        'credit_value_usd': credit_value_usd,
        'credit_value_idr': credit_value_idr,
        'carbon_price_per_ton': carbon_price_per_ton,
        'payback_months': 0  # Will be calculated based on investment
    }

# Fungsi untuk rekomendasi carbon offset
def get_carbon_offset_recommendations(total_emission):
    """
    Memberikan rekomendasi carbon offset
    
    Args:
        total_emission (float): Total emisi (ton CO2e/tahun)
    
    Returns:
        list: Daftar rekomendasi offset
    """
    recommendations = []
    
    # Rekomendasi berdasarkan skala emisi
    if total_emission > 0:
        trees_needed = int(total_emission * 50)
        area_hectare = trees_needed / 1000  # Asumsi 1000 pohon/ha
        
        recommendations.append({
            'type': 'Reforestasi/Aforestasi',
            'description': f'Tanam {trees_needed:,} pohon (~{area_hectare:.1f} hektar hutan)',
            'cost_estimate_juta': area_hectare * 50,  # Rp 50 juta/ha
            'offset_ton': total_emission,
            'timeline': '5-10 tahun',
            'co_benefits': 'Konservasi biodiversitas, watershed protection'
        })
        
        recommendations.append({
            'type': 'Renewable Energy Credits (REC)',
            'description': 'Beli REC dari proyek renewable energy',
            'cost_estimate_juta': total_emission * 15700 * 12 / 1_000_000,  # $12/ton
            'offset_ton': total_emission,
            'timeline': 'Immediate',
            'co_benefits': 'Mendukung transisi energi bersih'
        })
        
        recommendations.append({
            'type': 'Methane Capture',
            'description': 'Investasi di proyek methane capture (landfill/peternakan)',
            'cost_estimate_juta': total_emission * 15700 * 8 / 1_000_000,  # $8/ton
            'offset_ton': total_emission,
            'timeline': '1-2 tahun',
            'co_benefits': 'Waste management, renewable energy'
        })
        
        recommendations.append({
            'type': 'Blue Carbon',
            'description': 'Restorasi mangrove/coastal ecosystem',
            'cost_estimate_juta': total_emission * 0.5 * 30,  # Rp 30 juta per ton CO2
            'offset_ton': total_emission * 0.5,
            'timeline': '3-5 tahun',
            'co_benefits': 'Coastal protection, fisheries habitat'
        })
    
    return recommendations

# Main Application
def main():
    st.markdown("<h1 class='main-header'>🌍 Smart AQI Monitoring & Recommendation System</h1>", unsafe_allow_html=True)
    st.markdown("### Sistem Peringatan dan Rekomendasi Kualitas Udara Berbasis AI")
    
    # Sidebar
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/2990/2990515.png", width=100)
        st.header("⚙️ Konfigurasi")
        
        # Pilihan perspektif pengguna
        user_perspective = st.selectbox(
            "Pilih Perspektif:",
            ["👥 Masyarakat Umum", "🏭 Industri"],
            key="perspective"
        )
        
        st.markdown("---")
        
        # Input AQI (simulasi dari IoT)
        st.subheader("📊 Input Data AQI")
        input_method = st.radio(
            "Metode Input:",
            ["Manual Input", "Simulasi IoT"]
        )
        
        if input_method == "Manual Input":
            aqi_value = st.slider("Nilai AQI", 0, 500, 85, 5)
        else:
            if st.button("🔄 Ambil Data dari IoT"):
                # Simulasi pembacaan dari IoT
                import random
                aqi_value = random.randint(0, 400)
                st.session_state['aqi_value'] = aqi_value
                st.success(f"Data berhasil diambil: AQI = {aqi_value}")
            
            aqi_value = st.session_state.get('aqi_value', 85)
            st.metric("AQI Terbaca", aqi_value)
        
        st.markdown("---")
        
        # Informasi tambahan
        st.subheader("📍 Informasi Lokasi")
        location = st.text_input("Lokasi", "Jakarta, Indonesia")
        
        if user_perspective == "🏭 Industri":
            st.subheader("🏭 Info Industri")
            industry_type = st.selectbox(
                "Jenis Industri:",
                ["Manufaktur", "Petrokimia", "Pembangkit Listrik", "Semen", "Tekstil", "Lainnya"]
            )
            emission_source = st.multiselect(
                "Sumber Emisi Utama:",
                ["Boiler", "Furnace", "Generator", "Kendaraan", "Proses Produksi"],
                default=["Boiler"]
            )
        
        st.markdown("---")
        st.info("💡 **Tips**: Sistem ini menggunakan Gemini AI untuk memberikan rekomendasi yang personal dan kontekstual.")
    
    # Determine user type
    user_type = "public" if user_perspective == "👥 Masyarakat Umum" else "industry"
    
    # Get AQI category info
    aqi_info = get_aqi_category(aqi_value)
    
    # Main content area
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        st.plotly_chart(create_aqi_gauge(aqi_value), use_container_width=True)
    
    with col2:
        st.markdown(f"""
        <div class='aqi-card {aqi_info['color']}'>
            <h2>{aqi_info['icon']} {aqi_info['category']}</h2>
            <h3>AQI: {aqi_value}</h3>
            <p><strong>PM2.5 Range:</strong> {aqi_info['pm25_range']} μg/m³</p>
            <p><strong>Dampak Kesehatan:</strong> {aqi_info['health_implication']}</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("### 📊 Statistik")
        st.metric("Lokasi", location)
        st.metric("Waktu", datetime.now().strftime("%H:%M"))
        st.metric("Tanggal", datetime.now().strftime("%d/%m/%Y"))
    
    st.markdown("---")
    
    # Tabs untuk berbagai fitur
    if user_type == "public":
        tab1, tab2, tab3, tab4 = st.tabs(["🤖 Rekomendasi AI", "📈 Analisis Trend", "🏥 Info Kesehatan", "📱 Alert System"])
    else:
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["🤖 Rekomendasi AI", "📈 Analisis Trend", "🏭 Compliance", "💰 Cost Analysis", "🌱 Carbon Management"])
    
    with tab1:
        st.header("🤖 Rekomendasi Berbasis AI (Gemini)")
        
        # Additional context input
        additional_info = ""
        if user_type == "public":
            col_a, col_b = st.columns(2)
            with col_a:
                has_condition = st.checkbox("Memiliki kondisi kesehatan khusus?")
                if has_condition:
                    condition = st.text_input("Sebutkan kondisi (misal: asma, jantung)")
                    additional_info += f"Kondisi kesehatan: {condition}. "
            with col_b:
                age_group = st.selectbox("Kelompok usia", ["Anak-anak", "Dewasa", "Lansia"])
                additional_info += f"Kelompok usia: {age_group}. "
        else:
            additional_info = f"Jenis industri: {industry_type}. Sumber emisi: {', '.join(emission_source)}."
        
        if st.button("🔮 Dapatkan Rekomendasi AI", type="primary"):
            with st.spinner("Menganalisis data dan menyusun rekomendasi..."):
                recommendation = get_gemini_recommendation(aqi_value, user_type, additional_info)
                st.markdown("### 📋 Rekomendasi:")
                st.markdown(recommendation)
                
                # Tombol untuk download rekomendasi
                st.download_button(
                    label="📥 Download Rekomendasi (TXT)",
                    data=recommendation,
                    file_name=f"rekomendasi_aqi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
    
    with tab2:
        st.header("📈 Analisis Trend & Prediksi")
        
        # Generate historical data
        historical_data = generate_historical_data(aqi_value, days=7)
        
        # Create line chart
        fig_trend = px.line(
            historical_data,
            x='Date',
            y='AQI',
            title='Trend AQI 7 Hari Terakhir',
            markers=True
        )
        fig_trend.update_traces(line_color='#1f77b4', line_width=3)
        fig_trend.update_layout(hovermode='x unified')
        
        # Add horizontal lines for AQI categories
        fig_trend.add_hline(y=50, line_dash="dash", line_color="green", annotation_text="Good")
        fig_trend.add_hline(y=100, line_dash="dash", line_color="yellow", annotation_text="Moderate")
        fig_trend.add_hline(y=150, line_dash="dash", line_color="orange", annotation_text="Unhealthy (Sensitive)")
        fig_trend.add_hline(y=200, line_dash="dash", line_color="red", annotation_text="Unhealthy")
        
        st.plotly_chart(fig_trend, use_container_width=True)
        
        # Prediction
        predicted_aqi = predict_aqi_trend(historical_data)
        if predicted_aqi:
            pred_info = get_aqi_category(int(predicted_aqi))
            
            col_p1, col_p2 = st.columns(2)
            with col_p1:
                st.metric(
                    "Prediksi AQI Besok",
                    f"{int(predicted_aqi)}",
                    f"{int(predicted_aqi - aqi_value):+d}"
                )
            with col_p2:
                st.metric(
                    "Kategori Prediksi",
                    pred_info['category'],
                    delta_color="inverse"
                )
        
        # Statistics
        st.subheader("📊 Statistik 7 Hari")
        col_s1, col_s2, col_s3, col_s4 = st.columns(4)
        with col_s1:
            st.metric("Rata-rata", f"{historical_data['AQI'].mean():.1f}")
        with col_s2:
            st.metric("Maksimum", f"{historical_data['AQI'].max():.0f}")
        with col_s3:
            st.metric("Minimum", f"{historical_data['AQI'].min():.0f}")
        with col_s4:
            st.metric("Std Dev", f"{historical_data['AQI'].std():.1f}")
    
    with tab3:
        if user_type == "public":
            st.header("🏥 Informasi Kesehatan Detail")
            
            # Health impact by category
            st.subheader("📋 Dampak Kesehatan Berdasarkan Kategori AQI")
            
            health_data = pd.DataFrame({
                'Kategori': ['Good', 'Moderate', 'Unhealthy (Sensitive)', 'Unhealthy', 'Very Unhealthy', 'Hazardous'],
                'AQI Range': ['0-50', '51-100', '101-150', '151-200', '201-300', '301+'],
                'Aktivitas Outdoor': ['Aman', 'Aman untuk sebagian besar', 'Kurangi aktivitas berat', 'Hindari aktivitas berat', 'Hindari semua aktivitas', 'Tetap di dalam'],
                'Penggunaan Masker': ['Tidak perlu', 'Tidak perlu', 'Direkomendasikan (N95)', 'Wajib (N95)', 'Wajib (N95)', 'Wajib (N95/P100)']
            })
            
            st.dataframe(health_data, use_container_width=True)
            
            # Sensitive groups
            st.subheader("⚠️ Kelompok Sensitif")
            st.warning("""
            Kelompok yang lebih rentan terhadap polusi udara:
            - 👶 Bayi dan anak-anak
            - 👴 Lansia (65+ tahun)
            - 🫁 Penderita penyakit pernapasan (asma, PPOK)
            - ❤️ Penderita penyakit jantung
            - 🤰 Ibu hamil
            - 🏃 Orang yang beraktivitas outdoor intensif
            """)
            
            # Emergency contacts
            st.subheader("☎️ Kontak Darurat")
            emergency_col1, emergency_col2 = st.columns(2)
            with emergency_col1:
                st.info("🚑 **Ambulans**: 118 / 119")
                st.info("🏥 **Rumah Sakit Terdekat**: 1500-567")
            with emergency_col2:
                st.info("🔥 **Pemadam Kebakaran**: 113")
                st.info("📞 **Posko Bencana**: 117")
        
        else:  # Industry perspective
            st.header("🏭 Compliance & Regulasi")
            
            # Emission standards
            st.subheader("📜 Baku Mutu Emisi Udara")
            
            standards_data = pd.DataFrame({
                'Parameter': ['PM10', 'PM2.5', 'SO2', 'NO2', 'CO', 'O3'],
                'Satuan': ['μg/m³', 'μg/m³', 'μg/m³', 'μg/m³', 'μg/m³', 'μg/m³'],
                'Baku Mutu (24 jam)': ['150', '55', '75', '150', '10,000', '235'],
                'Status': ['✅ Comply', '⚠️ Warning', '✅ Comply', '✅ Comply', '✅ Comply', '✅ Comply']
            })
            
            st.dataframe(standards_data, use_container_width=True)
            
            # Compliance score
            compliance_score = 85  # Simulasi
            st.subheader("🎯 Skor Kepatuhan Lingkungan")
            
            progress_col1, progress_col2 = st.columns([3, 1])
            with progress_col1:
                st.progress(compliance_score / 100)
            with progress_col2:
                st.metric("Score", f"{compliance_score}%")
            
            if compliance_score >= 90:
                st.success("✅ Status: Excellent Compliance")
            elif compliance_score >= 75:
                st.info("ℹ️ Status: Good Compliance")
            elif compliance_score >= 60:
                st.warning("⚠️ Status: Needs Improvement")
            else:
                st.error("❌ Status: Non-Compliance")
            
            # Regulatory requirements
            st.subheader("📋 Kewajiban Regulasi")
            st.markdown("""
            **Peraturan yang Berlaku:**
            - PP No. 22 Tahun 2021 tentang Perlindungan dan Pengelolaan Lingkungan Hidup
            - Permen LHK No. 13 Tahun 2020 tentang Baku Mutu Emisi
            - Permen LHK No. 7 Tahun 2021 tentang PROPER
            
            **Kewajiban Pelaporan:**
            - ✅ Laporan pemantauan emisi (3 bulan sekali)
            - ✅ Laporan semester ke Dinas Lingkungan Hidup
            - ⚠️ Audit lingkungan (deadline: 2 bulan lagi)
            - ⚠️ Permohonan perpanjangan izin lingkungan
            """)
    
    with tab4:
        if user_type == "public":
            st.header("📱 Sistem Peringatan Otomatis")
            
            # Alert configuration
            st.subheader("⚙️ Konfigurasi Alert")
            
            alert_col1, alert_col2 = st.columns(2)
            with alert_col1:
                enable_alerts = st.checkbox("Aktifkan notifikasi", value=True)
                alert_threshold = st.selectbox(
                    "Threshold peringatan",
                    ["Moderate (51+)", "Unhealthy for Sensitive (101+)", "Unhealthy (151+)"]
                )
            
            with alert_col2:
                alert_methods = st.multiselect(
                    "Metode notifikasi",
                    ["Email", "SMS", "WhatsApp", "Push Notification"],
                    default=["Push Notification"]
                )
                alert_frequency = st.selectbox(
                    "Frekuensi update",
                    ["Real-time", "Setiap 30 menit", "Setiap jam", "2x sehari"]
                )
            
            if enable_alerts:
                st.success("✅ Sistem peringatan aktif")
                
                # Simulate alert history
                st.subheader("📜 Riwayat Peringatan")
                alert_history = pd.DataFrame({
                    'Waktu': [
                        (datetime.now() - timedelta(hours=2)).strftime("%d/%m %H:%M"),
                        (datetime.now() - timedelta(hours=5)).strftime("%d/%m %H:%M"),
                        (datetime.now() - timedelta(days=1)).strftime("%d/%m %H:%M")
                    ],
                    'Level': ['⚠️ Warning', '❌ Alert', 'ℹ️ Info'],
                    'Pesan': [
                        'AQI meningkat ke level Moderate (85)',
                        'AQI mencapai Unhealthy (165) - Hindari aktivitas outdoor',
                        'Kualitas udara membaik ke Good (45)'
                    ]
                })
                st.table(alert_history)
            
            # Location-based alerts
            st.subheader("📍 Alert Berbasis Lokasi")
            st.info("💡 Sistem dapat memberikan peringatan berdasarkan lokasi Anda secara real-time menggunakan GPS.")
            
            # Health tips subscription
            st.subheader("💌 Langganan Tips Kesehatan")
            email_sub = st.text_input("Email untuk tips harian")
            if st.button("Berlangganan"):
                if email_sub:
                    st.success(f"✅ Tips kesehatan akan dikirim ke {email_sub} setiap hari!")
        
        else:  # Industry perspective
            st.header("💰 Analisis Biaya & ROI")
            
            # Cost of pollution
            st.subheader("💸 Estimasi Biaya Dampak Polusi")
            
            # Simulated costs
            current_aqi_normalized = aqi_value / 100
            
            cost_data = {
                'Kategori Biaya': [
                    'Denda & Sanksi Lingkungan',
                    'Biaya Kesehatan Karyawan',
                    'Penurunan Produktivitas',
                    'Reputasi & Brand Image',
                    'Kompensasi Masyarakat'
                ],
                'Biaya per Tahun (Juta Rp)': [
                    round(50 * current_aqi_normalized, 1),
                    round(150 * current_aqi_normalized, 1),
                    round(200 * current_aqi_normalized, 1),
                    round(300 * current_aqi_normalized, 1),
                    round(100 * current_aqi_normalized, 1)
                ]
            }
            
            cost_df = pd.DataFrame(cost_data)
            total_cost = cost_df['Biaya per Tahun (Juta Rp)'].sum()
            
            # Pie chart for cost breakdown
            fig_cost = px.pie(
                cost_df,
                values='Biaya per Tahun (Juta Rp)',
                names='Kategori Biaya',
                title=f'Breakdown Biaya Tahunan (Total: Rp {total_cost:.1f} Juta)'
            )
            st.plotly_chart(fig_cost, use_container_width=True)
            
            # ROI Analysis
            st.subheader("📊 Analisis ROI Investasi Pengendalian Emisi")
            
            investment_col1, investment_col2 = st.columns(2)
            
            with investment_col1:
                st.markdown("**💰 Investasi Teknologi Bersih**")
                investment_amount = st.number_input(
                    "Investasi awal (Juta Rp)",
                    min_value=100,
                    max_value=5000,
                    value=500,
                    step=50
                )
                
                reduction_percentage = st.slider(
                    "Target pengurangan emisi (%)",
                    min_value=10,
                    max_value=80,
                    value=30
                )
            
            with investment_col2:
                st.markdown("**📈 Perhitungan Benefit**")
                
                annual_savings = total_cost * (reduction_percentage / 100)
                payback_period = investment_amount / annual_savings if annual_savings > 0 else 0
                roi_5_year = ((annual_savings * 5 - investment_amount) / investment_amount * 100)
                
                st.metric("Penghematan Tahunan", f"Rp {annual_savings:.1f} Jt")
                st.metric("Payback Period", f"{payback_period:.1f} tahun")
                st.metric("ROI (5 tahun)", f"{roi_5_year:.1f}%")
            
            # Investment recommendations
            st.subheader("🔧 Rekomendasi Investasi Teknologi")
            
            tech_recommendations = pd.DataFrame({
                'Teknologi': [
                    'Electrostatic Precipitator (ESP)',
                    'Bag Filter System',
                    'Scrubber (Wet/Dry)',
                    'Continuous Emission Monitoring',
                    'Renewable Energy Integration'
                ],
                'Investasi (Juta Rp)': [800, 600, 500, 200, 1500],
                'Efisiensi Reduksi': ['85-95%', '99%', '90-95%', 'N/A', '50-70%'],
                'Payback (tahun)': [3.5, 2.8, 3.2, 1.5, 6.5],
                'Prioritas': ['⭐⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐', '⭐⭐⭐⭐⭐', '⭐⭐⭐']
            })
            
            st.dataframe(tech_recommendations, use_container_width=True)
            
            # Green incentives
            st.subheader("🌿 Insentif & Program Pemerintah")
            st.info("""
            **Program yang Tersedia:**
            - 💚 **PROPER Hijau/Emas**: Tax allowance hingga 30% dari investasi
            - 🏭 **Program Efisiensi Energi**: Subsidi audit energi hingga 50%
            - 🌱 **Carbon Credit**: Potensi pendapatan dari perdagangan karbon
            - 📜 **Green Bond**: Akses pembiayaan berbunga rendah untuk proyek hijau
            - 🎓 **Bantuan Pelatihan**: Subsidi pelatihan SDM lingkungan
            """)
    
    # Tab Carbon Management (hanya untuk industri)
    if user_type == "industry":
        with tab5:
            st.header("🌱 Carbon Emission & Carbon Credit Management")
            
            st.info("💡 **Sistem ini membantu menghitung emisi karbon dari polutan industri dan memberikan rekomendasi carbon offset**")
            
            # Input data polutan
            st.subheader("📊 Input Data Polutan Harian")
            
            col_input1, col_input2 = st.columns(2)
            
            with col_input1:
                st.markdown("**Emisi Partikulat**")
                pm25_kg = st.number_input("PM2.5 (kg/hari)", min_value=0.0, value=50.0, step=5.0, help="Particulate Matter 2.5 mikron")
                pm10_kg = st.number_input("PM10 (kg/hari)", min_value=0.0, value=100.0, step=10.0, help="Particulate Matter 10 mikron")
                
                st.markdown("**Emisi Gas**")
                so2_kg = st.number_input("SO₂ (kg/hari)", min_value=0.0, value=30.0, step=5.0, help="Sulfur Dioxide")
                no2_kg = st.number_input("NO₂ (kg/hari)", min_value=0.0, value=40.0, step=5.0, help="Nitrogen Dioxide")
            
            with col_input2:
                co_kg = st.number_input("CO (kg/hari)", min_value=0.0, value=80.0, step=10.0, help="Carbon Monoxide")
                voc_kg = st.number_input("VOC (kg/hari)", min_value=0.0, value=25.0, step=5.0, help="Volatile Organic Compounds")
                
                st.markdown("**Konsumsi Energi**")
                energy_kwh = st.number_input("Listrik (kWh/hari)", min_value=0.0, value=5000.0, step=100.0, help="Konsumsi listrik harian")
            
            # Hitung emisi karbon
            pollutants_data = {
                'PM2.5': pm25_kg,
                'PM10': pm10_kg,
                'SO2': so2_kg,
                'NO2': no2_kg,
                'CO': co_kg,
                'VOC': voc_kg,
                'energy_kwh_per_day': energy_kwh
            }
            
            if st.button("🧮 Hitung Emisi Karbon", type="primary"):
                with st.spinner("Menghitung emisi karbon..."):
                    carbon_result = calculate_carbon_emissions(pollutants_data)
                    
                    st.markdown("---")
                    st.subheader("📈 Hasil Perhitungan Emisi Karbon")
                    
                    # Tampilkan total emisi
                    metric_col1, metric_col2, metric_col3 = st.columns(3)
                    with metric_col1:
                        st.metric(
                            "Total Emisi CO₂e",
                            f"{carbon_result['total_co2e_ton_per_year']:.2f} ton/tahun",
                            help="Total emisi setara CO2 per tahun"
                        )
                    with metric_col2:
                        st.metric(
                            "Setara Pohon Dibutuhkan",
                            f"{carbon_result['equivalent_trees']:,} pohon",
                            help="Jumlah pohon untuk menyerap emisi ini"
                        )
                    with metric_col3:
                        st.metric(
                            "Emisi dari Energi",
                            f"{carbon_result['energy_emission_ton_per_year']:.2f} ton/tahun",
                            help="Emisi dari konsumsi listrik"
                        )
                    
                    # Breakdown emisi per polutan
                    st.markdown("### 📊 Breakdown Emisi per Polutan")
                    
                    breakdown_data = []
                    for pollutant, data in carbon_result['breakdown'].items():
                        breakdown_data.append({
                            'Polutan': pollutant,
                            'Emisi (kg/hari)': f"{data['emission_kg_per_day']:.2f}",
                            'Emisi (ton/tahun)': f"{data['emission_ton_per_year']:.2f}",
                            'CO₂e (ton/tahun)': f"{data['co2e_ton_per_year']:.2f}"
                        })
                    
                    df_breakdown = pd.DataFrame(breakdown_data)
                    st.dataframe(df_breakdown, use_container_width=True)
                    
                    # Visualisasi pie chart
                    if breakdown_data:
                        fig_emission = px.pie(
                            df_breakdown,
                            values=[float(x['CO₂e (ton/tahun)']) for x in breakdown_data],
                            names=[x['Polutan'] for x in breakdown_data],
                            title='Kontribusi Emisi CO₂e per Polutan'
                        )
                        st.plotly_chart(fig_emission, use_container_width=True)
                    
                    # Simpan hasil ke session state
                    st.session_state['carbon_emission'] = carbon_result['total_co2e_ton_per_year']
                    
                    st.markdown("---")
                    
                    # Rekomendasi AI untuk pengurangan emisi
                    st.subheader("🤖 Rekomendasi AI untuk Pengurangan Emisi")
                    
                    if st.button("🔮 Dapatkan Rekomendasi Pengurangan Emisi"):
                        with st.spinner("Menganalisis emisi dan menyusun rekomendasi..."):
                            # Buat prompt untuk Gemini
                            emission_prompt = f"""
Sebagai konsultan karbon dan keberlanjutan industri, berikan rekomendasi untuk mengurangi emisi karbon.

DATA EMISI KARBON:
- Total Emisi CO₂e: {carbon_result['total_co2e_ton_per_year']:.2f} ton/tahun
- Emisi dari Energi: {carbon_result['energy_emission_ton_per_year']:.2f} ton/tahun
- Jenis Industri: {industry_type}
- Sumber Emisi Utama: {', '.join(emission_source)}

BREAKDOWN EMISI:
{chr(10).join([f"- {p}: {d['co2e_ton_per_year']:.2f} ton CO₂e/tahun" for p, d in carbon_result['breakdown'].items()])}

Berikan rekomendasi dalam format:

1. ANALISIS EMISI
   Evaluasi level emisi dan perbandingan dengan industri sejenis

2. PRIORITAS PENGURANGAN
   Area mana yang harus diprioritaskan untuk pengurangan emisi (minimal 5 prioritas)

3. TEKNOLOGI & METODE
   Teknologi dan metode spesifik untuk mengurangi emisi dari setiap polutan

4. QUICK WINS (0-6 bulan)
   Tindakan cepat yang bisa langsung diimplementasikan

5. MEDIUM-TERM (6-18 bulan)
   Program jangka menengah dengan investasi moderat

6. LONG-TERM (18+ bulan)
   Transformasi besar dan investasi strategis

7. ESTIMASI BIAYA & SAVINGS
   Perkiraan investasi dan penghematan untuk setiap rekomendasi

8. RENEWABLE ENERGY
   Rekomendasi transisi ke energi terbarukan

9. MONITORING & VERIFICATION
   Sistem monitoring untuk memverifikasi pengurangan emisi

Gunakan bahasa profesional dalam Bahasa Indonesia dan berikan angka spesifik.
"""
                            
                            try:
                                model = genai.GenerativeModel('gemini-2.0-flash-exp')
                                response = model.generate_content(emission_prompt)
                                st.markdown(response.text)
                                
                                # Tombol download
                                st.download_button(
                                    label="📥 Download Rekomendasi Pengurangan Emisi",
                                    data=response.text,
                                    file_name=f"rekomendasi_pengurangan_emisi_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                                    mime="text/plain"
                                )
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
            
            # Carbon Credit Calculator
            st.markdown("---")
            st.subheader("💰 Kalkulator Carbon Credit")
            
            st.info("💡 **Carbon credit** adalah sertifikat yang mewakili pengurangan 1 ton CO₂e. Dapat dijual di pasar karbon untuk menghasilkan revenue.")
            
            if 'carbon_emission' in st.session_state:
                current_emission = st.session_state['carbon_emission']
                
                credit_col1, credit_col2 = st.columns(2)
                
                with credit_col1:
                    st.markdown("**Skenario Pengurangan**")
                    target_reduction = st.slider(
                        "Target Pengurangan Emisi (%)",
                        min_value=5,
                        max_value=80,
                        value=30,
                        step=5,
                        help="Persentase pengurangan dari emisi saat ini"
                    )
                    
                    carbon_price = st.number_input(
                        "Harga Carbon Credit (USD/ton CO₂e)",
                        min_value=5.0,
                        max_value=100.0,
                        value=15.0,
                        step=1.0,
                        help="Harga pasar carbon credit (rata-rata global: $10-30/ton)"
                    )
                
                with credit_col2:
                    # Hitung carbon credit
                    credit_result = calculate_carbon_credit(current_emission, target_reduction, carbon_price)
                    
                    st.markdown("**Potensi Carbon Credit**")
                    st.metric(
                        "Pengurangan Emisi",
                        f"{credit_result['reduction_ton_co2e']:.2f} ton CO₂e/tahun"
                    )
                    st.metric(
                        "Nilai Credit (USD)",
                        f"${credit_result['credit_value_usd']:,.2f}/tahun"
                    )
                    st.metric(
                        "Nilai Credit (IDR)",
                        f"Rp {credit_result['credit_value_idr']:,.0f}/tahun"
                    )
                
                # ROI Analysis untuk Carbon Credit
                st.markdown("### 📊 Analisis ROI Carbon Credit Program")
                
                investment_for_reduction = st.number_input(
                    "Investasi untuk Mencapai Pengurangan (Juta Rp)",
                    min_value=10,
                    max_value=10000,
                    value=500,
                    step=50,
                    help="Total investasi teknologi/program untuk mencapai target pengurangan"
                )
                
                # Hitung ROI
                annual_revenue = credit_result['credit_value_idr'] / 1_000_000  # Dalam juta
                payback_years = investment_for_reduction / annual_revenue if annual_revenue > 0 else 0
                roi_5_years = ((annual_revenue * 5 - investment_for_reduction) / investment_for_reduction * 100) if investment_for_reduction > 0 else 0
                
                roi_col1, roi_col2, roi_col3 = st.columns(3)
                with roi_col1:
                    st.metric("Revenue Tahunan dari Credit", f"Rp {annual_revenue:.1f} Jt")
                with roi_col2:
                    st.metric("Payback Period", f"{payback_years:.1f} tahun")
                with roi_col3:
                    st.metric("ROI (5 tahun)", f"{roi_5_years:.1f}%")
                
                # Pathway to Net Zero
                st.markdown("### 🎯 Pathway to Net Zero")
                
                years_to_net_zero = st.slider(
                    "Target Net Zero (tahun)",
                    min_value=5,
                    max_value=30,
                    value=15,
                    help="Tahun target untuk mencapai net zero emission"
                )
                
                # Hitung trajectory
                annual_reduction_rate = 100 / years_to_net_zero
                remaining_emission_per_year = []
                years = []
                
                for year in range(years_to_net_zero + 1):
                    remaining = current_emission * (1 - (annual_reduction_rate * year / 100))
                    remaining_emission_per_year.append(max(0, remaining))
                    years.append(datetime.now().year + year)
                
                # Plot trajectory
                df_trajectory = pd.DataFrame({
                    'Tahun': years,
                    'Emisi (ton CO₂e)': remaining_emission_per_year
                })
                
                fig_trajectory = px.line(
                    df_trajectory,
                    x='Tahun',
                    y='Emisi (ton CO₂e)',
                    title=f'Pathway to Net Zero ({years_to_net_zero} Tahun)',
                    markers=True
                )
                fig_trajectory.add_hline(y=0, line_dash="dash", line_color="green", annotation_text="Net Zero Target")
                st.plotly_chart(fig_trajectory, use_container_width=True)
                
                # Carbon Offset Recommendations
                st.markdown("---")
                st.subheader("🌳 Rekomendasi Carbon Offset")
                
                st.info("💡 **Carbon offset** adalah cara mengkompensasi emisi yang tidak bisa dihindari dengan mendukung proyek pengurangan emisi di tempat lain.")
                
                offset_recommendations = get_carbon_offset_recommendations(current_emission)
                
                for i, rec in enumerate(offset_recommendations):
                    with st.expander(f"{i+1}. {rec['type']}", expanded=(i==0)):
                        st.markdown(f"**Deskripsi:** {rec['description']}")
                        
                        rec_col1, rec_col2, rec_col3 = st.columns(3)
                        with rec_col1:
                            st.metric("Offset Potential", f"{rec['offset_ton']:.1f} ton CO₂e")
                        with rec_col2:
                            st.metric("Estimasi Biaya", f"Rp {rec['cost_estimate_juta']:.1f} Juta")
                        with rec_col3:
                            st.metric("Timeline", rec['timeline'])
                        
                        st.markdown(f"**Co-benefits:** {rec['co_benefits']}")
                        
                        # Hitung biaya per ton
                        cost_per_ton = rec['cost_estimate_juta'] * 1_000_000 / rec['offset_ton'] if rec['offset_ton'] > 0 else 0
                        st.caption(f"💰 Biaya per ton CO₂e: Rp {cost_per_ton:,.0f}")
                
                # Action Plan
                st.markdown("---")
                st.subheader("📋 Action Plan Carbon Management")
                
                st.markdown("""
                **Langkah-langkah Implementasi:**
                
                1. **Baseline Assessment (Bulan 1-2)**
                   - Audit emisi lengkap dengan pihak ketiga
                   - Verifikasi data dan identifikasi hotspot
                   - Set baseline year dan boundary
                
                2. **Target Setting (Bulan 2-3)**
                   - Tentukan target pengurangan (Science-Based Targets)
                   - Align dengan Paris Agreement
                   - Commitment dari top management
                
                3. **Quick Wins Implementation (Bulan 3-6)**
                   - Energy efficiency measures
                   - Waste reduction
                   - Operational optimization
                
                4. **Technology Investment (Bulan 6-18)**
                   - Install emission control technology
                   - Renewable energy integration
                   - Process innovation
                
                5. **Carbon Credit Development (Bulan 12-24)**
                   - Identify eligible reduction activities
                   - Register dengan standard (Gold Standard, VCS)
                   - Verification dan issuance
                
                6. **Offset Strategy (Ongoing)**
                   - Purchase verified carbon credits
                   - Invest in offset projects
                   - Portfolio diversification
                
                7. **Monitoring & Reporting (Continuous)**
                   - Monthly emission tracking
                   - Annual sustainability report
                   - Disclosure (CDP, GRI, TCFD)
                """)
                
                # Sertifikasi dan Standard
                st.markdown("### 🏆 Sertifikasi & Standard Carbon")
                
                cert_col1, cert_col2 = st.columns(2)
                
                with cert_col1:
                    st.markdown("""
                    **Carbon Credit Standards:**
                    - ✅ **Verified Carbon Standard (VCS)**
                    - ✅ **Gold Standard**
                    - ✅ **Climate Action Reserve (CAR)**
                    - ✅ **American Carbon Registry (ACR)**
                    """)
                
                with cert_col2:
                    st.markdown("""
                    **Disclosure Frameworks:**
                    - 📊 **CDP (Carbon Disclosure Project)**
                    - 📊 **GRI (Global Reporting Initiative)**
                    - 📊 **TCFD (Task Force on Climate)**
                    - 📊 **ISO 14064 (GHG Accounting)**
                    """)
            
            else:
                st.warning("⚠️ Silakan hitung emisi karbon terlebih dahulu di bagian atas untuk mengakses kalkulator carbon credit.")
    
    # Footer
    st.markdown("---")
    footer_col1, footer_col2, footer_col3 = st.columns(3)
    
    with footer_col1:
        st.markdown("**📊 Data Source**")
        st.caption("IoT Air Quality Sensors")
        st.caption("Real-time monitoring")
    
    with footer_col2:
        st.markdown("**🤖 AI Technology**")
        st.caption("Powered by Google Gemini")
        st.caption("Advanced recommendation engine")
    
    with footer_col3:
        st.markdown("**📱 Support**")
        st.caption("24/7 Monitoring")
        st.caption("help@smartaqi.id")
    
    st.caption("© 2025 Smart AQI System | Untuk Indonesia yang lebih sehat 🇮🇩")

if __name__ == "__main__":
    main()
