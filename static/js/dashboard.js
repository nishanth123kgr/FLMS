function changeContent(element) {
    toggleActive(element);
    let activeSection = document.querySelector(".un-hide");
    let section = document.getElementById(element.innerText.toLowerCase().replace(/\s/g, '-'));
    if (section) {
        activeSection.classList.replace("un-hide", "hide");
        console.log(section, element.innerText.toLowerCase().replace(/\s/g, '-'))
        section.classList.replace("hide", "un-hide");
    }
}

function toggleActive(element) {
    var active = document.getElementsByClassName("active");
    active[0].className = active[0].className.replace(" active", "");
    element.className += " active";
}

let idInput = document.getElementById("id");
let name = document.getElementById("name");
let department = document.getElementById("dept");
let doj = document.getElementById("doj");

async function search(id) {
    const data = id;
    if (data.length === 5) {
        const response = await fetch(`/staff/${data}`, {
            method: 'POST',
        });
        return await response.json()
    }
}

function getStaffData(id) {
    let data = search(id);
    data.then((jsonData) => {
        if (jsonData[0]) {
            let nameElement = document.getElementById("nameElem");
            let deptElement = document.getElementById("depElem");
            let dataItem = jsonData[0]
            console.log(dataItem);
            nameElement.value = dataItem[0];
            deptElement.value = dataItem[1];
        } else {
            alert("No such staff exists");
        }
    })
}

idInput.addEventListener('input', async () => {
        let data = search(idInput.value);
        data.then((jsonData) => {
            if (jsonData[0]) {
                let dataItem = jsonData[0]
                console.log(dataItem);
                name.value = dataItem[0];
                department.value = dataItem[1];
                doj.value = new Date(dataItem[2]).toISOString().split('T')[0].split('-').reverse().join('-');
            } else {
                name.value = "";
                department.value = "";
                doj.value = "";
                alert("No such staff exists");
            }
        })
    }
)


function uploadExcel() {
    let file = document.getElementById("file").files[0];
    let formData = new FormData();
    formData.append("file", file);
    formData.append("info", JSON.stringify({
        "id": idInput.value,
        "name": name.value,
        "department": department.value,
        "doj": doj.value
    }))
    fetch("/staff/upload", {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            alert("File uploaded successfully");
        } else {
            alert("Error uploading file");
        }
    })
}

async function uploadLeaveFiles(element) {
    let postUrl = element.getAttribute("data-post")
    if (postUrl) {
        print(postUrl)
        let formData = new FormData();
        let files = document.querySelectorAll(".modal-content input[type=file]");
        console.log(files)
        let fileNames = document.querySelectorAll("label");
        console.log(fileNames)
        files.forEach((file, i) => {
            formData.append(`files`, file.files[0]);
            formData.append(`fileNames`, fileNames[i].innerText.toLowerCase().replace(/\s/g, '-'))
        })
        console.log(formData.keys())
        await fetch(postUrl, {
            method: "POST",
            body: formData
        }).then(response => {
            if (response.ok) {
                alert("File uploaded successfully");
            } else {
                alert("Error uploading file");
            }
        })
    }
    i = 0;
}

async function getLeaveDetails(id, type) {
    if (id.length === 6) {
        console.log(`/${type.toLowerCase()}/${id}`)
        const response = await fetch(`/${type.toLowerCase()}/${id}`, {
            method: 'POST',
        })
        return await response.json()
    }
}

let leaveType = document.getElementById("leaveType")
let idElement = document.getElementById("idElem")
let deptElement = document.getElementById("depElem")
let nameElement = document.getElementById("nameElem")

leaveType.addEventListener("change", () => {
    if (leaveType.value && idElement.value && deptElement.value) {
        let data = getLeaveDetails(idElement.value, leaveType.value);
        data.then((jsonData) => {
            if (jsonData) {
                console.log(jsonData)
                let tbody = ""
                jsonData.forEach((item, i) => {
                        tbody += `<tr data-lid="${item[0]}">
                            <td>${i + 1}</td>  
                            <td>${item[1]}</td>
                            <td>${nameElement.value}</td>
                            <td>${deptElement.value}</td>
                            <td>${leaveType.value}</td>
                            <td>${item[3]}</td>
                            <td>${item[4]}</td>
                            <td><button onclick="showModal(this)">Upload</button></td>
                            </tr>`
                    }
                )
                document.getElementById("leaveTable").getElementsByTagName("tbody")[0].innerHTML = tbody;
            } else {
                alert("No data exists");
            }
        })
    }
})

function showModal(element) {
    document.getElementById("myModal").style.display = "block";
    let tr = element.parentElement.parentElement;
    let id = tr.getElementsByTagName("td")[1].innerText;
    let type = tr.getElementsByTagName("td")[4].innerText;
    let dept = tr.getElementsByTagName("td")[3].innerText;
    let l_id = tr.getAttribute("data-lid");
    document.getElementById("fileSubmitButton").setAttribute("data-post", `/upload_document/${dept}/${id}/${type.toLowerCase()}/${l_id}`)
}

document.addEventListener("DOMContentLoaded", function () {
    const modal = document.getElementById("myModal");
    const openModalBtns = document.querySelectorAll(".uploadButton");
    console.log(openModalBtns)
    const closeModalSpan = document.querySelector(".close");

    openModalBtns.forEach(function (btn) {
        btn.onclick = function () {
            modal.style.display = "block";
        }
    });

    closeModalSpan.addEventListener("click", function () {
        modal.style.display = "none";
    });

    window.addEventListener("click", function (event) {
        if (event.target === modal) {
            modal.style.display = "none";
        }
    });
});

let i = 0;

function addMoreFile() {
    let inputs = document.getElementById("inputs");
    inputs.innerHTML += `
    <div class="block" id="row_${i}">
        <label class="block mb-2 font-medium text-gray-900 dark:text-white"
            for="file_input" contenteditable="true" id="filename_${i}">New Document ${i + 1}</label>
        <div class="flex items-center mb-2">
        <input class="block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 dark:text-gray-400 focus:outline-none dark:bg-gray-700 dark:border-gray-600 dark:placeholder-gray-400"
                name="file_${i}"
                id="file_${i}" type="file">
                <i class="fa-solid fa-trash ml-2 fa-lg text-red-400 cursor-pointer" onclick="removeFile(this.parentElement.parentElement.id)"></i>
        </div>
    </div>`
    i++;
}

function removeFile(id) {
    document.getElementById(id).remove();
}