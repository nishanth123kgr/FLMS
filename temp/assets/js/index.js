    var id = 0;
function addMoreFiles() {
    document.getElementById('table').innerHTML += ` <div class="row class-15" id="${id}">
<div class="col justify-content-center class-16"><input
        class="form-control justify-content-start" placeholder="Enter name (with extention)" type="text" /></div>
<div class="col justify-content-start class-17"><input class="form-control class-18"
        type="file" /><button class="btn btn-primary class-21" onclick="removeMoreFiles('${id}');"  type="button"><i class="fas fa-trash-alt text-danger"></i></button></div>
</div>`;
id += 1;

}

function removeMoreFiles(id) {
    document.getElementById('table').removeChild(document.getElementById(id));
}