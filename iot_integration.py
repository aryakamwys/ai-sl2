# Contoh Integrasi IoT dengan berbagai protokol

"""
File ini berisi contoh-contoh integrasi sistem AQI dengan perangkat IoT
menggunakan berbagai protokol komunikasi yang umum digunakan.
"""

import json
import time
from datetime import datetime

# ========== MQTT INTEGRATION ==========
"""
MQTT adalah protokol messaging yang ringan dan ideal untuk IoT.
Install: pip install paho-mqtt
"""

def mqtt_integration_example():
    import paho.mqtt.client as mqtt
    
    # Callback ketika koneksi berhasil
    def on_connect(client, userdata, flags, rc):
        print(f"Connected to MQTT broker with result code {rc}")
        # Subscribe ke topik sensor AQI
        client.subscribe("sensor/aqi/#")
    
    # Callback ketika menerima pesan
    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode())
            print(f"Received AQI data: {data}")
            
            # Data yang diharapkan:
            # {
            #     "aqi": 85,
            #     "pm25": 25.5,
            #     "pm10": 45.2,
            #     "temperature": 28.5,
            #     "humidity": 75,
            #     "location": "Jakarta",
            #     "timestamp": "2025-11-04T10:30:00Z"
            # }
            
            return data
        except Exception as e:
            print(f"Error parsing MQTT message: {e}")
    
    # Setup MQTT client
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    # Connect ke broker
    broker_address = "broker.hivemq.com"  # Atau broker Anda sendiri
    broker_port = 1883
    
    try:
        client.connect(broker_address, broker_port, 60)
        client.loop_forever()
    except Exception as e:
        print(f"MQTT connection error: {e}")


# ========== HTTP REST API INTEGRATION ==========
"""
REST API adalah metode paling umum untuk integrasi web-based IoT.
Install: pip install requests
"""

def rest_api_integration_example():
    import requests
    
    # Fetch data dari IoT device via REST API
    def fetch_aqi_data(device_id, api_key):
        """
        Mengambil data AQI dari REST API endpoint
        
        Args:
            device_id: ID perangkat IoT
            api_key: API key untuk autentikasi
        
        Returns:
            dict: Data AQI
        """
        url = f"https://api.iot-platform.com/devices/{device_id}/aqi"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error fetching data: {e}")
            return None
    
    # Contoh penggunaan
    device_id = "AQI-SENSOR-001"
    api_key = "your_api_key_here"
    
    while True:
        data = fetch_aqi_data(device_id, api_key)
        if data:
            print(f"AQI: {data.get('aqi')}, PM2.5: {data.get('pm25')}")
        time.sleep(60)  # Update setiap 1 menit


# ========== WebSocket INTEGRATION ==========
"""
WebSocket untuk real-time bidirectional communication.
Install: pip install websocket-client
"""

def websocket_integration_example():
    import websocket
    
    def on_message(ws, message):
        try:
            data = json.loads(message)
            print(f"WebSocket data received: {data}")
            # Process data here
        except Exception as e:
            print(f"Error: {e}")
    
    def on_error(ws, error):
        print(f"WebSocket error: {error}")
    
    def on_close(ws, close_status_code, close_msg):
        print("WebSocket connection closed")
    
    def on_open(ws):
        print("WebSocket connection opened")
        # Subscribe to AQI updates
        ws.send(json.dumps({
            "action": "subscribe",
            "topic": "aqi_updates"
        }))
    
    # WebSocket URL
    ws_url = "wss://iot-platform.com/ws/aqi"
    
    ws = websocket.WebSocketApp(
        ws_url,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    
    ws.run_forever()


# ========== SERIAL PORT INTEGRATION (Arduino/ESP32) ==========
"""
Untuk sensor yang terhubung langsung via USB/Serial.
Install: pip install pyserial
"""

def serial_integration_example():
    import serial
    
    def read_aqi_from_serial(port='COM3', baudrate=9600):
        """
        Membaca data AQI dari serial port (Arduino/ESP32)
        
        Args:
            port: Serial port (COM3 untuk Windows, /dev/ttyUSB0 untuk Linux)
            baudrate: Kecepatan komunikasi
        """
        try:
            ser = serial.Serial(port, baudrate, timeout=1)
            print(f"Connected to {port}")
            
            while True:
                if ser.in_waiting > 0:
                    line = ser.readline().decode('utf-8').strip()
                    try:
                        # Asumsikan Arduino mengirim JSON
                        data = json.loads(line)
                        print(f"AQI: {data.get('aqi')}")
                        return data
                    except json.JSONDecodeError:
                        # Jika format bukan JSON, parse manual
                        # Contoh format: "AQI:85,PM25:25.5,PM10:45.2"
                        if line.startswith("AQI:"):
                            parts = line.split(',')
                            data = {}
                            for part in parts:
                                key, value = part.split(':')
                                data[key.lower()] = float(value)
                            print(f"Parsed data: {data}")
                            return data
                
                time.sleep(0.1)
        
        except serial.SerialException as e:
            print(f"Serial port error: {e}")
        finally:
            if 'ser' in locals() and ser.is_open:
                ser.close()


# ========== MODBUS TCP INTEGRATION ==========
"""
Modbus TCP untuk industrial sensors.
Install: pip install pymodbus
"""

def modbus_integration_example():
    from pymodbus.client import ModbusTcpClient
    
    def read_aqi_from_modbus(host='192.168.1.100', port=502):
        """
        Membaca data AQI dari sensor Modbus TCP
        
        Args:
            host: IP address sensor
            port: Modbus port (default 502)
        """
        client = ModbusTcpClient(host, port=port)
        
        try:
            if client.connect():
                print(f"Connected to Modbus device at {host}")
                
                # Baca holding registers
                # Asumsikan:
                # Register 0: AQI value
                # Register 1: PM2.5
                # Register 2: PM10
                result = client.read_holding_registers(address=0, count=3, slave=1)
                
                if not result.isError():
                    aqi = result.registers[0]
                    pm25 = result.registers[1] / 10.0  # Jika nilai dikali 10
                    pm10 = result.registers[2] / 10.0
                    
                    data = {
                        'aqi': aqi,
                        'pm25': pm25,
                        'pm10': pm10,
                        'timestamp': datetime.now().isoformat()
                    }
                    
                    print(f"Modbus data: {data}")
                    return data
                else:
                    print(f"Modbus error: {result}")
            else:
                print("Failed to connect to Modbus device")
        
        finally:
            client.close()


# ========== INTEGRATION DENGAN STREAMLIT ==========
"""
Cara mengintegrasikan IoT data dengan aplikasi Streamlit
"""

def streamlit_iot_integration():
    """
    Contoh integrasi IoT dengan Streamlit app
    Tambahkan code ini ke main.py
    """
    
    code_example = '''
import streamlit as st
import requests
import time

# Di dalam main():

# Method 1: Polling dengan interval
if 'last_update' not in st.session_state:
    st.session_state.last_update = time.time()

# Update setiap 30 detik
if time.time() - st.session_state.last_update > 30:
    # Fetch data dari IoT
    try:
        response = requests.get("http://your-iot-api/aqi")
        if response.status_code == 200:
            data = response.json()
            st.session_state.aqi_value = data['aqi']
            st.session_state.last_update = time.time()
            st.rerun()
    except Exception as e:
        st.error(f"Error fetching IoT data: {e}")

# Method 2: Manual refresh button
if st.button("🔄 Refresh Data dari IoT"):
    with st.spinner("Mengambil data..."):
        # Fetch logic here
        st.success("Data berhasil diperbarui!")
        st.rerun()

# Method 3: Auto-refresh dengan st.empty()
placeholder = st.empty()
while True:
    with placeholder.container():
        # Fetch dan display data
        data = fetch_iot_data()
        st.metric("AQI", data['aqi'])
    time.sleep(30)
    '''
    
    return code_example


# ========== DATA VALIDATION ==========

def validate_aqi_data(data):
    """
    Validasi data AQI dari IoT sensor
    
    Args:
        data: Dictionary berisi data sensor
    
    Returns:
        tuple: (is_valid, error_message)
    """
    required_fields = ['aqi']
    optional_fields = ['pm25', 'pm10', 'temperature', 'humidity', 'location', 'timestamp']
    
    # Check required fields
    for field in required_fields:
        if field not in data:
            return False, f"Missing required field: {field}"
    
    # Validate AQI range
    aqi = data.get('aqi')
    if not isinstance(aqi, (int, float)):
        return False, "AQI must be a number"
    
    if aqi < 0 or aqi > 500:
        return False, f"AQI value out of range: {aqi}"
    
    # Validate PM2.5 if present
    if 'pm25' in data:
        pm25 = data.get('pm25')
        if not isinstance(pm25, (int, float)):
            return False, "PM2.5 must be a number"
        if pm25 < 0 or pm25 > 500:
            return False, f"PM2.5 value out of range: {pm25}"
    
    # Validate PM10 if present
    if 'pm10' in data:
        pm10 = data.get('pm10')
        if not isinstance(pm10, (int, float)):
            return False, "PM10 must be a number"
        if pm10 < 0 or pm10 > 600:
            return False, f"PM10 value out of range: {pm10}"
    
    return True, "Data valid"


# ========== CONTOH FORMAT DATA ==========

def get_sample_iot_data():
    """
    Contoh format data yang dikirim dari IoT sensor
    """
    return {
        "device_id": "AQI-SENSOR-001",
        "location": {
            "name": "Jakarta Pusat",
            "latitude": -6.2088,
            "longitude": 106.8456
        },
        "timestamp": datetime.now().isoformat(),
        "measurements": {
            "aqi": 85,
            "pm25": 25.5,      # μg/m³
            "pm10": 45.2,      # μg/m³
            "so2": 15.3,       # ppb
            "no2": 25.8,       # ppb
            "co": 0.8,         # ppm
            "o3": 35.2,        # ppb
            "temperature": 28.5,  # °C
            "humidity": 75,    # %
            "pressure": 1013   # hPa
        },
        "sensor_status": {
            "battery": 85,     # %
            "signal_strength": -65,  # dBm
            "calibration_date": "2025-10-01",
            "firmware_version": "2.1.0"
        }
    }


# ========== MAIN DEMO ==========

if __name__ == "__main__":
    print("IoT Integration Examples for Smart AQI System")
    print("=" * 50)
    
    # Tampilkan sample data
    print("\n📊 Sample IoT Data Format:")
    print(json.dumps(get_sample_iot_data(), indent=2))
    
    # Test validation
    print("\n✅ Testing Data Validation:")
    test_data = {"aqi": 85, "pm25": 25.5}
    is_valid, message = validate_aqi_data(test_data)
    print(f"Valid: {is_valid}, Message: {message}")
    
    print("\n💡 Uncomment specific integration examples to test:")
    print("   - MQTT: mqtt_integration_example()")
    print("   - REST API: rest_api_integration_example()")
    print("   - WebSocket: websocket_integration_example()")
    print("   - Serial: serial_integration_example()")
    print("   - Modbus: modbus_integration_example()")
