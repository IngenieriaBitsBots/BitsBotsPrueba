import os
from flask import Flask, request, jsonify
from azure.communication.callautomation import (
    CallAutomationClient,
    SsmlSource
)
from azure.cognitiveservices.speech import SpeechConfig, SpeechSynthesizer, AudioConfig
from azure.identity import DefaultAzureCredential

# Configuración de Azure Communication Services
ACS_CONNECTION_STRING = "endpoint=https://botinfo.unitedstates.communication.azure.com/;accesskey=1guTFl7aIVgWq2tkZM4oSHEpLrL3owX2NHVr87eeefBe0p4TEC0eJQQJ99AKACULyCpETjDrAAAAAZCSEYQW"
CALLBACK_URL = "https://bitsbotsprueba.azurewebsites.net/events"  # Asegúrate de que esté completo

# Configuración de Azure Speech
speech_key = os.getenv("SPEECH_KEY")
region = os.getenv("SPEECH_REGION")

# Crear cliente de CallAutomation
client = CallAutomationClient.from_connection_string(ACS_CONNECTION_STRING)

# Crear cliente de Speech
speech_config = SpeechConfig(subscription=speech_key, region=region)
speech_config.speech_synthesis_voice_name = "es-CO-GonzaloNeural"  # Voz en español
audio_config = AudioConfig(use_default_speaker=True)
synthesizer = SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

app = Flask(__name__)

# 📞 Webhook para recibir llamadas entrantes
@app.route("/incoming-call", methods=["POST"])
def incoming_call():
    data = request.json
    print("📞 Llamada entrante:", data)

    # Extrae el contexto de la llamada
    incoming_call_context = data.get("incomingCallContext")
    
    if incoming_call_context:
        # Contestar la llamada
        call_connection = client.answer_call(
            incoming_call_context=incoming_call_context,
            callback_url=CALLBACK_URL
        )

        call_connection_id = call_connection.call_connection_id
        print(f"✅ Llamada contestada. ID: {call_connection_id}")

        # El mensaje que queremos convertir en voz
        message_text = "¡Hola! Bienvenido a nuestro servicio. ¿En qué podemos ayudarte hoy?"

        # Usamos el Speech API para convertir texto en audio
        result = synthesizer.speak_text_async(message_text).get()

        if result.reason == result.Reason.SynthesizingAudioCompleted:
            print("✅ Audio sintetizado correctamente.")
        else:
            print("❌ Error al sintetizar el audio:", result.error_details)

        # Reproducir el mensaje de bienvenida a través de la llamada
        media_client = client.get_call_connection(call_connection_id).get_call_media()
        
        # Aquí se debe enviar el archivo de audio generado para ser reproducido
        media_client.play_to_caller(SsmlSource(result.audio_data))

        return jsonify({"status": "Llamada contestada y mensaje de bienvenida reproducido."}), 200
    
    return jsonify({"error": "No se encontró incomingCallContext"}), 400

# 📡 Webhook para eventos de la llamada
@app.route("/events", methods=["POST"])
def call_events():
    event_data = request.json
    print("📡 Evento recibido:", event_data)

    # Aquí puedes agregar la lógica de eventos, por ejemplo, para detectar cuándo se termina una llamada
    if 'callEnded' in event_data:
        print("🔚 La llamada ha terminado.")

    return jsonify({"status": "Evento procesado"}), 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 80)))
