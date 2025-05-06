from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

# MySQL configuration
app.config['MYSQL_HOST'] = os.getenv('MYSQL_HOST', 'localhost')
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER', 'root')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD', 'password')
app.config['MYSQL_DB'] = os.getenv('MYSQL_DB', 'plant_database')

mysql = MySQL(app)

@app.route('/api/plants/<int:plant_id>/attracts', methods=['GET'])
def get_plant_attracts(plant_id):
    try:
        # Query the attracts table for this plant
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT birds, butterflies, bees, hummingbirds, other_animals
            FROM attracts
            WHERE plant_id = %s
        """, (plant_id,))
        attracts_data = cursor.fetchone()
        cursor.close()

        if attracts_data:
            # Convert other_animals from string to list if it's stored as comma-separated values
            if attracts_data['other_animals']:
                attracts_data['other_animals'] = [animal.strip() for animal in attracts_data['other_animals'].split(',')]
            else:
                attracts_data['other_animals'] = []
            
            return jsonify(attracts_data)
        return jsonify({'error': 'No attracts data found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/plants/<int:plant_id>/sunlight', methods=['GET'])
def get_plant_sunlight(plant_id):
    try:
        # Query the sunlight table for this plant
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""
            SELECT full_sun, partial_shade, full_shade, notes
            FROM sunlight
            WHERE plant_id = %s
        """, (plant_id,))
        sunlight_data = cursor.fetchone()
        cursor.close()

        if sunlight_data:
            return jsonify(sunlight_data)
        return jsonify({'error': 'No sunlight data found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    app.run(host='0.0.0.0', port=port) 