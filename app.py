from flask import Flask, request, render_template_string, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

# HTML FORM TEMPLATE
HTML_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Warren Heroldt - Medical Aid Application</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f9f9f9; }
        .container { max-width: 800px; margin: auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 15px rgba(0,0,0,0.1); }
        h1 { color: #1a5276; text-align: center; }
        h2 { color: #2874a6; border-bottom: 2px solid #3498db; padding-bottom: 5px; }
        label { display: block; margin: 15px 0 5px; font-weight: bold; }
        input, select, textarea { width: 100%; padding: 10px; margin: 5px 0; border: 1px solid #ccc; border-radius: 5px; }
        .radio-group { margin: 10px 0; }
        .radio-group label { display: inline; margin-right: 20px; font-weight: normal; }
        .conditional { display: none; margin-left: 20px; padding: 15px; background: #f0f8ff; border-left: 4px solid #3498db; }
        button { background: #2874a6; color: white; padding: 12px 30px; border: none; border-radius: 5px; font-size: 16px; cursor: pointer; margin-top: 20px; }
        button:hover { background: #1a5276; }
        .contact { text-align: center; margin-bottom: 30px; color: #2874a6; font-weight: bold; }
    </style>
</head>
<body>
    <div class="container">
        <h1>Warren Heroldt - Medical Aid Application</h1>
        <p class="contact">Contact: Warren Heroldt, Cell: 082 336 2414</p>

        <form method="POST" action="/submit">
            <h2>1. Personal Details</h2>
            <label>Surname:</label>
            <input type="text" name="surname" required>
            
            <label>First Name(s):</label>
            <input type="text" name="firstname" required>
            
            <label>ID Number:</label>
            <input type="text" name="id_number" required>
            
            <label>Email:</label>
            <input type="email" name="email" required>
            
            <label>Cell Number:</label>
            <input type="text" name="cell" required>

            <h2>2. Spouse Included?</h2>
            <div class="radio-group">
                <label><input type="radio" name="spouse" value="No" onclick="toggleSpouse()" checked> No</label>
                <label><input type="radio" name="spouse" value="Yes" onclick="toggleSpouse()"> Yes</label>
            </div>
            <div id="spouse-details" class="conditional">
                <label>Spouse Full Name:</label>
                <input type="text" name="spouse_name">
                <label>Spouse ID:</label>
                <input type="text" name="spouse_id">
            </div>

            <h2>3. Any Pre-existing Medical Conditions?</h2>
            <div class="radio-group">
                <label><input type="radio" name="medical" value="No" onclick="toggleMedical()" checked> No</label>
                <label><input type="radio" name="medical" value="Yes" onclick="toggleMedical()"> Yes</label>
            </div>
            <div id="medical-details" class="conditional">
                <label>Describe Condition(s):</label>
                <textarea name="medical_condition" rows="3"></textarea>
            </div>

            <h2>11. Medical Underwriting Questions</h2>
            <p><strong>Please answer ALL questions. If "Yes", provide full details.</strong></p>

            <button type="submit">Submit & Download PDF</button>
        </form>
    </div>

    <script>
        function toggleSpouse() {
            document.getElementById('spouse-details').style.display = 
                document.querySelector('input[name="spouse"]:checked').value === 'Yes' ? 'block' : 'none';
        }
        function toggleMedical() {
            document.getElementById('medical-details').style.display = 
                document.querySelector('input[name="medical"]:checked').value === 'Yes' ? 'block' : 'none';
        }
    </script>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/submit', methods=['POST'])
def submit():
    # Collect form data
    data = {
        'surname': request.form['surname'],
        'firstname': request.form['firstname'],
        'id_number': request.form['id_number'],
        'email': request.form['email'],
        'cell': request.form['cell'],
        'spouse': request.form['spouse'],
        'spouse_name': request.form.get('spouse_name', ''),
        'spouse_id': request.form.get('spouse_id', ''),
        'medical': request.form['medical'],
        'medical_condition': request.form.get('medical_condition', '')
    }

    # Generate PDF
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    pdf.setFont("Helvetica-Bold", 16)
    pdf.drawString(50, height - 50, "Warren Heroldt - Medical Aid Application")
    pdf.setFont("Helvetica", 12)
    pdf.drawString(50, height - 70, "Contact: Warren Heroldt, Cell: 082 336 2414")
    pdf.line(50, height - 80, width - 50, height - 80)

    y = height - 120
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "1. Personal Details")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Surname: {data['surname']}")
    y -= 20
    pdf.drawString(70, y, f"First Name: {data['firstname']}")
    y -= 20
    pdf.drawString(70, y, f"ID Number: {data['id_number']}")
    y -= 20
    pdf.drawString(70, y, f"Email: {data['email']}")
    y -= 20
    pdf.drawString(70, y, f"Cell: {data['cell']}")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "2. Spouse Included?")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Answer: {data['spouse']}")
    if data['spouse'] == 'Yes':
        y -= 20
        pdf.drawString(70, y, f"Spouse Name: {data['spouse_name']}")
        y -= 20
        pdf.drawString(70, y, f"Spouse ID: {data['spouse_id']}")
    y -= 30

    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(50, y, "3. Pre-existing Medical Conditions?")
    y -= 20
    pdf.setFont("Helvetica", 11)
    pdf.drawString(70, y, f"Answer: {data['medical']}")
    if data['medical'] == 'Yes':
        y -= 20
        pdf.drawString(70, y, f"Details: {data['medical_condition']}")
    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "11. Medical Underwriting Questions")
    y -= 25
    pdf.setFont("Helvetica", 11)
    pdf.drawString(50, y, "Please answer ALL questions. If 'Yes', provide full details.")
    y -= 30
    pdf.drawString(50, y, "(Full underwriting to follow upon submission)")

    pdf.showPage()
    pdf.save()
    buffer.seek(0)

    # === SEND EMAIL TO WARREN ===
    sender_email = "youremail@gmail.com"           # CHANGE THIS
    sender_password = "your_app_password"          # CHANGE THIS (Gmail App Password)
    recipient = "WarrenH@StatusMarketing.co.za"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = recipient
    msg['Subject'] = f"New Medical Form: {data['firstname']} {data['surname']}"

    part = MIMEBase('application', 'octet-stream')
    part.set_payload(buffer.getvalue())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment; filename="Medical_Form.pdf"')
    msg.attach(part)

    try:
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except Exception as e:
        print(f"Email failed: {e}")  # Won't break the form

    # Return PDF to user
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="Medical_Form.pdf",
        mimetype='application/pdf'
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
