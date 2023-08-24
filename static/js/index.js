var id = 0;

function addMoreFiles() {
    id++;
    var newRow = document.createElement('div');
    newRow.className = 'row class-15';
    newRow.id = id;

    newRow.innerHTML = `
        <div class="col justify-content-center class-16">
            <input class="form-control justify-content-start" placeholder="Enter name (with extension)" type="text" name="file_name_${id}">
        </div>
        <div class="col justify-content-start class-17">
            <input class="form-control class-18" type="file" name="additional_file_${id}">
            <button class="btn btn-primary class-21" onclick="removeMoreFiles('${id}');" type="button">
                <i class="fas fa-trash-alt text-danger"></i>
            </button>
        </div>
    `;

    document.getElementById('table').appendChild(newRow);
}

function removeMoreFiles(id) {
    document.getElementById('table').removeChild(document.getElementById(id));
}
