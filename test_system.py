# Test Script untuk Smart AQI System
# Gunakan file ini untuk testing fungsi-fungsi utama

import sys
import json
from datetime import datetime

def test_aqi_category():
    """Test fungsi kategorisasi AQI"""
    print("\n=== Testing AQI Category Function ===")
    
    test_cases = [
        (25, "Good"),
        (75, "Moderate"),
        (125, "Unhealthy for Sensitive Groups"),
        (175, "Unhealthy"),
        (250, "Very Unhealthy"),
        (350, "Hazardous")
    ]
    
    # Import fungsi dari main.py
    try:
        from main import get_aqi_category
        
        all_passed = True
        for aqi, expected_category in test_cases:
            result = get_aqi_category(aqi)
            actual_category = result['category']
            status = "✅ PASS" if expected_category in actual_category else "❌ FAIL"
            print(f"AQI {aqi}: {actual_category} {status}")
            if expected_category not in actual_category:
                all_passed = False
        
        if all_passed:
            print("\n🎉 All AQI category tests passed!")
        else:
            print("\n⚠️ Some tests failed!")
            
    except ImportError as e:
        print(f"❌ Error importing main.py: {e}")
        print("Make sure main.py exists in the same directory")

def test_data_validation():
    """Test validasi data IoT"""
    print("\n=== Testing Data Validation ===")
    
    try:
        from iot_integration import validate_aqi_data
        
        # Test valid data
        valid_data = {
            'aqi': 85,
            'pm25': 25.5,
            'pm10': 45.2,
            'temperature': 28.5,
            'humidity': 75
        }
        
        is_valid, message = validate_aqi_data(valid_data)
        print(f"Valid data test: {'✅ PASS' if is_valid else '❌ FAIL'} - {message}")
        
        # Test invalid data (missing aqi)
        invalid_data = {
            'pm25': 25.5,
            'temperature': 28.5
        }
        
        is_valid, message = validate_aqi_data(invalid_data)
        print(f"Invalid data test: {'✅ PASS' if not is_valid else '❌ FAIL'} - {message}")
        
        # Test out of range AQI
        out_of_range = {
            'aqi': 600  # Invalid: should be 0-500
        }
        
        is_valid, message = validate_aqi_data(out_of_range)
        print(f"Out of range test: {'✅ PASS' if not is_valid else '❌ FAIL'} - {message}")
        
        print("\n🎉 Data validation tests completed!")
        
    except ImportError as e:
        print(f"❌ Error importing iot_integration.py: {e}")

def generate_sample_iot_data():
    """Generate sample IoT data untuk testing"""
    print("\n=== Generating Sample IoT Data ===")
    
    try:
        from iot_integration import get_sample_iot_data
        
        sample = get_sample_iot_data()
        print(json.dumps(sample, indent=2))
        
        # Save to file
        with open('sample_iot_data.json', 'w') as f:
            json.dump(sample, f, indent=2)
        
        print("\n✅ Sample data saved to: sample_iot_data.json")
        
    except ImportError as e:
        print(f"❌ Error: {e}")

def test_streamlit_imports():
    """Test apakah semua library yang dibutuhkan terinstall"""
    print("\n=== Testing Required Libraries ===")
    
    libraries = {
        'streamlit': 'streamlit',
        'google.generativeai': 'google-generativeai',
        'pandas': 'pandas',
        'plotly': 'plotly'
    }
    
    all_installed = True
    
    for lib_import, lib_name in libraries.items():
        try:
            __import__(lib_import)
            print(f"✅ {lib_name}: Installed")
        except ImportError:
            print(f"❌ {lib_name}: NOT installed - Run: pip install {lib_name}")
            all_installed = False
    
    if all_installed:
        print("\n🎉 All required libraries are installed!")
    else:
        print("\n⚠️ Some libraries are missing. Please install them.")

def test_api_key_config():
    """Test apakah API key sudah dikonfigurasi"""
    print("\n=== Testing API Key Configuration ===")
    
    try:
        import streamlit as st
        import toml
        
        # Try to read secrets file
        try:
            with open('.streamlit/secrets.toml', 'r') as f:
                secrets = toml.load(f)
                
            api_key = secrets.get('GEMINI_API_KEY', '')
            
            if api_key == '' or api_key == 'YOUR_GEMINI_API_KEY_HERE':
                print("⚠️ API Key belum dikonfigurasi")
                print("Silakan setup API key di .streamlit/secrets.toml")
                print("Panduan: https://makersuite.google.com/app/apikey")
            else:
                print(f"✅ API Key configured (length: {len(api_key)} chars)")
                
        except FileNotFoundError:
            print("⚠️ File secrets.toml tidak ditemukan")
            print("Pastikan file .streamlit/secrets.toml ada")
            
    except ImportError:
        print("⚠️ TOML library not found. Install: pip install toml")

def simulate_iot_reading():
    """Simulasi pembacaan data dari IoT sensor"""
    print("\n=== Simulating IoT Sensor Reading ===")
    
    import random
    
    # Simulate realistic AQI values with some randomness
    aqi = random.randint(30, 200)
    
    # PM2.5 based on AQI
    if aqi <= 50:
        pm25 = random.uniform(0, 12)
    elif aqi <= 100:
        pm25 = random.uniform(12.1, 35.4)
    elif aqi <= 150:
        pm25 = random.uniform(35.5, 55.4)
    else:
        pm25 = random.uniform(55.5, 150.4)
    
    pm10 = pm25 * random.uniform(1.5, 2.0)
    
    sensor_data = {
        'timestamp': datetime.now().isoformat(),
        'device_id': 'TEST-SENSOR-001',
        'location': 'Jakarta Testing Lab',
        'measurements': {
            'aqi': aqi,
            'pm25': round(pm25, 2),
            'pm10': round(pm10, 2),
            'temperature': round(random.uniform(25, 32), 1),
            'humidity': round(random.uniform(60, 85), 1)
        }
    }
    
    print(json.dumps(sensor_data, indent=2))
    
    try:
        from main import get_aqi_category
        category = get_aqi_category(aqi)
        print(f"\n📊 Category: {category['icon']} {category['category']}")
        print(f"💡 Recommendation: {category['health_implication']}")
    except:
        pass
    
    return sensor_data

def run_all_tests():
    """Jalankan semua tests"""
    print("=" * 60)
    print("SMART AQI SYSTEM - AUTOMATED TESTING")
    print("=" * 60)
    
    test_streamlit_imports()
    test_api_key_config()
    test_aqi_category()
    test_data_validation()
    generate_sample_iot_data()
    simulate_iot_reading()
    
    print("\n" + "=" * 60)
    print("TESTING COMPLETED!")
    print("=" * 60)
    
    print("\n📝 Next Steps:")
    print("1. Jika ada library yang missing, install dengan: pip install -r requirements.txt")
    print("2. Jika API key belum setup, configure di .streamlit/secrets.toml")
    print("3. Jalankan aplikasi dengan: streamlit run main.py")
    print("\n✨ Happy testing! ✨")

def interactive_menu():
    """Menu interaktif untuk testing"""
    while True:
        print("\n" + "=" * 60)
        print("SMART AQI SYSTEM - TEST MENU")
        print("=" * 60)
        print("1. Test semua fungsi")
        print("2. Test AQI category")
        print("3. Test data validation")
        print("4. Generate sample IoT data")
        print("5. Simulate IoT sensor reading")
        print("6. Test library installations")
        print("7. Test API key config")
        print("0. Exit")
        print("=" * 60)
        
        choice = input("\nPilih menu (0-7): ").strip()
        
        if choice == '1':
            run_all_tests()
        elif choice == '2':
            test_aqi_category()
        elif choice == '3':
            test_data_validation()
        elif choice == '4':
            generate_sample_iot_data()
        elif choice == '5':
            simulate_iot_reading()
        elif choice == '6':
            test_streamlit_imports()
        elif choice == '7':
            test_api_key_config()
        elif choice == '0':
            print("\n👋 Goodbye! Thanks for testing Smart AQI System!")
            break
        else:
            print("❌ Invalid choice! Please select 0-7")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    print("""
    ╔═══════════════════════════════════════════════════════╗
    ║     SMART AQI SYSTEM - TEST & VALIDATION TOOL         ║
    ║              Testing Suite v1.0                       ║
    ╚═══════════════════════════════════════════════════════╝
    """)
    
    if len(sys.argv) > 1 and sys.argv[1] == '--auto':
        # Run all tests automatically
        run_all_tests()
    else:
        # Interactive menu
        interactive_menu()
