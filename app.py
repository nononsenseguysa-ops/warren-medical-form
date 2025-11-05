from flask import Flask, request, render_template_string, send_file
import io
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

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

        <!-- ALL 14 MEDICAL QUESTIONS -->
        <div class="form-section">
            <h2>11. Medical Underwriting Questions</h2>
            <p>Please answer <strong>ALL</strong> questions. If "Yes", provide full details.</p>

            <h3>11.1 Tumours, growths, cancerous or non-cancerous conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_1" value="yes" onclick="toggleDetails('q11_1_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_1" value="no" onclick="toggleDetails('q11_1_details', false)" required> No</label><br>
            <div id="q11_1_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_1_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_1_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_1_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_1_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_1_treatment">
            </div>

            <h3>11.2 Heart and circulation conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_2" value="yes" onclick="toggleDetails('q11_2_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_2" value="no" onclick="toggleDetails('q11_2_details', false)" required> No</label><br>
            <div id="q11_2_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_2_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_2_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_2_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_2_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_2_treatment">
            </div>

            <h3>11.3 Diabetes and sugar-related disorders?</h3>
            <label class="yes-no"><input type="radio" name="q11_3" value="yes" onclick="toggleDetails('q11_3_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_3" value="no" onclick="toggleDetails('q11_3_details', false)" required> No</label><br>
            <div id="q11_3_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_3_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_3_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_3_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_3_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_3_treatment">
            </div>

            <h3>11.4 Respiratory conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_4" value="yes" onclick="toggleDetails('q11_4_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_4" value="no" onclick="toggleDetails('q11_4_details', false)" required> No</label><br>
            <div id="q11_4_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_4_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_4_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_4_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_4_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_4_treatment">
            </div>

            <h3>11.5 Ear, nose and throat conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_5" value="yes" onclick="toggleDetails('q11_5_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_5" value="no" onclick="toggleDetails('q11_5_details', false)" required> No</label><br>
            <div id="q11_5_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_5_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_5_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_5_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_5_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_5_treatment">
            </div>

            <h3>11.6 Eye conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_6" value="yes" onclick="toggleDetails('q11_6_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_6" value="no" onclick="toggleDetails('q11_6_details', false)" required> No</label><br>
            <div id="q11_6_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_6_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_6_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_6_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_6_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_6_treatment">
            </div>

            <h3>11.7 Digestive system conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_7" value="yes" onclick="toggleDetails('q11_7_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_7" value="no" onclick="toggleDetails('q11_7_details', false)" required> No</label><br>
            <div id="q11_7_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_7_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_7_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_7_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_7_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_7_treatment">
            </div>

            <h3>11.8 Urinary system conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_8" value="yes" onclick="toggleDetails('q11_8_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_8" value="no" onclick="toggleDetails('q11_8_details', false)" required> No</label><br>
            <div id="q11_8_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_8_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_8_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_8_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_8_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_8_treatment">
            </div>

            <h3>11.9 Nervous system conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_9" value="yes" onclick="toggleDetails('q11_9_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_9" value="no" onclick="toggleDetails('q11_9_details', false)" required> No</label><br>
            <div id="q11_9_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_9_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_9_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_9_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_9_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_9_treatment">
            </div>

            <h3>11.10 Musculoskeletal conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_10" value="yes" onclick="toggleDetails('q11_10_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_10" value="no" onclick="toggleDetails('q11_10_details', false)" required> No</label><br>
            <div id="q11_10_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_10_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_10_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_10_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_10_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_10_treatment">
            </div>

            <h3>11.11 Endocrine system conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_11" value="yes" onclick="toggleDetails('q11_11_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_11" value="no" onclick="toggleDetails('q11_11_details', false)" required> No</label><br>
            <div id="q11_11_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_11_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_11_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_11_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_11_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_11_treatment">
            </div>

            <h3>11.12 Blood disorders?</h3>
            <label class="yes-no"><input type="radio" name="q11_12" value="yes" onclick="toggleDetails('q11_12_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_12" value="no" onclick="toggleDetails('q11_12_details', false)" required> No</label><br>
            <div id="q11_12_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_12_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_12_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_12_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_12_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_12_treatment">
            </div>

            <h3>11.13 Mental health conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_13" value="yes" onclick="toggleDetails('q11_13_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_13" value="no" onclick="toggleDetails('q11_13_details', false)" required> No</label><br>
            <div id="q11_13_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_13_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_13_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_13_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_13_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_13_treatment">
            </div>

            <h3>11.14 Any other conditions?</h3>
            <label class="yes-no"><input type="radio" name="q11_14" value="yes" onclick="toggleDetails('q11_14_details', true)"> Yes</label>
            <label class="yes-no"><input type="radio" name="q11_14" value="no" onclick="toggleDetails('q11_14_details', false)" required> No</label><br>
            <div id="q11_14_details" class="details">
                <label>Symptoms/Diagnosis:</label><textarea name="q11_14_symptoms" rows="2"></textarea><br>
                <label>Date First Diagnosed:</label><input type="date" name="q11_14_first"><br>
                <label>Last Consultation:</label><input type="date" name="q11_14_last"><br>
                <label>Medicine & Dosage:</label><textarea name="q11_14_medicine" rows="2"></textarea><br>
                <label>Last Treatment:</label><input type="date" name="q11_14_treatment">
            </div>
        </div>

        <button type="submit">Submit & Download PDF</button>
    </form>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        data = request.form.to_dict()
        data['submitted'] = datetime.now().strftime('%Y-%m-%d %H:%M')

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        story = [Paragraph("Warren Heroldt Medical Aid Application", styles['Title'])]
        story.append(Spacer(1, 12))
        for k, v in data.items():
            if v:
                story.append(Paragraph(f"<b>{k.replace('_', ' ').title()}:</b> {v}", styles['Normal']))
                story.append(Spacer(1, 6))
        doc.build(story)
        buffer.seek(0)

        print("NEW SUBMISSION:")
        for k, v in data.items():
            print(f"{k}: {v}")

        return send_file(buffer, as_attachment=True, download_name=f"WarrenHeroldt_Application_{data.get('surname', 'User')}.pdf", mimetype='application/pdf')
    
    return render_template_string(FORM_HTML)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)