import streamlit as st 
import paho.mqtt.client as mqtt
import json
import time

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Lector de Sensor MQTT",
    page_icon="📡",
    layout="centered"
)

# --- ESTILOS PERSONALIZADOS ---
page_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap');

    html, body, [class*="st-"], [data-testid="stAppViewContainer"] * {
        font-family: 'Poppins', sans-serif !important;
    }

    [data-testid="stAppViewContainer"] {
        background: linear-gradient(135deg, #e6f0ff, #f5f9ff, #eaf9f5);
        color: #333;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #d7e3ff, #f0f5ff);
        color: #333;
    }

    /* Título principal con sombra y degradado cálido */
    h1, .stMarkdown h1 {
        text-align: center;
        font-weight: 700 !important;
        background: linear-gradient(90deg, #ff6ec7, #9b5de5, #4361ee);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.4em !important;
        padding: 0.3em 0;
        display: block;
        text-shadow: 2px 2px 10px rgba(100, 100, 255, 0.2);
    }

    h2, h3, h4 {
        color: #0077b6 !important;
        font-weight: 600 !important;
    }

    .stButton > button {
        background: linear-gradient(90deg, #0096c7, #48cae4);
        color: white !important;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #48cae4, #0096c7);
        transform: scale(1.03);
    }

    .stMetric {
        background-color: #f0f8ff !important;
        border-radius: 10px;
        padding: 8px !important;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
    }

    .stExpander {
        border-radius: 10px !important;
        background-color: #f8fbff !important;
    }

    .stSuccess {
        background-color: #d9f8e4 !important;
    }
</style>
"""
st.markdown(page_style, unsafe_allow_html=True)

# --- VARIABLES DE ESTADO ---
if 'sensor_data' not in st.session_state:
    st.session_state.sensor_data = None

# --- FUNCIÓN MQTT ---
def get_mqtt_message(broker, port, topic, client_id):
    message_received = {"received": False, "payload": None}
    
    def on_message(client, userdata, message):
        try:
            payload = json.loads(message.payload.decode())
            message_received["payload"] = payload
            message_received["received"] = True
        except:
            message_received["payload"] = message.payload.decode()
            message_received["received"] = True
    
    try:
        client = mqtt.Client(client_id=client_id)
        client.on_message = on_message
        client.connect(broker, port, 60)
        client.subscribe(topic)
        client.loop_start()
        
        timeout = time.time() + 5
        while not message_received["received"] and time.time() < timeout:
            time.sleep(0.1)
        
        client.loop_stop()
        client.disconnect()
        
        return message_received["payload"]
    
    except Exception as e:
        return {"error": str(e)}

# --- SIDEBAR ---
with st.sidebar:
    st.subheader('⚙️ Configuración de Conexión')
    broker = st.text_input('Broker MQTT', value='broker.mqttdashboard.com')
    port = st.number_input('Puerto', value=1883, min_value=1, max_value=65535)
    topic = st.text_input('Tópico', value='sensor_st')
    client_id = st.text_input('ID del Cliente', value='streamlit_client')

# --- TÍTULO ---
st.markdown("<h1>📡 Lector de Sensor MQTT</h1>", unsafe_allow_html=True)

# --- INFORMACIÓN ---
with st.expander('ℹ️ Información', expanded=False):
    st.markdown("""
    ### Cómo usar esta aplicación:
    1. **Broker MQTT**: Ingresa la dirección del servidor MQTT en el sidebar  
    2. **Puerto**: Generalmente es 1883  
    3. **Tópico**: Canal al que deseas suscribirte  
    4. **ID del Cliente**: Identificador único  
    5. Haz clic en **Obtener Datos** para recibir el mensaje más reciente  

    **Brokers públicos recomendados:**  
    - broker.mqttdashboard.com  
    - test.mosquitto.org  
    - broker.hivemq.com  
    """)

st.divider()

# --- BOTÓN ---
if st.button('🔄 Obtener Datos del Sensor', use_container_width=True):
    with st.spinner('Conectando al broker y esperando datos...'):
        sensor_data = get_mqtt_message(broker, int(port), topic, client_id)
        st.session_state.sensor_data = sensor_data

# --- RESULTADOS ---
if st.session_state.sensor_data:
    st.divider()
    st.subheader('📊 Datos Recibidos')
    
    data = st.session_state.sensor_data
    
    if isinstance(data, dict) and 'error' in data:
        st.error(f"❌ Error de conexión: {data['error']}")
    else:
        st.success('✅ Datos recibidos correctamente')
        
        if isinstance(data, dict):
            cols = st.columns(len(data))
            for i, (key, value) in enumerate(data.items()):
                with cols[i]:
                    st.metric(label=key, value=value)
            
            with st.expander('Ver JSON completo'):
                st.json(data)
        else:
            st.code(data)
