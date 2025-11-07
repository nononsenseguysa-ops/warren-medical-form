from flask import Flask, request, render_template_string, send_file
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

app = Flask(__name__)

FORM_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Warren Heroldt - Medical Aid Application</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background: #f9f9f9; }
        .header { text-align: center; background: #003087; color: white; padding: 20px; }
        .form-section { background: white; margin: 20px 0; border: 1px solid #ddd; padding: 15px; border-radius: 5px; }
        .yes-no { display: inline-block; margin-right: 10px; }
        .details { display: none; margin-top: 10px; padding: 10px; background: #f0f8ff; border-radius: 3px; }
        input, select, textarea { width: 100%; padding: 8px; margin: 5px 0; box-sizing: border-box; }
        button { background: #f5821f; color: white; padding: 12px 24px; border: none; cursor: pointer; font-size: 16px; border-radius: 5px; margin-top: 20px; }
        button:hover { background: #e56a00; }
        .required { color: red; }
        h3 { margin-top: 20px; color: #003087; }
    </style>
    <script>
        function toggleDetails(id, show) {
            document.getElementById(id).style.display = show ? 'block' : 'none';
        }
        function toggleSpouse(show) {
            document.getElementById('spouse_details').style.display = show ? 'block' : 'none';
        }
    </script>
</head>
<body>
    <div class="header">
        <h1>Warren Heroldt - Medical Aid Application</h1>
        <p>Contact: Warren Heroldt, Cell: 082 336 2414</p>
    </div>

    <form method="POST">
        <!-- PERSONAL INFO -->
        <div class="form-section">
            <h2>1. Personal Information (Main Applicant)</h2>
            <label>Cover Start Date: <span class="required">*</span></label>
            <input type="date" name="cover_start" required><br>

            <label>Title: <span class="required">*</span></label>
            <select name="title" required>
                <option>Mr</option><option>Mrs</option><option>Ms</option><option>Dr</option><option>Prof</option>
            </select><br>

            <label>Initials: <span class="required">*</span></label>
            <input type="text" name="initials" maxlength="2" required><br>

            <label>Surname: <span class="required">*</span></label>
            <input type="text" name="surname" required><br>

            <label>First Names: <span class="required">*</span></label>
            <input type="text" name="first_names" required><br>

            <label>ID or Passport Number: <span class="required">*</span></label>
            <input type="text" name="id_number" required><br>

            <label>Gender: <span class="required">*</span></label>
            <select name="gender" required>
                <option>Male</option><option>Female</option><option>Other</option>
            </select><br>

            <label>Date of Birth: <span class="required">*</span></label>
            <input type="date" name="dob" required><br>

            <label>Race: <span class="required">*</span></label>
            <select name="race" required>
                <option>African</option><option>Coloured</option><option>Indian/Asian</option><option>White</option><option>Other</option><option>Prefer not to disclose</option>
            </select><br>

            <label>Cellphone: <span class="required">*</span></label>
            <input type="tel" name="cellphone" required><br>

            <label>Email Address: <span class="required">*</span></label>
            <input type="email" name="email" required><br>

            <label>Physical Address: <span class="required">*</span></label>
            <textarea name="physical_address" rows="3" required></textarea><br>

            <label>Postal address same as residential? <span class="required">*</span></label>
            <label class="yes-no"><input type="radio" name="same_postal" value="yes" onclick="toggleDetails('postal_details', false)" required> Yes</label>
            <label class="yes-no"><input type="radio" name="same_postal" value="no" onclick="toggleDetails('postal_details', true)" required> No</label><br>
            <div id="postal_details" class="details">
                <label>Postal Address:</label>
                <textarea name="postal_address" rows="3"></textarea>
            </div>
        </div>

        <!-- SPOUSE -->
        <div class="form-section">
            <h2>2. Spouse/Partner (if applying)</h2>
            <label>Applying for spouse? <span class="required">*</span></label>
            <label class="yes-no"><input type="radio" name="spouse_applying" value="yes" onclick="toggleSpouse(true)" required> Yes</label>
            <label class="yes-no"><input type="radio" name="spouse_applying" value="no" onclick="toggleSpouse(false)" required> No</label><br>
            <div id="spouse_details" class="details">
                <label>Spouse Title:</label><select name="spouse_title"><option>Mr</option><option>Mrs</option><option>Ms</option></select><br>
                <label>Spouse Initials:</label><input type="text" name="spouse_initials" maxlength="2"><br>
                <label>Spouse Surname:</label><input type="text" name="spouse_surname"><br>
                <label>Spouse First Names:</label><input type="text" name="spouse_first_names"><br>
                <label>Spouse ID:</label><input type="text" name="spouse_id"><br>
                <label>Spouse DOB:</label><input type="date" name="spouse_dob"><br>
                <label>Spouse Cellphone:</label><input type="tel" name="spouse_cellphone"><br>
            </div>
        </div>

        <!-- MEDICAL QUESTIONS 11.1 to 11.14 -->
        <div class="form-section">
            <h2>11. Medical Underwriting Questions</h2>
            <p>Please answer <strong>ALL</strong> questions. If "Yes", provide full details.</p>

            {% for i in range(1, 15) %}
            <h3>11.{{ i }} {{ questions[i-1] }}</h3>
            <label class="yes-no"><input type="radio" name="q11_{{ i }}" value="yes" onclick="toggleDetails('q11_{{ i }}_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_{{ i }}" value="no" onclick="toggleDetails('q11_{{ i }}_details', false)" required> No</label><br>
            <div id="q11_{{ i }}_ thy_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_{{ i }}_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_{{ i }}_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_{{ i }}_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_{{ i }}_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_{{ i }}_treatment">
            </div>
            {% endfor %}
        </div>

        <button type="submit">Submit & Download PDF</button>
    </form>
</body>
</html>
"""

QUESTIONS = [
    "Tumours, growths, cancerous or non-cancerous conditions?",
    "Heart and circulation conditions?",
    "Diabetes and sugar-related disorders?",
    "Respiratory conditions?",
    "Ear, nose and throat conditions?",
    "Eye conditions?",
    "Digestive system conditions?",
    "Urinary system conditions?",
    "Nervous system conditions?",
    "Musculoskeletal conditions?",
    "Endocrine system conditions?",
    "Blood disorders?",
    "Mental health conditions?",
    "Any other conditions?"
]

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['submitted'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        # Generate PDF
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = []
        story.append(Paragraph("Warren Heroldt - Medical Aid Application", styles['Title']))
        story.append(Paragraph(f"Submitted: {data['submitted']}", styles['Normal']))
        story.append(Paragraph(f"Contact: Warren Heroldt, Cell: 082 336 2414", styles['Normal']))
        story.append(Spacer(1, 12))
        for k, v in data.items():
            if v and k != 'submitted':
                story.append(Paragraph(f"<b>{k.replace('_', ' ').title()}:</b> {v}", styles['Normal']))
                story.append(Spacer(1, 6))
        doc.build(story)
        buffer.seek(0)

        # === SEND EMAIL TO WARREN ===
        sender_email = "warrenh@statusmarketing.co.za"   # ← YOUR EMAIL
        sender_password = "your_app_password_here"       # ← GMAIL APP PASSWORD
        recipient = "warrenh@statusmarketing.co.za"

        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient
        msg['Subject'] = f"New Medical Form: {data.get('first_names', '')} {data.get('surname', '')}"

        part = MIMEBase('application', 'octet-stream')
        part.set_payload(buffer.getvalue())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', f'attachment; filename="Medical_Form_{data.get('surname', 'User')}.pdf"')
        msg.attach(part)

        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                server.login(sender_email, sender_password)
                server.send_message(msg)
            print("Email sent to Warren")
        except Exception as e:
            print(f"Email failed: {e}")

        # Return PDF to user
        buffer.seek(0)
        return send_file(buffer, as_attachment=True, download_name=f"WarrenHeroldt_Application_{data.get('surname', 'User')}.pdf", mimetype='application/pdf')
    
    return render_template_string(FORM_HTML, questions=QUESTIONS)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
