import streamlit as st
import google.generativeai as genai
from datetime import datetime
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import plotly.graph_objects as go
import plotly.express as px

# Konfigurasi halaman
st.set_page_config(
    page_title="Smart AQI System",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# API Key
try:
    GEMINI_API_KEY = st.secrets.get("GEMINI_API_KEY", "")
except:
    GEMINI_API_KEY = ""
genai.configure(api_key=GEMINI_API_KEY)

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
    .very-unhealthy { background: linear-gradient(135deg, #d946ef 0%, #c026d3 100%); color: white; }
    .hazardous { background: linear-gradient(135deg, #8e44ad 0%, #c0392b 100%); color: white; }
    .rag-info {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# ===========================
# RAG SYSTEM FUNCTIONS
# ===========================

@st.cache_data
def load_datasets():
    """Load dan preprocess dataset untuk RAG"""
    try:
        # Load Klasifikasi AQI Air (global data)
        df_global = pd.read_csv('Klasifikasi AQI Air.csv')
        
        # Load pollution dataset
        df_pollution = pd.read_csv('pollution_dataset.csv', sep=';')
        
        return df_global, df_pollution
    except Exception as e:
        st.error(f"Error loading datasets: {str(e)}")
        return None, None

@st.cache_data
def create_knowledge_base(df_global, df_pollution):
    """Membuat knowledge base dari dataset untuk RAG"""
    knowledge_base = []
    
    # 1. Extract knowledge dari global AQI data
    if df_global is not None:
        # Agregasi data per negara
        country_stats = df_global.groupby('Country').agg({
            'AQI Value': ['mean', 'min', 'max', 'std'],
            'Status': lambda x: x.mode()[0] if len(x) > 0 else 'Unknown'
        }).reset_index()
        
        country_stats.columns = ['Country', 'Mean_AQI', 'Min_AQI', 'Max_AQI', 'Std_AQI', 'Most_Common_Status']
        
        for _, row in country_stats.iterrows():
            knowledge_base.append({
                'type': 'global_stats',
                'content': f"Negara {row['Country']} memiliki rata-rata AQI {row['Mean_AQI']:.1f} dengan status paling umum {row['Most_Common_Status']}. Range AQI dari {row['Min_AQI']} hingga {row['Max_AQI']}.",
                'metadata': {
                    'country': row['Country'],
                    'mean_aqi': row['Mean_AQI'],
                    'status': row['Most_Common_Status']
                }
            })
        
        # Agregasi data per status
        status_stats = df_global.groupby('Status').agg({
            'AQI Value': ['mean', 'count', 'min', 'max']
        }).reset_index()
        
        status_stats.columns = ['Status', 'Mean_AQI', 'Count', 'Min_AQI', 'Max_AQI']
        
        for _, row in status_stats.iterrows():
            knowledge_base.append({
                'type': 'status_distribution',
                'content': f"Status {row['Status']} memiliki {row['Count']} kejadian dengan rata-rata AQI {row['Mean_AQI']:.1f} (range: {row['Min_AQI']}-{row['Max_AQI']}).",
                'metadata': {
                    'status': row['Status'],
                    'count': row['Count'],
                    'mean_aqi': row['Mean_AQI']
                }
            })
    
    # 2. Extract knowledge dari pollution dataset
    if df_pollution is not None:
        # Analisis per kategori kualitas udara
        quality_stats = df_pollution.groupby('Air Quality').agg({
            'PM2.5': 'mean',
            'PM10': 'mean',
            'NO2': 'mean',
            'SO2': 'mean',
            'CO': 'mean',
            'Temperature': 'mean',
            'Humidity': 'mean',
            'Proximity_to_Industrial_Areas': 'mean',
            'Population_Density': 'mean'
        }).reset_index()
        
        for _, row in quality_stats.iterrows():
            knowledge_base.append({
                'type': 'pollution_profile',
                'content': f"Kualitas udara {row['Air Quality']} biasanya memiliki PM2.5: {row['PM2.5']:.1f}, PM10: {row['PM10']:.1f}, NO2: {row['NO2']:.1f}, SO2: {row['SO2']:.1f}, CO: {row['CO']:.2f}. Rata-rata suhu {row['Temperature']:.1f}°C, kelembaban {row['Humidity']:.1f}%, jarak ke area industri {row['Proximity_to_Industrial_Areas']:.1f}km, kepadatan populasi {row['Population_Density']:.0f}.",
                'metadata': {
                    'air_quality': row['Air Quality'],
                    'pm25': row['PM2.5'],
                    'pm10': row['PM10'],
                    'no2': row['NO2'],
                    'so2': row['SO2'],
                    'co': row['CO']
                }
            })
        
        # Korelasi polutan dengan kualitas udara
        pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO']
        for pollutant in pollutants:
            correlation_data = df_pollution.groupby('Air Quality')[pollutant].mean().to_dict()
            knowledge_base.append({
                'type': 'pollutant_correlation',
                'content': f"Polutan {pollutant} memiliki distribusi: " + ", ".join([f"{quality}: {value:.1f}" for quality, value in correlation_data.items()]),
                'metadata': {
                    'pollutant': pollutant,
                    'distribution': correlation_data
                }
            })
    
    # 3. Expert knowledge tentang AQI
    expert_knowledge = [
        {
            'type': 'expert_guideline',
            'content': "AQI 0-50 (Good): Kualitas udara sangat baik, tidak ada risiko kesehatan. Aktivitas outdoor aman untuk semua kelompok.",
            'metadata': {'aqi_range': '0-50', 'status': 'Good', 'risk_level': 'minimal'}
        },
        {
            'type': 'expert_guideline',
            'content': "AQI 51-100 (Moderate): Kualitas udara dapat diterima. Kelompok sensitif (anak-anak, lansia, penderita asma) sebaiknya membatasi aktivitas outdoor yang berkepanjangan.",
            'metadata': {'aqi_range': '51-100', 'status': 'Moderate', 'risk_level': 'low'}
        },
        {
            'type': 'expert_guideline',
            'content': "AQI 101-150 (Unhealthy for Sensitive Groups): Kelompok sensitif dapat mengalami efek kesehatan. Gunakan masker N95 untuk aktivitas outdoor, kurangi durasi aktivitas luar ruangan.",
            'metadata': {'aqi_range': '101-150', 'status': 'Unhealthy for Sensitive Groups', 'risk_level': 'moderate'}
        },
        {
            'type': 'expert_guideline',
            'content': "AQI 151-200 (Unhealthy): Semua orang dapat mengalami efek kesehatan. Hindari aktivitas outdoor, gunakan air purifier indoor, konsultasi dokter jika ada gejala.",
            'metadata': {'aqi_range': '151-200', 'status': 'Unhealthy', 'risk_level': 'high'}
        },
        {
            'type': 'expert_guideline',
            'content': "AQI 201-300 (Very Unhealthy): Peringatan kesehatan serius. Tetap di dalam ruangan, tutup semua jendela dan pintu, gunakan air purifier HEPA.",
            'metadata': {'aqi_range': '201-300', 'status': 'Very Unhealthy', 'risk_level': 'very_high'}
        },
        {
            'type': 'expert_guideline',
            'content': "AQI 301+ (Hazardous): Kondisi darurat kesehatan. Evakuasi jika memungkinkan, gunakan respirator, tetap indoor dengan ventilasi tersegel.",
            'metadata': {'aqi_range': '301+', 'status': 'Hazardous', 'risk_level': 'emergency'}
        },
        {
            'type': 'industrial_guideline',
            'content': "Industri dengan emisi PM2.5 tinggi harus menginstall Electrostatic Precipitator (ESP) atau Bag Filter untuk mencapai efisiensi removal >99%. Target emisi PM2.5 <50 mg/Nm³.",
            'metadata': {'pollutant': 'PM2.5', 'technology': 'ESP/Bag Filter', 'efficiency': '>99%'}
        },
        {
            'type': 'industrial_guideline',
            'content': "Untuk mengurangi NOx, gunakan Selective Catalytic Reduction (SCR) atau Low NOx Burner. Target emisi NOx <200 mg/Nm³ untuk industri baru.",
            'metadata': {'pollutant': 'NOx', 'technology': 'SCR/Low NOx Burner', 'target': '<200 mg/Nm³'}
        },
        {
            'type': 'industrial_guideline',
            'content': "SO2 dapat dikurangi dengan Flue Gas Desulfurization (FGD) menggunakan wet scrubber atau dry sorbent injection. Efisiensi removal 90-98%.",
            'metadata': {'pollutant': 'SO2', 'technology': 'FGD', 'efficiency': '90-98%'}
        },
        {
            'type': 'health_guideline',
            'content': "PM2.5 >35 µg/m³ meningkatkan risiko penyakit kardiovaskular dan pernapasan. Kelompok berisiko: anak <5 tahun, lansia >65 tahun, penderita asma/COPD.",
            'metadata': {'pollutant': 'PM2.5', 'threshold': '35 µg/m³', 'health_impact': 'cardiovascular & respiratory'}
        },
        {
            'type': 'health_guideline',
            'content': "Paparan NO2 jangka pendek >200 µg/m³ dapat menyebabkan iritasi saluran pernapasan. Paparan kronis meningkatkan risiko asma pada anak-anak.",
            'metadata': {'pollutant': 'NO2', 'threshold': '200 µg/m³', 'health_impact': 'respiratory irritation'}
        }
    ]
    
    knowledge_base.extend(expert_knowledge)
    
    return knowledge_base

@st.cache_resource
def create_rag_retriever(_knowledge_base):
    """Membuat retriever menggunakan TF-IDF untuk similarity search"""
    # Extract semua content untuk vectorization
    documents = [kb['content'] for kb in _knowledge_base]
    
    # TF-IDF Vectorizer
    vectorizer = TfidfVectorizer(max_features=500, stop_words='english')
    doc_vectors = vectorizer.fit_transform(documents)
    
    return vectorizer, doc_vectors, _knowledge_base

def retrieve_relevant_knowledge(query, vectorizer, doc_vectors, knowledge_base, top_k=5):
    """Retrieve top-k most relevant knowledge pieces"""
    # Vectorize query
    query_vector = vectorizer.transform([query])
    
    # Calculate cosine similarity
    similarities = cosine_similarity(query_vector, doc_vectors).flatten()
    
    # Get top-k indices
    top_indices = np.argsort(similarities)[-top_k:][::-1]
    
    # Return relevant knowledge
    relevant_kb = []
    for idx in top_indices:
        if similarities[idx] > 0.01:  # Threshold untuk relevance
            relevant_kb.append({
                **knowledge_base[idx],
                'similarity_score': similarities[idx]
            })
    
    return relevant_kb

# ===========================
# AQI CALCULATION FUNCTIONS
# ===========================

def calculate_aqi_from_pollutants(pm25, pm10, no2, so2, co, o3=None):
    """Hitung AQI dari konsentrasi polutan"""
    
    def calculate_individual_aqi(concentration, breakpoints):
        """Hitung AQI individual untuk satu polutan"""
        for bp in breakpoints:
            if bp['c_low'] <= concentration <= bp['c_high']:
                aqi = ((bp['i_high'] - bp['i_low']) / (bp['c_high'] - bp['c_low'])) * \
                      (concentration - bp['c_low']) + bp['i_low']
                return round(aqi)
        
        # Jika di luar range, gunakan kategori tertinggi
        if concentration > breakpoints[-1]['c_high']:
            return 500
        return 0
    
    # Breakpoints untuk PM2.5 (µg/m³, 24-hour average)
    pm25_bp = [
        {'c_low': 0.0, 'c_high': 12.0, 'i_low': 0, 'i_high': 50},
        {'c_low': 12.1, 'c_high': 35.4, 'i_low': 51, 'i_high': 100},
        {'c_low': 35.5, 'c_high': 55.4, 'i_low': 101, 'i_high': 150},
        {'c_low': 55.5, 'c_high': 150.4, 'i_low': 151, 'i_high': 200},
        {'c_low': 150.5, 'c_high': 250.4, 'i_low': 201, 'i_high': 300},
        {'c_low': 250.5, 'c_high': 500.4, 'i_low': 301, 'i_high': 500}
    ]
    
    # Breakpoints untuk PM10 (µg/m³, 24-hour average)
    pm10_bp = [
        {'c_low': 0, 'c_high': 54, 'i_low': 0, 'i_high': 50},
        {'c_low': 55, 'c_high': 154, 'i_low': 51, 'i_high': 100},
        {'c_low': 155, 'c_high': 254, 'i_low': 101, 'i_high': 150},
        {'c_low': 255, 'c_high': 354, 'i_low': 151, 'i_high': 200},
        {'c_low': 355, 'c_high': 424, 'i_low': 201, 'i_high': 300},
        {'c_low': 425, 'c_high': 604, 'i_low': 301, 'i_high': 500}
    ]
    
    # Breakpoints untuk NO2 (ppb, 1-hour average)
    no2_bp = [
        {'c_low': 0, 'c_high': 53, 'i_low': 0, 'i_high': 50},
        {'c_low': 54, 'c_high': 100, 'i_low': 51, 'i_high': 100},
        {'c_low': 101, 'c_high': 360, 'i_low': 101, 'i_high': 150},
        {'c_low': 361, 'c_high': 649, 'i_low': 151, 'i_high': 200},
        {'c_low': 650, 'c_high': 1249, 'i_low': 201, 'i_high': 300},
        {'c_low': 1250, 'c_high': 2049, 'i_low': 301, 'i_high': 500}
    ]
    
    # Breakpoints untuk SO2 (ppb, 1-hour average)
    so2_bp = [
        {'c_low': 0, 'c_high': 35, 'i_low': 0, 'i_high': 50},
        {'c_low': 36, 'c_high': 75, 'i_low': 51, 'i_high': 100},
        {'c_low': 76, 'c_high': 185, 'i_low': 101, 'i_high': 150},
        {'c_low': 186, 'c_high': 304, 'i_low': 151, 'i_high': 200},
        {'c_low': 305, 'c_high': 604, 'i_low': 201, 'i_high': 300},
        {'c_low': 605, 'c_high': 1004, 'i_low': 301, 'i_high': 500}
    ]
    
    # Breakpoints untuk CO (ppm, 8-hour average)
    co_bp = [
        {'c_low': 0.0, 'c_high': 4.4, 'i_low': 0, 'i_high': 50},
        {'c_low': 4.5, 'c_high': 9.4, 'i_low': 51, 'i_high': 100},
        {'c_low': 9.5, 'c_high': 12.4, 'i_low': 101, 'i_high': 150},
        {'c_low': 12.5, 'c_high': 15.4, 'i_low': 151, 'i_high': 200},
        {'c_low': 15.5, 'c_high': 30.4, 'i_low': 201, 'i_high': 300},
        {'c_low': 30.5, 'c_high': 50.4, 'i_low': 301, 'i_high': 500}
    ]
    
    # Hitung AQI untuk setiap polutan
    aqi_values = []
    
    if pm25 is not None and pm25 >= 0:
        aqi_values.append(calculate_individual_aqi(pm25, pm25_bp))
    
    if pm10 is not None and pm10 >= 0:
        aqi_values.append(calculate_individual_aqi(pm10, pm10_bp))
    
    if no2 is not None and no2 >= 0:
        aqi_values.append(calculate_individual_aqi(no2, no2_bp))
    
    if so2 is not None and so2 >= 0:
        aqi_values.append(calculate_individual_aqi(so2, so2_bp))
    
    if co is not None and co >= 0:
        aqi_values.append(calculate_individual_aqi(co, co_bp))
    
    # AQI final adalah maksimum dari semua AQI individual
    if aqi_values:
        return max(aqi_values)
    return 0

def get_aqi_category(aqi):
    """Dapatkan kategori AQI"""
    if aqi <= 50:
        return "Good", "good"
    elif aqi <= 100:
        return "Moderate", "moderate"
    elif aqi <= 150:
        return "Unhealthy for Sensitive Groups", "unhealthy-sensitive"
    elif aqi <= 200:
        return "Unhealthy", "unhealthy"
    elif aqi <= 300:
        return "Very Unhealthy", "very-unhealthy"
    else:
        return "Hazardous", "hazardous"

def create_aqi_gauge(aqi_value):
    """Buat gauge chart untuk AQI"""
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=aqi_value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': "Air Quality Index (AQI)", 'font': {'size': 24}},
        delta={'reference': 50, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={
            'axis': {'range': [None, 500], 'tickwidth': 1, 'tickcolor': "darkblue"},
            'bar': {'color': "darkblue"},
            'bgcolor': "white",
            'borderwidth': 2,
            'bordercolor': "gray",
            'steps': [
                {'range': [0, 50], 'color': '#00E400'},
                {'range': [50, 100], 'color': '#FFFF00'},
                {'range': [100, 150], 'color': '#FF7E00'},
                {'range': [150, 200], 'color': '#FF0000'},
                {'range': [200, 300], 'color': '#8F3F97'},
                {'range': [300, 500], 'color': '#7E0023'}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': aqi_value
            }
        }
    ))
    
    fig.update_layout(height=400, margin=dict(l=20, r=20, t=60, b=20))
    return fig

def get_rag_enhanced_recommendation(aqi, category, pollutants_data, user_type, vectorizer, doc_vectors, knowledge_base):
    """Dapatkan rekomendasi dengan RAG enhancement"""
    
    # 1. Buat query untuk retrieval
    query = f"""
    Air quality status {category} with AQI {aqi}.
    Pollutants: PM2.5={pollutants_data.get('PM2.5', 0)}, PM10={pollutants_data.get('PM10', 0)}, 
    NO2={pollutants_data.get('NO2', 0)}, SO2={pollutants_data.get('SO2', 0)}, CO={pollutants_data.get('CO', 0)}.
    User type: {user_type}
    """
    
    # 2. Retrieve relevant knowledge
    relevant_knowledge = retrieve_relevant_knowledge(query, vectorizer, doc_vectors, knowledge_base, top_k=8)
    
    # 3. Construct context dari retrieved knowledge
    context = "=== RELEVANT KNOWLEDGE FROM DATABASE ===\n\n"
    for i, kb in enumerate(relevant_knowledge, 1):
        context += f"{i}. [{kb['type']}] {kb['content']}\n"
        context += f"   (Relevance: {kb['similarity_score']:.3f})\n\n"
    
    # 4. Generate prompt untuk Gemini dengan RAG context
    if user_type == "public":
        prompt = f"""
Anda adalah asisten kesehatan lingkungan yang ahli dalam kualitas udara.

{context}

SITUASI SAAT INI:
- AQI: {aqi} ({category})
- Data Polutan:
  * PM2.5: {pollutants_data.get('PM2.5', 0):.1f} µg/m³
  * PM10: {pollutants_data.get('PM10', 0):.1f} µg/m³
  * NO2: {pollutants_data.get('NO2', 0):.1f} ppb
  * SO2: {pollutants_data.get('SO2', 0):.1f} ppb
  * CO: {pollutants_data.get('CO', 0):.2f} ppm

Berikan rekomendasi untuk MASYARAKAT UMUM dengan format:

1. **RINGKASAN STATUS**
   - Penjelasan singkat kondisi udara saat ini
   - Perbandingan dengan knowledge base yang relevan

2. **KELOMPOK BERISIKO**
   - Identifikasi siapa saja yang berisiko (anak-anak, lansia, penderita asma, dll)
   - Tingkat risiko untuk setiap kelompok

3. **REKOMENDASI AKTIVITAS**
   - Aktivitas yang aman dilakukan
   - Aktivitas yang harus dihindari
   - Durasi maksimal aktivitas outdoor (jika ada)

4. **TINDAKAN PENCEGAHAN**
   - Penggunaan masker (jenis yang tepat)
   - Air purifier indoor
   - Ventilasi ruangan
   - Konsumsi vitamin/makanan yang membantu

5. **PERBANDINGAN GLOBAL**
   - Berdasarkan knowledge base, bagaimana kondisi ini dibandingkan dengan negara/kota lain
   - Insight dari data historis

6. **PREDIKSI & TREN**
   - Kapan kondisi mungkin membaik
   - Faktor yang mempengaruhi

Gunakan data dari knowledge base untuk membuat rekomendasi lebih akurat dan spesifik.
Berikan dalam Bahasa Indonesia yang mudah dipahami.
"""
    else:  # industry
        prompt = f"""
Anda adalah konsultan lingkungan industri yang ahli dalam pengendalian emisi.

{context}

DATA EMISI SAAT INI:
- PM2.5: {pollutants_data.get('PM2.5', 0):.1f} µg/m³
- PM10: {pollutants_data.get('PM10', 0):.1f} µg/m³
- NO2: {pollutants_data.get('NO2', 0):.1f} ppb
- SO2: {pollutants_data.get('SO2', 0):.1f} ppb
- CO: {pollutants_data.get('CO', 0):.2f} ppm
- AQI Terukur: {aqi} ({category})

Berikan rekomendasi untuk INDUSTRI dengan format:

1. **ANALISIS EMISI**
   - Evaluasi level emisi dibandingkan dengan standar
   - Polutan yang melebihi ambang batas
   - Perbandingan dengan data industri sejenis dari knowledge base

2. **COMPLIANCE STATUS**
   - Status kepatuhan terhadap regulasi
   - Baku mutu yang berlaku (PP 22/2021, PermenLH)
   - Risiko sanksi/denda

3. **TEKNOLOGI PENGENDALIAN**
   Untuk setiap polutan yang tinggi, rekomendasikan:
   - Teknologi yang sesuai (ESP, Bag Filter, SCR, FGD, dll)
   - Efisiensi removal yang bisa dicapai
   - Estimasi biaya investasi
   - Timeline implementasi

4. **QUICK WINS (0-3 Bulan)**
   - Tindakan cepat tanpa investasi besar
   - Process optimization
   - Housekeeping improvements

5. **MEDIUM-TERM (3-12 Bulan)**
   - Upgrade peralatan existing
   - Training operator
   - Sistem monitoring

6. **LONG-TERM (12+ Bulan)**
   - Investasi teknologi baru
   - Transformasi proses
   - Renewable energy

7. **ENVIRONMENTAL MANAGEMENT**
   - Sistem monitoring berkelanjutan
   - Reporting requirements
   - Sertifikasi lingkungan (ISO 14001, PROPER)

8. **COST-BENEFIT ANALYSIS**
   - Estimasi biaya implementasi
   - Penghematan dari efisiensi
   - ROI timeline
   - Insentif/subsidi yang tersedia

Gunakan data dari knowledge base untuk memberikan benchmark dan best practices.
Berikan dalam Bahasa Indonesia yang profesional.
"""
    
    # 5. Generate dengan Gemini
    try:
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content(prompt)
        return response.text, relevant_knowledge
    except Exception as e:
        return f"Error generating recommendation: {str(e)}", []

# ===========================
# MAIN APP
# ===========================

def main():
    st.markdown('<div class="main-header">🌍 Smart AQI RAG System</div>', unsafe_allow_html=True)
    st.markdown("### Sistem Rekomendasi Kualitas Udara")
    
    # Load datasets dan build knowledge base
    with st.spinner("🔄 Loading datasets dan membangun knowledge base..."):
        df_global, df_pollution = load_datasets()
        
        if df_global is not None and df_pollution is not None:
            knowledge_base = create_knowledge_base(df_global, df_pollution)
            vectorizer, doc_vectors, kb = create_rag_retriever(knowledge_base)
            
            st.success(f"✅ Knowledge base berhasil dimuat: {len(knowledge_base)} knowledge pieces")
            
            # Info tentang RAG
            with st.expander("ℹ️ Tentang RAG System"):
                st.markdown("""
                <div class="rag-info">
                <h4>🧠 Retrieval-Augmented Generation (RAG)</h4>
                <p>Sistem ini menggunakan RAG untuk memberikan rekomendasi yang lebih akurat dengan:</p>
                <ul>
                    <li>📊 <b>Knowledge Base</b> dari 2 dataset CSV (21,966 data global + 400 data pollution)</li>
                    <li>🔍 <b>TF-IDF Vectorization</b> untuk similarity search</li>
                    <li>🎯 <b>Top-K Retrieval</b> mengambil 8 knowledge paling relevan</li>
                    <li>🤖 <b>Gemini AI</b> menggunakan retrieved knowledge untuk generate rekomendasi</li>
                </ul>
                <p><b>Knowledge Types:</b></p>
                <ul>
                    <li>Global AQI statistics per negara</li>
                    <li>Pollution profiles per kategori kualitas udara</li>
                    <li>Pollutant correlation patterns</li>
                    <li>Expert guidelines untuk public & industrial users</li>
                    <li>Health impact thresholds</li>
                    <li>Industrial control technologies</li>
                </ul>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.error("❌ Gagal memuat dataset!")
            return
    
    # Sidebar
    st.sidebar.header("⚙️ Konfigurasi")
    
    user_type = st.sidebar.radio(
        "Pilih Perspektif:",
        ["public", "industry"],
        format_func=lambda x: "👥 Masyarakat Umum" if x == "public" else "🏭 Industri"
    )
    
    st.sidebar.markdown("---")
    
    # Input data polutan
    st.sidebar.subheader("📊 Input Data Polutan")
    
    pm25 = st.sidebar.number_input("PM2.5 (µg/m³)", min_value=0.0, max_value=500.0, value=35.0, step=1.0)
    pm10 = st.sidebar.number_input("PM10 (µg/m³)", min_value=0.0, max_value=600.0, value=50.0, step=1.0)
    no2 = st.sidebar.number_input("NO₂ (ppb)", min_value=0.0, max_value=2000.0, value=30.0, step=1.0)
    so2 = st.sidebar.number_input("SO₂ (ppb)", min_value=0.0, max_value=1000.0, value=20.0, step=1.0)
    co = st.sidebar.number_input("CO (ppm)", min_value=0.0, max_value=50.0, value=1.5, step=0.1)
    
    # Hitung AQI
    aqi = calculate_aqi_from_pollutants(pm25, pm10, no2, so2, co)
    category, css_class = get_aqi_category(aqi)
    
    # Main content
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("📈 AQI Visualization")
        fig_gauge = create_aqi_gauge(aqi)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # AQI Card
        st.markdown(f"""
        <div class="aqi-card {css_class}">
            <h2 style="margin:0;">AQI: {aqi}</h2>
            <h3 style="margin:0.5rem 0 0 0;">{category}</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.subheader("🧪 Pollutant Levels")
        
        pollutants_df = pd.DataFrame({
            'Polutan': ['PM2.5', 'PM10', 'NO₂', 'SO₂', 'CO'],
            'Nilai': [pm25, pm10, no2, so2, co],
            'Unit': ['µg/m³', 'µg/m³', 'ppb', 'ppb', 'ppm']
        })
        
        st.dataframe(pollutants_df, use_container_width=True, hide_index=True)
        
        # Bar chart
        fig_bar = px.bar(
            pollutants_df,
            x='Polutan',
            y='Nilai',
            color='Polutan',
            title='Konsentrasi Polutan'
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    
    # Generate rekomendasi
    st.markdown("---")
    st.subheader("🤖 Rekomendasi")

    if st.button("🔮 Generate Rekomendasi", type="primary", use_container_width=True):
        with st.spinner("🔍 Retrieving knowledge dan generating rekomendasi..."):
            pollutants_data = {
                'PM2.5': pm25,
                'PM10': pm10,
                'NO2': no2,
                'SO2': so2,
                'CO': co
            }
            
            recommendation, retrieved_kb = get_rag_enhanced_recommendation(
                aqi, category, pollutants_data, user_type,
                vectorizer, doc_vectors, knowledge_base
            )
            
            # Tampilkan retrieved knowledge
            with st.expander("📚 Retrieved Knowledge (yang digunakan untuk rekomendasi)"):
                for i, kb in enumerate(retrieved_kb, 1):
                    st.markdown(f"""
                    **{i}. [{kb['type']}]** (Relevance: {kb['similarity_score']:.3f})
                    
                    {kb['content']}
                    
                    ---
                    """)
            
            # Tampilkan rekomendasi
            st.markdown("### 💡 Rekomendasi")
            st.markdown(recommendation)
            
            # Download button
            st.download_button(
                label="📥 Download Rekomendasi",
                data=recommendation,
                file_name=f"rekomendasi_rag_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                mime="text/plain"
            )
    
    # Dataset preview
    st.markdown("---")
    st.subheader("📊 Dataset Preview")
    
    tab1, tab2 = st.tabs(["Global AQI Data", "Pollution Dataset"])
    
    with tab1:
        st.dataframe(df_global.head(100), use_container_width=True)
        st.caption(f"Total: {len(df_global)} records")
    
    with tab2:
        st.dataframe(df_pollution.head(100), use_container_width=True)
        st.caption(f"Total: {len(df_pollution)} records")

if __name__ == "__main__":
    main()
