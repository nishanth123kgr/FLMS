from flask import Flask, render_template, request, redirect
from from_csv.el_from_csv import get_el
from from_csv.ml_mtl_lop_from_csv import get_ml_mtl_lop
from from_csv.getInfo import get_info
import mysql.connector

app = Flask(__name__)

db = mysql.connector.connect(host="localhost", port="3306", user="root", database="facultyleavedb")
cursor = db.cursor()


# def insert_el():
#


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
                # Update the ML table
                # for i in range(len(ml)):
                #     row = ml[i]
                #     try:
                #         cursor.execute(
                #             'INSERT INTO ml (id, dept, `from`, `to`, total) VALUES (%s, "%s", "%s", "%s", %s)' %
                #             (info["id"], info["department"], row[0], row[1], row[2]))
                #         db.commit()
                #         cursor.reset()
                #     except Exception as e:
                #         return str(e) + " <a href='/'>Go back</a>"
            return redirect("/")
        return "No file uploaded"


@app.route("/el/<id>")
def display_el(id):
    cursor.execute("select * from el where id = %s", (id,))
    result = cursor.fetchall()
    cursor.reset()
    return render_template("el.html", table_content=enumerate(result),
                           table_head=["Si.No", "ID", "Department", "From", "To", "Prefix", "Suffix",
                                       "With permission on",
                                       "Date of join", "Total", "Document"])


if __name__ == "__main__":
    app.run(debug=True)
