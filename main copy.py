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
        tab1, tab2, tab3, tab4 = st.tabs(["🤖 Rekomendasi AI", "📈 Analisis Trend", "🏭 Compliance", "💰 Cost Analysis"])
    
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
