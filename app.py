from flask import Flask, render_template, request, redirect
from from_csv.el_from_csv import get_el
from from_csv.ml_mtl_lop_from_csv import get_ml_mtl_lop
from from_csv.getInfo import get_info
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(host="localhost", port="3306", user="root", database="facultyleavedb")
cursor = db.cursor()


@app.route("/")
def display_staff():
    cursor.execute("select * from staff")
    result = cursor.fetchall()
    cursor.reset()
    return render_template("index.html", table_content=enumerate(result))


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "GET":
        return render_template("upload.html")
    elif request.method == "POST":
        uploaded_file = request.files["file"]
        if uploaded_file:
            # Save the uploaded file to a desired location
            el = get_el(uploaded_file)
            ml, mtl, lop = get_ml_mtl_lop(uploaded_file)
            info = get_info(uploaded_file)
            cursor.execute("select * from staff where id = %s", (info["id"],))
            result = cursor.fetchall()
            cursor.reset()
            if not result:
                try:
                    cursor.execute('INSERT INTO staff VALUES (%s, "%s", "%s", "%s")' %
                                   (info["id"], info["name"], info["department"], str(info["doj"].date())))
                    db.commit()
                    cursor.reset()
                except Exception as e:
                    return str(e) + " <a href='/'>Go back</a>"

            else:
                # Update the EL table
                for i in range(len(el) - 1):
                    row = el[i]
                    try:
                        cursor.execute(
                            'INSERT INTO el (id, dept, `from`, `to`, with_permission_on, date_of_rejoin, total) VALUES (%s, "%s", "%s", "%s", %s, %s, %s)' %
                            (info["id"], info["department"], row[0], row[1],
                             row[2] if row[2] == 'NULL' else '\'["' + row[2] + '"]\'',
                             row[3] if row[3] == 'NULL' else '"' + row[3] + '"', row[4]))
                        db.commit()
                        cursor.reset()
                    except Exception as e:
                        return str(e) + " <a href='/'>Go back</a>"
                # Update the ML, MTL, LOP table
                for name, table in [('ml', ml), ('mtl', mtl), ('lop', lop)]:
                    if table:
                        for i in range(len(table)):
                            row = table[i]
                            try:
                                cursor.execute(
                                    'INSERT INTO %s (id, dept, `from`, `to`, medical_fittness_on, with_permission_on, doj,total) VALUES (%s, "%s", "%s", "%s",%s, %s, "%s", %s)' %
                                    (name, info["id"], info["department"], row[0], row[1],
                                     row[3] if row[3] == 'NULL' else '\'["' + row[3] + '"]\'',
                                     row[4] if row[4] == 'NULL' else '\'["' + row[4] + '"]\'', row[5], row[2]))
                                db.commit()
                                cursor.reset()
                            except Exception as e:
                                return str(e) + " <a href='/'>Go back</a>"
            return redirect("/")
        return "No file uploaded"


@app.route("/el/<id>")
def display_el(id):
    cursor.execute("select * from el where id = %s", (id,))
    result = cursor.fetchall()
    for i in result:

        del i[0]
        del i[-1]
    cursor.reset()
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Earned Leave (EL)", len=len(result))


@app.route("/ml/<id>")
def display_ml(id):
    cursor.execute("select * from ml where id = %s", (id,))
    result = cursor.fetchall()
    cursor.reset()
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "Medical fitness on",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Medical Leave (ML)", len=len(result))


@app.route("/mtl/<id>")
def display_mtl(id):
    cursor.execute("select * from mtl where id = %s", (id,))
    result = cursor.fetchall()
    cursor.reset()
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "Medical fitness on",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Maternal Leave (MTL)", len=len(result))


@app.route("/lop/<id>")
def display_lop(id):
    cursor.execute("select * from lop where id = %s", (id,))
    result = cursor.fetchall()
    cursor.reset()
    print(result)
    return render_template("table.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "Medical fitness on",
                                       "With permission on",
                                       "Date of join", "Total", "Document"], type="Loss Of Pay (LOP)", len=len(result))


@app.route("/upload_document/<id>/<type>/<int:si_no>", methods=["GET", "POST"])
def upload_document(id, type, si_no):
    if request.method == "POST":
        file = request.files["file"]
        if file:
            file.save("static/%s/%s/%s" % (id, si_no, file.filename))
            return "File uploaded successfully"
        return "No file uploaded"
    return render_template("upload_document.html", id=id, type=type, si_no=si_no)

if __name__ == "__main__":
    app.run(debug=True)
