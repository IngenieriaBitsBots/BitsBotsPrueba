from flask import Flask, jsonify, request
import time

app = Flask(__name__)

@app.route('/api/test', methods=['GET'])
def test_service():
    """Servicio de prueba que responde con un mensaje de estado."""
    try:
        return jsonify({
            "status": "success",
            "message": "El servicio está funcionando correctamente.",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error en el servicio de prueba: {str(e)}"
        }), 500


@app.route('/api/echo', methods=['POST'])
def echo_service():
    """Servicio que recibe datos JSON y los devuelve (eco)."""
    try:
        data = request.get_json()
        return jsonify({
            "status": "success",
            "received_data": data
        }), 200
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"Error al procesar los datos: {str(e)}"
        }), 400

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
