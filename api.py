from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/hello', methods=['GET'])
def hello():
    return jsonify({"message": "Hello World! Welcome to the API."}), 200

@app.route('/add', methods=['POST'])
def add():
    data = request.get_json()
    if not data or 'a' not in data or 'b' not in data:
        return jsonify({"error": "Missing 'a' or 'b' in request body"}), 400
    
    try:
        a = float(data['a'])
        b = float(data['b'])
        result = a + b
        return jsonify({"result": result}), 200
    except ValueError:
        return jsonify({"error": "Inputs must be numbers"}), 400

if __name__ == '__main__':
    # Running on port 5000 by default
    print("Starting Flask API on http://127.0.0.1:5000/")
    app.run(debug=True, port=5000)