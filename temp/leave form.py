from flask import Flask, request, render_template
import os

app = Flask(__name__)
@app.route('/')
def index():
    return 'hello world'


@app.route("/documents/upload/<id>/<mid>",methods=['GET', 'POST'])
def upload(id, mid):
    if request.method == 'POST':
        UPLOAD_FOLDER = "/documents/"+id+"/"+mid
        leave_form = request.files['leave_form']
        medical_certificate = request.files['medical_certificate']

        # Save the first two files with default names
        leave_form.save(os.path.join(app.config['UPLOAD_FOLDER'], 'leave_form.pdf'))
        medical_certificate.save(os.path.join(app.config['UPLOAD_FOLDER'], 'medical_certificate.pdf'))

        # Save additional files with custom names
        additional_files = request.files.getlist('additional_file')
        for index, file in enumerate(additional_files):
            file_name = request.form.get(f'file_name_{index}')
            if file_name:
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], file_name))
            else:
                # Handle cases where the custom name is not provided
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], f'additional_file_{index}.pdf'))

        return 'Files uploaded successfully'

    return 'Sucessfully uploaded'

if __name__ == '__main__':
    app.run(debug=True)