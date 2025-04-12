from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
import sqlite3
from io import BytesIO
from xhtml2pdf import pisa

app = Flask(__name__)
app.secret_key = 'your_secret_key_should_be_strong_and_secret'
app.permanent_session_lifetime = 1800  # 30 minutes

def get_db_connection():
    conn = sqlite3.connect('login.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS login (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS donors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL,
            phone TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            donation_date TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS blood_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_name TEXT NOT NULL,
            phone TEXT NOT NULL,
            request_date TEXT NOT NULL,
            blood_group TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            reference_number TEXT NOT NULL
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS handed_over (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            physician_name TEXT NOT NULL,
            handed_date TEXT NOT NULL,
            reference_number TEXT NOT NULL,
            status TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()

@app.route('/', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        return redirect(url_for('dashboard'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if username and password:
            conn = get_db_connection()
            user = conn.execute("SELECT * FROM login WHERE username = ? AND password = ?", 
                                (username, password)).fetchone()
            conn.close()

            if user:
                session.permanent = True
                session['username'] = username
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))
            else:
                error = "Invalid Username or Password"
        else:
            error = "Username and password are required."

    return render_template('login.html', error=error)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=session['username'])

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully!', 'info')
    return redirect(url_for('login'))

@app.route('/donors', methods=['GET', 'POST'])
def donors():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        blood_group = request.form['blood_group']
        donation_date = request.form['donation_date']

        if name and email and phone and blood_group and donation_date:
            conn.execute("""
                INSERT INTO donors (name, email, phone, blood_group, donation_date)
                VALUES (?, ?, ?, ?, ?)
            """, (name, email, phone, blood_group, donation_date))
            conn.commit()
            flash('Donor added successfully!', 'success')
            return redirect(url_for('donors'))

    donors = conn.execute("SELECT * FROM donors").fetchall()
    conn.close()
    
    return render_template('donors.html', donors=donors)

@app.route('/edit_donor/<int:donor_id>', methods=['GET', 'POST'])
def edit_donor(donor_id):
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    donor = conn.execute("SELECT * FROM donors WHERE id = ?", (donor_id,)).fetchone()

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        blood_group = request.form['blood_group']
        donation_date = request.form['donation_date']

        conn.execute("""
            UPDATE donors SET name = ?, email = ?, phone = ?, blood_group = ?, donation_date = ?
            WHERE id = ?
        """, (name, email, phone, blood_group, donation_date, donor_id))
        conn.commit()
        conn.close()
        
        flash('Donor updated successfully!', 'success')
        return redirect(url_for('donors'))

    conn.close()
    return render_template('edit_donor.html', donor=donor)

@app.route('/delete_donor/<int:donor_id>')
def delete_donor(donor_id):
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM donors WHERE id = ?", (donor_id,))
    conn.commit()
    conn.close()
    flash('Donor deleted successfully!', 'info')
    return redirect(url_for('donors'))

@app.route('/blood_requests', methods=['GET', 'POST'])
def blood_requests():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        phone = request.form['phone']
        request_date = request.form['request_date']
        blood_group = request.form['blood_group']
        quantity = request.form['quantity']
        reference_number = request.form['reference_number']

        conn.execute("""
            INSERT INTO blood_requests (patient_name, phone, request_date, blood_group, quantity, reference_number)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (patient_name, phone, request_date, blood_group, quantity, reference_number))
        conn.commit()
        flash('Blood request added successfully!', 'success')
        return redirect(url_for('blood_requests'))

    requests = conn.execute("SELECT * FROM blood_requests").fetchall()
    conn.close()
    
    return render_template('blood_requests.html', requests=requests)

@app.route('/edit_request/<int:request_id>', methods=['GET', 'POST'])
def edit_request(request_id):
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    request_data = conn.execute("SELECT * FROM blood_requests WHERE id = ?", (request_id,)).fetchone()

    if request_data is None:
        flash("Blood request not found!", "danger")
        return redirect(url_for('blood_requests'))

    if request.method == 'POST':
        patient_name = request.form['patient_name']
        phone = request.form['phone']
        request_date = request.form['request_date']
        blood_group = request.form['blood_group']
        quantity = request.form['quantity']
        reference_number = request.form['reference_number']

        conn.execute("""
            UPDATE blood_requests 
            SET patient_name = ?, phone = ?, request_date = ?, blood_group = ?, quantity = ?, reference_number = ? 
            WHERE id = ?
        """, (patient_name, phone, request_date, blood_group, quantity, reference_number, request_id))
        conn.commit()
        conn.close()

        flash('Blood request updated successfully!', 'success')
        return redirect(url_for('blood_requests'))

    conn.close()
    return render_template('edit_request.html', request_data=request_data)

@app.route('/delete_request/<int:request_id>')
def delete_request(request_id):
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    conn.execute("DELETE FROM blood_requests WHERE id = ?", (request_id,))
    conn.commit()
    conn.close()
    
    flash('Blood request deleted successfully!', 'info')
    return redirect(url_for('blood_requests'))

@app.route('/add_handed_over', methods=['POST'])
def add_handed_over():
    physician = request.form['physician_name']
    handed_date = request.form['handed_date']
    reference = request.form['reference_number']
    status = request.form.get('status', 'Pending')

    conn = get_db_connection()
    conn.execute("""
        INSERT INTO handed_over (physician_name, handed_date, reference_number, status)
        VALUES (?, ?, ?, ?)
    """, (physician, handed_date, reference, status))
    conn.commit()
    conn.close()

    flash('Handed Over Record Added!', 'success')
    return redirect(url_for('handed_over'))

@app.route('/add_handed_over', methods=['GET'])
def add_handed_over_redirect():
    return redirect(url_for('handed_over'))

@app.route('/update_status', methods=['POST'])
def update_status():
    record_id = request.form['id']
    new_status = request.form['status']

    conn = get_db_connection()
    conn.execute("UPDATE handed_over SET status = ? WHERE id = ?", (new_status, record_id))
    conn.commit()
    conn.close()

    flash('Status updated!', 'success')
    return redirect(url_for('handed_over'))

@app.route('/handedover')
def handed_over():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    conn = get_db_connection()
    records = conn.execute("""
        SELECT handed_over.*, blood_requests.patient_name
        FROM handed_over
        LEFT JOIN blood_requests ON handed_over.reference_number = blood_requests.reference_number
    """).fetchall()
    conn.close()

    return render_template('handedover.html', handed_overs=records)

@app.route('/delete_handed_over', methods=['POST'])
def delete_handed_over():
    if 'username' not in session:
        flash('Please login first.', 'warning')
        return redirect(url_for('login'))

    record_id = request.form['id']

    conn = get_db_connection()
    conn.execute("DELETE FROM handed_over WHERE id = ?", (record_id,))
    conn.commit()
    conn.close()

    flash('Handed Over record deleted successfully!', 'info')
    return redirect(url_for('handed_over'))

@app.route('/receipt_page')
def receipt_page():
    conn = get_db_connection()
    handed_overs = conn.execute("""
        SELECT handed_over.*, blood_requests.patient_name
        FROM handed_over
        LEFT JOIN blood_requests ON handed_over.reference_number = blood_requests.reference_number
    """).fetchall()
    conn.close()
    return render_template('receipt_page.html', handed_overs=handed_overs)

@app.route('/download_receipt/<int:id>')
def download_receipt(id):
    conn = get_db_connection()
    handed_over = conn.execute("""
        SELECT handed_over.*, blood_requests.patient_name, blood_requests.blood_group, 
               donors.name AS donor_name, donors.blood_group AS donor_blood_group, donors.donation_date
        FROM handed_over
        LEFT JOIN blood_requests ON handed_over.reference_number = blood_requests.reference_number
        LEFT JOIN donors ON donors.blood_group = blood_requests.blood_group
        WHERE handed_over.id = ?
    """, (id,)).fetchone()
    conn.close()

    if handed_over is None:
        flash("Handed over record not found.", "danger")
        return redirect(url_for('handed_over'))

    html_content = render_template('receipt_template.html', handed_over=handed_over)
    pdf = BytesIO()
    pisa_status = pisa.CreatePDF(html_content, dest=pdf)
    pdf.seek(0)

    if pisa_status.err:
        flash("Error generating PDF.", "danger")
        return redirect(url_for('handed_over'))

    return send_file(pdf, as_attachment=True, download_name="receipt.pdf", mimetype='application/pdf')


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
