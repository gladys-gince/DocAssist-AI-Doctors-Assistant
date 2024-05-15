from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import psycopg2
from psycopg2 import sql
from flask_cors import CORS
import os
import io
from datetime import datetime
import base64
import re
import pytz
from dotenv import load_dotenv
import time
# from model import pipe,classifier

load_dotenv()

india_timezone = pytz.timezone('Asia/Kolkata')

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'wav'}

app = Flask(__name__, static_folder="public", static_url_path="/public")
app.secret_key = os.getenv("SECRET_KEY")
CORS(app)

app.config['UPLOAD_FOLDER'] = 'uploads'
dbname = os.getenv("DB_NAME")
user = os.getenv("USER")
password = os.getenv("PASSWORD")
host = os.getenv("HOST")
port = os.getenv("PORT")

conn = psycopg2.connect(dbname=dbname, user=user,
                        password=password, host=host, port=port)
cursor = conn.cursor()


""" 
Functions
"""


def insert_Query(query, param):
    cursor.execute(query, param)
    conn.commit()
    return


def fetchAll_Query(query, param=()):
    select_query = sql.SQL(query)
    cursor.execute(select_query, param)
    result = cursor.fetchall()
    return result


def fetchOne_Query(query, param=()):
    select_query = sql.SQL(query)
    cursor.execute(select_query, param)
    result = cursor.fetchone()
    return result


def doctor_timing():
    rows = fetchAll_Query("SELECT * FROM doctor_timing")
    specialist, doctor_name, doctor_time, doctor_day = [[] for _ in range(4)]
    specialist, doctor_name, doctor_time, doctor_day = [row[1] for row in rows], [
        row[2] for row in rows], [row[3] for row in rows], [row[4] for row in rows]
    return specialist, doctor_name, doctor_time, doctor_day


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def list_to_string(l):
    s = ''
    for i in l:
        s += str(i)
    return s


def available_doctors():
    current_datetime = datetime.now(india_timezone)
    current_day = current_datetime.strftime("%A")
    result = fetchAll_Query(
        "SELECT specialist,name,timing FROM doctor_timing WHERE day = %s;", (current_day,))
    return result


def pending_appointment():
    pending_count = fetchOne_Query(
        "SELECT COUNT(*) FROM appointments WHERE DATE(doctor_date) = CURRENT_DATE;")[0]
    completed_count = fetchOne_Query(
        "SELECT COUNT(*) FROM appointment_history WHERE LEFT(\"Appointment Time\", 10)::date = CURRENT_DATE;")[0]
    return pending_count, completed_count


def doctor_and_patient():
    result1 = fetchOne_Query("SELECT COUNT(*) FROM doctor_timing;")[0]
    result2 = fetchOne_Query(
        "SELECT COUNT(*) FROM user_data where type = 'user';")[0]
    result3 = fetchOne_Query("SELECT COUNT(*) FROM appointment_history;")[0]
    return result1, result2, result3


def top_doctor():
    result = fetchAll_Query("""SELECT "Doctor Name", COUNT(*) AS "Appointment Count" FROM appointment_history WHERE EXTRACT(MONTH FROM TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS.US')) = EXTRACT(MONTH FROM CURRENT_DATE) GROUP BY "Doctor Name";""")
    max_iterations = min(3, len(result))
    for i in range(max_iterations):
        result2 = fetchOne_Query(
            "SELECT profile_photo FROM user_demographic where name = %s;", (result[i][0],))[0]
        image_bytes = io.BytesIO(result2)
        base64_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
        result[i] = result[i] + (base64_image,)
    return result


transcriptin = "Hello, Doctor. My name is Gladys. I am 21 years old and female. I've been experiencing persistent cough , high fever , and fatigue for the past few days. I got my influenza vaccine a couple of months ago. Hello, Gladys. Based on your symptoms and recent influenza vaccination, it is likely that you have Hypertension . Do you have any underlying health conditions ? Are you currently taking any medications? I recently had a bypass surgery as well. I am regularly taking CTZ Tablet. Last time you had prescribed Allegra M Tablet . I would prescribe to take Shotmax spray every morning and keep an eye on your symptoms. Additionally, I recommend a nasal swab test to confirm the Hypertension diagnosis and to check for any secondary infections. If there's any worsening, contact our office immediately. Thank you, Doctor. I'll follow your advice and get the nasal swab test done as soon as possible and buy the prescribed medication."


""" 
API Endpoints
 """


@app.route('/', methods=['GET', 'POST'])
def main():
    try:
        if request.method == 'GET':
            if 'access' in session:
                if session['access'] == 'user':
                    return redirect(url_for('home'))
                elif session['access'] == 'doctor':
                    return redirect(url_for('dashboard'))
                elif session['access'] == 'admin':
                    return redirect(url_for('admin'))
                else:
                    return render_template("login.html")
            else:
                return render_template("login.html")

        elif request.method == 'POST':
            gmail = request.form.get('gmail')
            password = request.form.get('password')
            result = fetchOne_Query(
                "SELECT * FROM user_data WHERE gmail = %s;", (gmail,))
            print(result)
            if result and password == result[2]:
                res = fetchOne_Query(
                    "SELECT * FROM user_demographic WHERE user_id = %s;", (result[0],))
                session['name'], session['access'], session['user_id'] = res[1], result[3], res[0]
                if session['access'] == 'user':
                    return redirect(url_for('home'))
                elif session['access'] == 'doctor':
                    return redirect(url_for('dashboard'))
                elif session['access'] == 'admin':
                    return redirect(url_for('admin'))

            return redirect(url_for('invalid' if result else 'notfound'))
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("error.html")


@app.route('/register', methods=['GET', 'POST'])
def register():
    try:
        if request.method == 'GET':
            if 'access' in session:
                if session['access'] == 'user':
                    return redirect(url_for('home'))
                elif session['access'] == 'doctor':
                    return redirect(url_for('dashboard'))
                elif session['access'] == 'admin':
                    return redirect(url_for('admin'))
                else:
                    return render_template("register.html")
            else:
                return render_template("register.html")

        elif request.method == 'POST':
            if session and session['access']:
                if session['access'] == 'user':
                    return redirect(url_for('home'))
                elif session['access'] == 'doctor':
                    return redirect(url_for('dashboard'))
                elif session['access'] == 'admin':
                    return redirect(url_for('admin'))
            else:
                email = request.form.get('email')
                password = request.form.get('password')
                last_row_data = fetchOne_Query(
                    "SELECT * FROM user_data ORDER BY user_id DESC LIMIT 1;")
                return redirect(url_for('demographics', data=last_row_data[0]+1, email=email, password=password))

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("error.html")


@app.route('/home', methods=['GET'])
def home():
    try:

        if session['access'] == 'user':
            specialist, doctor_name, doctor_time, doctor_day = doctor_timing()
            res1 = fetchAll_Query(
                "SELECT * FROM appointments WHERE user_id = %s;", (session['user_id'],))
            res2 = fetchOne_Query(
                "SELECT * FROM user_demographic WHERE user_id = %s;", (session['user_id'],))

            img = res2[6] if res2 else None
            base64_image = base64.b64encode(io.BytesIO(
                img).getvalue()).decode('utf-8') if img else None
            data1 = res1 if res2 else None

            return render_template("home.html", specialist=specialist, doctor_name=doctor_name, doctor_time=doctor_time, doctor_day=doctor_day, appointments=data1, profile_photo=base64_image, user_name=res2[1] if res2 else None)

        else:
            return redirect('/logout')

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("error.html")


@app.route('/demographics', methods=['GET', 'POST'])
def demographics():
    try:
        if request.method == 'GET':
            if not session:
                data_received = request.args.get(
                    'data', 'default_value_if_not_provided')
                temp_email = request.args.get(
                    'email', 'default_value_if_not_provided')
                temp_password = request.args.get(
                    'password', 'default_value_if_not_provided')
                return render_template("demographics.html", data=data_received, email=temp_email, password=temp_password)
            else:
                return redirect('/logout')
        elif request.method == 'POST':
            if not session:
                user_id = request.form.get('user_id')
                email = request.form.get('email')
                password = request.form.get('password')
                name = request.form.get('name')
                gender = request.form.get('gender')
                contact = request.form.get('contact')
                blood_group = request.form.get('blood_group')
                dob = request.form.get('dob')
                photo = request.files['photo']
                photo_data = photo.read()
                address = request.form.get('address')

                insert_Query("INSERT INTO user_data (user_id,gmail, password, type) VALUES (%s,%s, %s, %s);",
                             (user_id, email, password, 'user'))

                insert_Query("""INSERT INTO user_demographic (user_id, name, gender, contact, blood_group, dob, profile_photo, address) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);""",
                             (user_id, name, gender, contact, blood_group, dob, psycopg2.Binary(photo_data), address))

                session['name'] = name
                session['access'] = 'user'
                session['user_id'] = user_id

                return redirect(url_for('home'))
            else:
                return redirect('/logout')

    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("error.html")


@app.route('/book_appointment', methods=['POST'])
def bookAppointment():
    try:
        if session and session['access'] == 'user':
            doctor_type = request.form.get('docter-type')
            doctor_name = request.form.get('docter-name')
            doctor_date = request.form.get('appointment-date')

            insert_Query(""" INSERT INTO appointments (user_id, doctor_type,doctor_name, doctor_date) VALUES (%s, %s, %s, %s);""", (
                session['user_id'],
                doctor_type,
                doctor_name,
                doctor_date,
            ))
            return jsonify({'msg': 'received'})

        else:
            return redirect('/')
    except Exception as e:
        print(f"An error occurred: {e}")
        return render_template("error.html")


@app.route('/logout', methods=['GET'])
def logout():
    if session:
        session.clear()
        return redirect('/')
    else:
        return redirect('/')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if session['access'] == 'doctor':
        res = fetchAll_Query(
            "SELECT * FROM appointments WHERE doctor_name = %s;", (session['name'],))
        user_data = []
        for row in res:
            userr = fetchOne_Query(
                "SELECT * FROM user_demographic WHERE user_id = %s;", (row[1],))
            userr = (row[0],) + userr
            user_data.append(userr)
        return render_template("dashboard.html", data=user_data)
    else:
        return redirect('/')


@app.route('/recording', methods=['POST'])
def recording():
    if session['access'] == 'doctor':
        audio_data = request.files['audio']
        audio_data.save('uploaded_audio.wav')
        user_id = request.form['user_id']
        appointment_id = request.form['appointment_id']
        if audio_data:
            current_datetime = datetime.now(india_timezone)
            
            from model import pipe, classifier
            from analysis import pratham, gladys

            start_time = time.time()
            audio_bytes = audio_data.read()
            transcription = pipe(audio_bytes)["text"]
            end_time = time.time()
            print('Time Taken to Transcript : ', end_time - start_time)
            print('Transcription:', transcription)

            sentiment = classifier(transcriptin)[0]['label']

            output1 = pratham(transcriptin)
            output2 = gladys(transcriptin)

            res = fetchOne_Query(
                "SELECT * FROM appointments WHERE srno = %s;", (appointment_id,))
            doctor_name = res[3]

            regular_medicines = list_to_string(output2['regular_medicines'])
            last_prescribed_medicines = list_to_string(
                output2['last_prescribed_medicines'])
            current_prescribed_medicines = list_to_string(
                output2['current_prescribed_medicines'])
            immunization_history = list_to_string(
                output2['immunization_history'])

            detected_symptoms = list_to_string(output1['detected_symptoms'])
            detected_diseases = list_to_string(output1['detected_diseases'])
            detected_surgery = list_to_string(output1['detected_surgery'])
            detected_tests = list_to_string(output1['detected_tests'])

            conversation_tone = sentiment
            voice_conversation = audio_data.read()

            data = (appointment_id, user_id, doctor_name, current_datetime, regular_medicines, last_prescribed_medicines, current_prescribed_medicines,
                    immunization_history, detected_symptoms, detected_diseases, detected_surgery, detected_tests, conversation_tone, voice_conversation)

            insert_query = """
            INSERT INTO appointment_history ("Appointment ID", "Patient ID","Doctor Name","Appointment Time","Regular Medicines","Last Prescribed Medicines","Current Prescribed Medicine","Immunization History","Detected Symptoms","Detected Diseases","Detected Surgery","Detected Tests","Conversation Tone","Voice Recording")
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s, %s, %s, %s, %s, %s);
            """

            insert_Query(insert_query, data)

            delete_query = """
            delete from appointments where srno = %s;
            """

            insert_Query(delete_query, (appointment_id,))

            print('[Data Added to DB] . . .')

            # os.remove(filepath)

            return jsonify({'message': 'Recording received and saved successfully'})
    else:
        return redirect('/')


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if request.method == 'GET':
        select_query = sql.SQL(
            "SELECT * FROM user_demographic WHERE user_id = %s;")
        cursor.execute(select_query, (session['user_id'],))
        res = cursor.fetchone()
        if res:
            img = res[6]
            image_bytes = io.BytesIO(img)
            base64_image = base64.b64encode(
                image_bytes.getvalue()).decode('utf-8')
            res = tuple(value if i != 6 else base64_image for i,
                        value in enumerate(res))
            return render_template('profile.html', data=res)


@app.route('/last_appointments', methods=['GET', 'POST'])
def lastAppointment():
    if request.method == 'GET':

        if session['access'] == 'user':
            column_names = ["Appointment ID", "Doctor Name", "Appointment Time", "Current Prescribed Medicine",
                            "Detected Symptoms", "Detected Diseases", "Detected Surgery", "Detected Tests"]
            select_query1 = sql.SQL("SELECT ({}) FROM appointment_history WHERE {} = %s;").format(
                sql.SQL(', ').join(map(sql.Identifier, column_names)),
                sql.Identifier("Patient ID")
            )
            cursor.execute(select_query1, (session['user_id'],))
            res1 = cursor.fetchall()
        elif session['access'] == 'doctor':
            column_names = ["Appointment ID", "Patient ID", "Appointment Time", "Current Prescribed Medicine",
                            "Detected Symptoms", "Detected Diseases", "Detected Surgery", "Detected Tests"]
            select_query1 = sql.SQL("SELECT ({}) FROM appointment_history WHERE {} = %s;").format(
                sql.SQL(', ').join(map(sql.Identifier, column_names)),
                sql.Identifier("Doctor Name")
            )
            cursor.execute(select_query1, (session['name'],))
            res1 = cursor.fetchall()
            print(res1[:2])

        select_query2 = sql.SQL(
            "SELECT * FROM user_demographic WHERE user_id = %s;")
        cursor.execute(select_query2, (session['user_id'],))
        res2 = cursor.fetchone()
        # res2 = fetchOne_Query(select_query2,(session['user_id'],))
        res_data = []
        if res2 and res1:
            for i in res1:
                temp_data = i[0]
                temp_data = temp_data.replace('(', '').replace(')', '')
                temp_data = temp_data.replace('"', '')
                pattern = re.compile(r',(?![^\[]*\])')
                parts = pattern.split(temp_data)
                parts = [part.strip() for part in parts]
                res_data.append(parts)
            img = res2[6]
            image_bytes = io.BytesIO(img)
            base64_image = base64.b64encode(
                image_bytes.getvalue()).decode('utf-8')
        if session['access'] == 'user':
            return render_template('lastAppointment.html', user_name=res2[1], profile_img=base64_image, appointments=res_data, acc_type='user')
        elif session['access'] == 'doctor':
            return render_template('lastAppointment.html', user_name=res2[1], profile_img=base64_image, appointments=res_data, acc_type='doctor')


@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        pending_count, completed_count = pending_appointment()
        result = available_doctors()
        top_performer = top_doctor()
        doctor_count, patient_count, appointment_count = doctor_and_patient()
        select_query = sql.SQL(
            "SELECT name,profile_photo FROM user_demographic WHERE user_id = %s;")
        cursor.execute(select_query, (session['user_id'],))
        res = cursor.fetchone()
        img = res[1]
        image_bytes = io.BytesIO(img)
        base64_image = base64.b64encode(image_bytes.getvalue()).decode('utf-8')
        return render_template('admin_dashboard.html', username=res[0], profile_photo=base64_image, doctor_details=result, pending_count=pending_count, completed_count=completed_count, doctor_count=doctor_count, patient_count=patient_count, appointment_count=appointment_count, top_performer=top_performer)


@app.route('/notfound', methods=['GET'])
def notfound():
    if request.method == 'GET':
        return render_template('notfound.html')


@app.route('/front', methods=['GET'])
def front():
    return render_template('front.html')


@app.route('/doctorList', methods=['GET'])
def doctorList():
    # doctorList = doctor_timing()
    doctorList = fetchAll_Query("SELECT * FROM doctor_timing")
    print(doctorList)
    return render_template('doctor.html', doctorDetails=doctorList)


@app.route('/analysis', methods=['GET', 'POST'])
def analysis():
    if request.method == 'GET':
        return render_template('analysis.html')
    else:
        data = request.json
        selected_option = data['selectedOption']
        if type(selected_option) != list:
            if selected_option == 'overall_doctor':
                data = fetchAll_Query(
                    'select "Appointment ID","Doctor Name" from appointment_history;')
                return jsonify({'data': data})
            elif selected_option == '30days_doctor':
                data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '30 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == '90days_doctor':
                data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '90 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == '180days_doctor':
                data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '180 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == '365days_doctor':
                data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '365 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == 'overall_disease':
                data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history;""")
                return jsonify({'data': data})
            elif selected_option == '30days_disease':
                data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '30 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == '90days_disease':
                data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '90 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == '180days_disease':
                data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '180 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == '365days_disease':
                data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '365 DAY' ORDER BY "Appointment Time" DESC;""")
                return jsonify({'data': data})
            elif selected_option == 'age_vs_disease':
                data = fetchAll_Query("""SELECT EXTRACT(YEAR FROM AGE(a."Appointment Time"::timestamp, u.dob::timestamp)) AS age, a."Detected Diseases" FROM user_demographic u JOIN appointment_history a ON u.user_id = a."Patient ID";""")
                return jsonify({'data': data})
        else:
            send_data = {}
            idx = 1
            for i in selected_option:
                if i == 'overall_doctor':
                    data = fetchAll_Query(
                        'select "Appointment ID","Doctor Name" from appointment_history;')
                    send_data[idx] = data
                    idx += 1
                elif i == '30days_doctor':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '30 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '90days_doctor':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '90 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '180days_doctor':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '180 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '365days_doctor':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Doctor Name" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '365 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == 'overall_disease':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '30days_disease':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '30 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '90days_disease':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '90 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '180days_disease':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '180 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == '365days_disease':
                    data = fetchAll_Query("""SELECT "Appointment ID", "Detected Diseases" FROM appointment_history WHERE TO_TIMESTAMP("Appointment Time", 'YYYY-MM-DD HH24:MI:SS') >= CURRENT_DATE - INTERVAL '365 DAY' ORDER BY "Appointment Time" DESC;""")
                    send_data[idx] = data
                    idx += 1
                elif i == 'age_vs_disease':
                    data = fetchAll_Query("""SELECT EXTRACT(YEAR FROM AGE(a."Appointment Time"::timestamp, u.dob::timestamp)) AS age, a."Detected Diseases" FROM user_demographic u JOIN appointment_history a ON u.user_id = a."Patient ID";""")
                    send_data[idx] = data
                    idx += 1
                elif i == 'age_vs_symptoms':
                    data = fetchAll_Query("""SELECT EXTRACT(YEAR FROM AGE(a."Appointment Time"::timestamp, u.dob::timestamp)) AS age, a."Detected Symptoms" FROM user_demographic u JOIN appointment_history a ON u.user_id = a."Patient ID" WHERE a."Appointment Time"::timestamp >= CURRENT_DATE - INTERVAL '30 DAY';""")
                    send_data[idx] = data
                    idx += 1
            return jsonify(send_data)
        print(selected_option)
        return "gotch"


if __name__ == "__main__":
    app.run(debug=False)
    # app.run(debug=True, host="::", port=3390)
