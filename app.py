import ast
import datetime
import hashlib
import json
import os
import random
import smtplib
import string
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import mysql.connector
import pandas as pd
from flask import Flask, render_template, request, redirect, flash, jsonify, session

from from_csv.el_from_csv import get_el
from from_csv.ml_mtl_lop_from_csv import get_ml_mtl_lop

app = Flask(__name__)

db = mysql.connector.connect(host="localhost", port="3306", user="root", database="facultyleavedb")
cursor = db.cursor()

drive_directory = "H:\\.shortcut-targets-by-id\\"

app.config['SECRET_KEY'] = 'f6f5372c8210fd221e2b4842e51af432'
app.config['DRIVE_DIRECTORIES'] = {
    "CSE": drive_directory + "1BUHQk3y7vWh5b354fI94PVY_pSPxOCa7\\CSE",
    "ECE": drive_directory + "1sxi1C8tQb4rOj30xLSnubSF8uyNYa4DF\\ECE",
    "MECH": drive_directory + "1sUWSOGjVJgwECV_5C37EvogdcPbrnRO6\\MECH",
    "CIVIL": drive_directory + "1_WEgUo8OtmadKQKi8NFKZ0pH7wuPbWDP\\CIVIL",
    "MBA": drive_directory + "1xCWj4xRnjBGu7fD1Zh2OXSY4LX0bBZsL\\MBA",
    "MCA": drive_directory + "1FwfZAkKwrtv3oJ_N-2DHLpuybjoqlUeD\\MCA",
    "SH": drive_directory + "1LcDBfZ7VSRouXjnJl-_K3at1UI2vT-KH\\SH"
}


def get_data(id, type):
    if session['role'] != 4:
        return redirect("/login")
    cursor.execute("select * from %s where id = %s" % (type, id,))
    result = cursor.fetchall()
    for i in range(len(result)):
        result[i] = list(result[i])
        del result[i][-1]
    cursor.reset()
    return result


@app.route("/")
def display_staff():
    if session['role'] != 4:
        return redirect("/login")
    return redirect("/login")
    cursor.execute("select * from staff")
    result = cursor.fetchall()
    cursor.reset()
    return render_template("index.html", table_content=enumerate(result))


@app.route("/staff/<id>", methods=["POST"])
def get_staff_details(id):
    if session['role'] != 4:
        return redirect("/login")
    cursor.execute("select name, department, doj from staff where id = %s" % (id,))
    result = cursor.fetchall()
    cursor.reset()
    return jsonify(result)


@app.route("/dashboard")
def display_dashboard():
    session_key = session.get('session_key')
    role = session.get('role')
    if session_key and role:
        if role == 4:
            cursor.execute("SELECT name FROM `staff` WHERE id=(SELECT id from user_login where SESSION_key=%s)",
                           (session_key,))
            name = cursor.fetchone()[0]
            cursor.reset()
            return render_template("dashboard.html", name=name)
        else:
            return redirect("/login")
    else:
        return redirect("/login")


def get_total_days(from_date, to_date):
    format = "%Y-%m-%d" if "-" in from_date else "%d.%m.%Y" if "." in from_date else "%d/%m/%Y"
    from_date = datetime.datetime.strptime(from_date, format)
    to_date = datetime.datetime.strptime(to_date, format)
    return (to_date - from_date).days + 1


@app.route("/staff/upload", methods=["GET", "POST"])
def upload_file():
    if session['role'] != 4:
        return redirect("/login")
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file:
            # Save the uploaded file to a desired location
            info = json.loads(request.form["info"])
            el = get_el(uploaded_file, info["sheetName"])
            ml, mtl, lop = get_ml_mtl_lop(uploaded_file, info["sheetName"])
            # Update the EL table
            print(ml)
            print(mtl)
            print(lop)
            for i in range(len(el)):
                row = el[i]
                print(row)
                try:
                    total = get_total_days(row[0], row[1])
                    cursor.execute(
                        'INSERT INTO el (id, dept, `from`, `to`, from_prefix, to_prefix, from_suffix, to_suffix, date_of_rejoin, total) VALUES ('
                        '%s, "%s", "%s", "%s", %s, %s, %s, %s, %s, %s)' %
                        (info["id"], info["department"], row[0], row[1],
                         row[2][0] if row[2][0] == 'NULL' else '"' + row[2][0] + '"',
                         row[2][1] if row[2][1] == 'NULL' else '"' + row[2][1] + '"',
                         row[2][2] if row[2][2] == 'NULL' else '"' + row[2][2] + '"',
                         row[2][3] if row[2][3] == 'NULL' else '"' + row[2][3] + '"',
                         row[3] if row[3] == 'NULL' else '"' + row[3] + '"', total))
                    db.commit()
                    cursor.reset()
                except Exception as e:
                    print("Error:", e, "Row:", row)
            # Update the ML, MTL, LOP table
            for name, table in [('ml', ml), ('mtl', mtl), ('lop', lop)]:
                if table:
                    for i in range(len(table)):
                        row = table[i]
                        print(row)
                        try:
                            total = get_total_days(row[0], row[1])
                            cursor.execute(
                                'INSERT INTO %s (id, dept, `from`, `to`, medical_fittness_on, from_prefix, to_prefix, from_suffix, to_suffix, '
                                'doj,total) VALUES (%s, "%s", "%s", "%s",%s, %s, %s, %s, %s, "%s", %s)' %
                                (name, info["id"], info["department"], row[0], row[1],
                                 row[3] if row[3] == 'NULL' else '\'["' + row[3] + '"]\'',
                                 row[4][0] if row[4][0] == 'NULL' else '"' + row[4][0] + '"',
                                 row[4][1] if row[4][1] == 'NULL' else '"' + row[4][1] + '"',
                                 row[4][2] if row[4][2] == 'NULL' else '"' + row[4][2] + '"',
                                 row[4][3] if row[4][3] == 'NULL' else '"' + row[4][3] + '"',
                                 row[5], total))
                            db.commit()
                            cursor.reset()
                        except Exception as e:
                            print(e)
            return {"status": "success"}
        return {"status": "failed"}


@app.route("/staff/get_sheet_names", methods=["POST"])
def get_sheet_names():
    if session['role'] != 4:
        return redirect("/login")
    uploaded_file = request.files["file"]
    if uploaded_file:
        # Save the uploaded file to a desired location
        sheet_names = pd.ExcelFile(uploaded_file).sheet_names
        return {"status": "success", "sheet_names": sheet_names}
    return {"status": "failed"}


def normalize_date(obj):
    for i in obj:
        for j in range(len(i)):
            if isinstance(i[j], bytes):
                i[j] = ast.literal_eval(i[j].decode("utf-8"))
            if isinstance(i[j], datetime.date):
                i[j] = i[j].strftime("%d-%m-%Y")
    return obj


@app.route("/el/<id>", methods=["GET", "POST"])
def display_el(id):
    result = get_data(id, "el")
    if request.method == "POST":
        print(result)
        return json.dumps(normalize_date(result))
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Earned Leave (EL)", len=len(result))


@app.route("/ml/<id>", methods=["GET", "POST"])
def display_ml(id):
    result = get_data(id, "ml")
    if request.method == "POST":
        return json.dumps(normalize_date(result))
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "Medical fitness on",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Medical Leave (ML)", len=len(result))


@app.route("/mtl/<id>", methods=["GET", "POST"])
def display_mtl(id):
    result = get_data(id, "mtl")
    if request.method == "POST":
        return json.dumps(normalize_date(result))
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "Medical fitness on",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Maternal Leave (MTL)",
                           len=len(result))


@app.route("/lop/<id>", methods=["GET", "POST"])
def display_lop(id):
    result = get_data(id, "lop")
    if request.method == "POST":
        return json.dumps(normalize_date(result))
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "Medical fitness on",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Loss Of Pay (LOP)", len=len(result))


def getExtension(filename):
    return os.path.splitext(filename)[1]


@app.route("/upload_document/<dept>/<id>/<type>/<l_id>", methods=["GET", "POST"])
def upload_document(dept, id, type, l_id):
    if session['role'] != 4:
        return redirect("/login")
    if request.method == "POST":
        uploaded_files = request.files.getlist('files')
        labels = request.form.getlist('fileNames')
        upload_folder = os.path.join(app.config["DRIVE_DIRECTORIES"][dept], id, type, l_id)
        print(upload_folder)
        labels[0] = "leave_form"
        os.makedirs(upload_folder, exist_ok=True)
        for i in range(len(uploaded_files)):
            uploaded_file = uploaded_files[i]
            label = labels[i]
            if uploaded_file:
                uploaded_file.save(os.path.join(upload_folder, label + getExtension(uploaded_file.filename)))
            else:
                flash('Invalid file format', 'error')
        return {"status": "success"}
    return "This is upload Page"


# Sharon Work Starts
@app.route('/login', methods=['GET', 'POST'])
def login():
    signined = None
    if request.method == 'GET':
        return render_template('login.html', signined="")
    elif request.method == 'POST':
        data = request.form
        mail_id = data['mail_id']
        password = data['password']

        if authenticate_user(mail_id, password):
            session_key = generate_session_key()
            update_session_key(mail_id, session_key)
            session['session_key'] = session_key
            signined = None
            return render_template('login.html', signined="true")
        else:
            return render_template('login.html', signined="false")


def authenticate_user(mail_id, password):
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    select_query = "SELECT id FROM user_login WHERE mail_id = %s AND password = %s"
    cursor.execute(select_query, (mail_id, hashed_password))
    user_id = cursor.fetchone()
    if user_id:
        return True
    else:
        return False


def generate_session_key():
    return ''.join(random.choices(string.ascii_letters + string.digits, k=24))


def update_session_key(mail_id, session_key):
    update_query = "UPDATE user_login SET session_key = %s WHERE mail_id = %s"
    cursor.execute(update_query, (session_key, mail_id))
    db.commit()


@app.route('/forget-password', methods=['GET', 'POST'])
def forgetPassword():
    signined = None
    if request.method == 'GET':
        return render_template('forget_password.html')
    elif request.method == 'POST':
        data = request.form
        mail_id = data['mail']
        if check_email_in_database(mail_id):
            otp = str(otp_gen())
            session['otp'] = otp
            session['email_forgot'] = mail_id
            send_html_email(mail_id, otp, "Users")
            return render_template('one_time_password.html', otpf="")
        else:
            return render_template('forget_password.html', emailf="false")


def check_email_in_database(email):
    query = "SELECT COUNT(*) FROM user_login WHERE mail_id = %s"
    cursor.execute(query, (email,))
    result = cursor.fetchone()[0]

    if result > 0:
        return True
    else:
        return False


def otp_gen():
    return random.randint(100000, 999999)


def send_html_email(receiver_email, otp, name):
    sender_email = "sharonjoseph52@yahoo.com"
    password = "zgodamlpduxhfnrf"
    subject = "Faculty Login Password Change OTP"

    date = datetime.datetime.now().strftime("%B %d, %Y")

    html_content_1 = """
                    <!DOCTYPE html>
                    <html lang="en">
                    <head>
                        <meta charset="UTF-8" />
                        <meta name="viewport" content="width=device-width, initial-scale=1.0" />
                        <meta http-equiv="X-UA-Compatible" content="ie=edge" />
                        <title>Static Template</title>
                        <link
                        href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap"
                        rel="stylesheet"
                        />
                    </head>
                    <body
                        style="margin: 0; font-family: 'Poppins', sans-serif; background: #ffffff; font-size: 14px;">
                        <div style="max-width: 680px; margin: 0 auto; padding: 45px 30px 60px; background: #f4f7ff; background-image: url(https://archisketch-resources.s3.ap-northeast-2.amazonaws.com/vrstyler/1661497957196_595865/email-template-background-banner); background-repeat: no-repeat; background-size: 800px 452px; background-position: top center; font-size: 14px; color: #434343;">
                        <header>
                            <table style="width: 100%;">
                            <tbody>
                                <tr style="height: 0;">
                                <td>
                                    <img src="https://upload.wikimedia.org/wikipedia/en/thumb/4/49/Anna_University_Logo.svg/330px-Anna_University_Logo.svg.png" height="100px"/>
                                    <h2 style="color: white;">
                                    Anna University Regional Campus - Tirunelveli
                                    </h2>
                                </td>
                                <td style="text-align: right;">
                                    <span style="font-size: 16px; line-height: 30px; color: #ffffff;">
                    """
    html_content_2 = """
                                    </span>
                                </td>
                                </tr>
                            </tbody>
                            </table>
                        </header>
                        <main>
                            <div style=" margin: 0; margin-top: 70px; padding: 92px 30px 115px; background: #ffffff; border-radius: 30px; text-align: center;">
                            <div style="width: 100%; max-width: 489px; margin: 0 auto;">
                                <h1 style=" margin: 0; font-size: 24px; font-weight: 500; color: #1f1f1f;">
                                Your OTP
                                </h1>
                                <p style=" margin: 0; margin-top: 17px; font-size: 16px; font-weight: 500;">
                                Hey """

    html_content_3 = """,
                </p>
                <p style=" margin: 0;  margin-top: 17px; font-weight: 500; letter-spacing: 0.56px;">
                Use the following OTP to complete the procedure to change your
                Password for Faculty Login. OTP is valid for
                <span style="font-weight: 600; color: #1f1f1f;">5 minutes</span>.
                Do not share this code with others.
                </p>
                <p style=" margin: 0; margin-top: 60px; font-size: 40px; font-weight: 600; letter-spacing: 15px; color: #ba3d4f;">
                """
    html_content_4 = """</p>
            </div>
            </div>
        </main>
        </div>
    </body>
    </html>"""

    html_content = html_content_1 + date + html_content_2 + name + html_content_3 + otp + html_content_4

    # Create a multipart message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = subject

    # Attach HTML content to the email
    html_part = MIMEText(html_content, "html")
    message.attach(html_part)

    try:
        # Connect to the SMTP server
        with smtplib.SMTP("smtp.mail.yahoo.com", 587) as server:
            server.starttls()
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            return True

    except Exception as e:
        return False


@app.route("/otpr", methods=["POST"])
def otpr():
    return render_template('one_time_password.html', otpf="")


@app.route("/otp", methods=["POST"])
def otp():
    formotp = request.form['combinedValue']
    sendotp = session.get('otp')
    if sendotp == formotp:
        session.pop('otp', None)
        return render_template('newpassword.html')
    else:
        return render_template('one_time_password.html', otpf="false")


@app.route("/newpass", methods=["POST"])
def newpass():
    passwd = request.form['password-2']
    emaill = session.get('email_forgot')
    hashed_password = hashlib.sha256(passwd.encode()).hexdigest()
    update_password(emaill, hashed_password)
    session.pop('email_forgot', None)
    return render_template('newpassword.html', succ=True)


def update_password(email_to_search, new_password):
    cursor.execute("UPDATE user_login SET password = %s WHERE mail_id = %s", (new_password, email_to_search))


@app.route('/auth-success')
def auth_success():
    session_key = session.get('session_key')
    cursor.execute("SELECT role FROM user_login WHERE session_key = %s", (session_key,))
    session['role'] = cursor.fetchone()[0]
    print(session['role'])
    if session['role'] == 4:  # admin
        return redirect('/dashboard')
    else:
        return "You are not authorized to access this page"


# Ended Sharon Work


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
