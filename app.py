from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from flask_cors import CORS

app = Flask(__name__)

# Enable CORS for cross-origin requests
CORS(app)

# MySQL configurations (Update with your XAMPP MySQL credentials)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'  # Default user in XAMPP
app.config['MYSQL_PASSWORD'] = ''  # Default password in XAMPP (leave empty)
app.config['MYSQL_DB'] = 'test'

mysql = MySQL(app)

# Test DB connection route
@app.route('/test-db')
def test_db():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT DATABASE()")
        db_name = cur.fetchone()
        return jsonify({'connected_to': db_name[0]})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Get All Students
@app.route('/students', methods=['GET'])
def get_students():
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students")
        rows = cur.fetchall()
        cur.close()

        students = [{'id': row[0], 'name': row[1], 'age': row[2], 'course': row[3]} for row in rows]
        return jsonify(students)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Add New Student
@app.route('/students', methods=['POST'])
def add_student():
    try:
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        course = data.get('course')

        if not name or not age or not course:
            return jsonify({'error': 'Invalid data'}), 400

        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO students (name, age, course) VALUES (%s, %s, %s)", (name, age, course))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Student added successfully'}), 201
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Get Specific Student by ID
@app.route('/students/<int:id>', methods=['GET'])
def get_student(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id = %s", (id,))
        row = cur.fetchone()
        cur.close()

        if not row:
            return jsonify({'error': 'Student not found'}), 404

        student = {'id': row[0], 'name': row[1], 'age': row[2], 'course': row[3]}
        return jsonify(student)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Update Student by ID
@app.route('/students/<int:id>', methods=['PUT'])
def update_student(id):
    try:
        data = request.get_json()
        name = data.get('name')
        age = data.get('age')
        course = data.get('course')

        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id = %s", (id,))
        row = cur.fetchone()

        if not row:
            cur.close()
            return jsonify({'error': 'Student not found'}), 404

        cur.execute("""
            UPDATE students 
            SET name = %s, age = %s, course = %s 
            WHERE id = %s
        """, (name or row[1], age or row[2], course or row[3], id))
        mysql.connection.commit()
        cur.close()

        return jsonify({'message': 'Student updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Endpoint: Delete Student by ID
@app.route('/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    try:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM students WHERE id = %s", (id,))
        row = cur.fetchone()

        if not row:
            cur.close()
            return jsonify({'error': 'Student not found'}), 404

        cur.execute("DELETE FROM students WHERE id = %s", (id,))
        mysql.connection.commit()
        cur.close()
        return jsonify({'message': 'Student deleted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Run the app
if __name__ == '__main__':
    app.run(debug=True)
