from flask import Flask, request, render_template, redirect, url_for, flash
import os
app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = 'E:\\My Drive\\Lave'
app.config['ALLOWED_EXTENSIONS'] = {'pdf', 'docx'} 

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

@app.route("/documents/upload/<dep>/<id>/<mid>", methods=['GET', 'POST'])
def upload(id, mid, dep):
    upload_s = None
    if request.method == 'POST':
        upload_folder = os.path.join(app.config['UPLOAD_FOLDER'], dep, id, mid)
        os.makedirs(upload_folder, exist_ok=True)
        script = "<script>alert('Hello, world!');</script>"
        

        leave_form = request.files['leave_form']
        medical_certificate = request.files['medical_certificate']

        if leave_form and allowed_file(leave_form.filename) and medical_certificate and allowed_file(medical_certificate.filename):
            leave_form.save(os.path.join(upload_folder, 'leave_form.pdf'))
            medical_certificate.save(os.path.join(upload_folder, 'medical_certificate.pdf'))

            additional_files = []
            file_names = []
            

            for field_name in request.files:
                if field_name.startswith('additional_file_'):
                    file = request.files[field_name]
                    if allowed_file(file.filename):
                        additional_files.append(file)
                        file_index = int(field_name.split('_')[-1])
                        file_name = request.form.get(f'file_name_{file_index}')
                        file_names.append(file_name if file_name else f'additional_file_{file_index}.pdf')
                        
                    else:
                        flash('Invalid file format: ' + file.filename, 'error')

            for index, file in enumerate(additional_files):
                file_name = file_names[index]
                file.save(os.path.join(upload_folder, file_name))
                
            upload_s = True
            return render_template('upload_document.html', script=script, successful_upload=upload_s)

        else:
            flash('Invalid file format', 'error')

    return render_template('upload_document.html')

if __name__ == '__main__':
    app.secret_key = 'your_secret_key'
    app.run(debug=True)
