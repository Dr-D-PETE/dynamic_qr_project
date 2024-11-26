from flask import Flask, request, render_template, jsonify, send_file
import sqlite3
import qrcode
import io
import os

app = Flask(__name__)

# Initialize the database
def init_db():
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            email TEXT,
            website TEXT,
            company TEXT,
            title TEXT,
            address TEXT
        )
    """)
    conn.commit()
    conn.close()

# Route to display user data dynamically
@app.route("/profile")
def profile():
    user_id = request.args.get("id")  # Get the user ID from the URL query string
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if user:
        # Render the user's information as an HTML page
        return render_template("profile.html", user=user)
    else:
        return "User not found", 404

# Route to add or update user data
@app.route("/update_user", methods=["POST"])
def update_user():
    data = request.json  # Accept data as JSON
    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()

    if "id" in data:  # Update an existing user
        cursor.execute("""
            UPDATE users SET name = ?, phone = ?, email = ?, website = ?, company = ?, title = ?, address = ?
            WHERE id = ?
        """, (data["name"], data["phone"], data["email"], data["website"], data["company"], data["title"], data["address"], data["id"]))
    else:  # Add a new user
        cursor.execute("""
            INSERT INTO users (name, phone, email, website, company, title, address)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (data["name"], data["phone"], data["email"], data["website"], data["company"], data["title"], data["address"]))

    conn.commit()
    conn.close()
    return jsonify({"message": "User data saved successfully"})

# Route to generate a QR code for the user's profile
@app.route("/generate_qr", methods=["GET"])
def generate_qr():
    user_id = request.args.get("id")  # Get the user ID from query parameters
    if not user_id:
        return "User ID is required", 400

    conn = sqlite3.connect("database.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return "User not found", 404

    # Generate the QR code with the profile link
    profile_url = f"http://127.0.0.1:5000/profile?id={user_id}"
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(profile_url)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save the QR code image to a BytesIO object
    img_io = io.BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return send_file(img_io, mimetype="image/png")

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))  # Use the PORT environment variable provided by Render
    app.run(host="0.0.0.0", port=port, debug=True)  # Bind to 0.0.0.0 and the correct port
