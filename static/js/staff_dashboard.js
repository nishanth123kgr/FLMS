let staff_id = document.getElementById('staff_data').getAttribute('data-id')
let staff_name = document.getElementById('staff_data').getAttribute('data-name')
let staff_dept = document.getElementById('staff_data').getAttribute('data-dept')

let leaveType = document.getElementById('leave_type')

function render_leave_details(jsonData) {
    if (jsonData.length !== 0) {
        console.log(jsonData)
        let tableHead = ["Si.No", "ID", "Name", "Department", "Leave Type", "From", "To",
            "Prefix From", "Prefix To", "Suffix From", "Suffix To", "Date of Joining", "Total", "Document"]
        let is_ML_MTL_LOP = false;
        switch (leaveType.value.toUpperCase()) {
            case "ML":
            case "MTL":
            case "LOP":
                tableHead = [...tableHead.slice(0, 11), "Medical Fitness on", ...tableHead.slice(11)]
                console.log(tableHead)
                is_ML_MTL_LOP = true;
                break;
            default:
                break;
        }
        document.getElementById("table-head-upload").innerHTML = `<tr>${tableHead.map((item) => `<th>${item}</th>`).join("")}</tr>`
        let tbody = ""
        jsonData.forEach((item, i) => {
            let filePath = `${staff_dept}_${item[1]}_${leaveType.value}_${item[0]}`
            tbody += `<tr data-lid="${item[0]}">
                      <td>${i + 1}</td>  
                            <td>${item[1]}</td>
                            <td>${staff_name}</td>
                            <td>${staff_dept}</td>
                            <td>${leaveType.value.toUpperCase()}</td>
                            <td>${item[3]}</td>
                            <td>${item[4]}</td>
                            <td>${item[5] === null ? "Nil" : item[5]}</td>
                            <td>${item[6] === null ? "Nil" : item[6]}</td>
                            <td>${item[7] === null ? "Nil" : item[7]}</td>
                            <td>${item[8] === null ? "Nil" : item[8]}</td>
                            <td>${item[9]}</td>
                            <td>${item[10]}</td>
                            ${is_ML_MTL_LOP ? `<td>${item[11]}</td>` : ""}
                            <td><button id="show-files-button" onclick="getFiles(\'${filePath}\', this)">View</button></td>
                            </tr>`
        }
        )
        document.getElementById("leaveTable").getElementsByTagName("tbody")[0].innerHTML = tbody;
        document.getElementById("leaveTable").style.display = "table";
        document.querySelector(".no-data").style.display = "none";
    } else {

        document.getElementById("leaveTable").style.display = "none";
        document.querySelector(".no-data").style.display = "flex";

    }
}

leaveType.addEventListener("change", () => {
    if (leaveType.value && staff_id) {
        let data = getLeaveDetails(staff_id, leaveType.value);
        data.then((jsonData) => {
            render_leave_details(jsonData)
        })
    }
})

function format_date(date) {
    console.log(date)
    let dateComponents = date.split('-');
    return dateComponents[2] + '-' + dateComponents[1] + '-' + dateComponents[0]
}

function applyDateFilter() {
    let leave_filter_start_date = document.getElementById("leave_date_start_filter").value
    let leave_filter_end_date = document.getElementById("leave_date_end_filter").value
    if (!leave_filter_end_date) {
        alert("Select valid start date and try again!")
        return
    } else if (!leave_filter_start_date) {
        alert("Select valid end date and try again!")
        return
    } else if (!leaveType.value) {
        alert("Select valid leave type and try again!")
        return
    }
    let formData = new FormData()
    formData.set('start', format_date(leave_filter_start_date))
    formData.set('end', format_date(leave_filter_end_date))
    formData.set('id', staff_id)
    console.log(formData)
    let response = fetch('/get_leave_with_date/', {
        method: 'post',
        body: formData
    })
    response.then(data => {
        data.json().then(data => {
            render_leave_details(data)
        })
    })
}

function getFiles(path, element) {
    let formData = new FormData();
    formData.set('path', path)
    fetch('/get_files/', {
        method: 'post',
        body: formData
    })
        .then(response => response.json())
        .then(data => {
            console.log(data);
            let fileContainer = document.querySelector('#myModal .modal-content .file-container')
            fileContainer.innerHTML = '';
            path = path.replace(/_/g, '/');
            console.log(path);
            data.files.forEach(file => {
                let fileElement = document.createElement('a');
                fileElement.classList.add('file', 'flex', 'flex-col', 'items-center');
                fileElement.setAttribute('href', `/get_files/${path}/${file}`);
                fileElement.setAttribute('target', '_blank');
                fileElement.style.width = '120px';
                fileElement.style.wordWrap = 'break-word';
                let imgElement = document.createElement('img');
                imgElement.setAttribute('src', '../static/images/pdf.png');
                imgElement.setAttribute('alt', '');
                imgElement.setAttribute('width', '100px');
                imgElement.setAttribute('height', '100px');

                fileElement.appendChild(imgElement);

                fileElement.innerHTML += file;
                fileContainer.appendChild(fileElement);
            });
        });
    showModal(element);
}

function showModal(element) {
    document.getElementById("myModal").style.display = "block";
    console.log(element);
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


async function get_el_earned() {
    let formData = new FormData()
    formData.set('id', staff_id)
    let el_earned_data = await fetch('/get_el_earned/', {
        method: "POST",
        body: formData
    })
    el_earned_data.json().then(data => {
        console.log(data);
        render_el_details(data, 'before')
        render_el_details(data, 'after')
    })
}

function render_el_details(data, type) {
    let tableHead = ["Semester", "Total Working Days", "Total Leave Availed", "EL Availed", "VL Prevented", "EL Credited", "Total"]
    document.querySelector(`#table-head-el-${type[0]}`).innerHTML = `<tr>${tableHead.map((item) => `<th>${item}</th>`).join("")}</tr>`
    let tbody = ''
    for (let i in data[type]) {
        let sem = `20${data[type][i]['sem'].split('_')[0]} ${data[type][i]['sem'].split('_')[1] == 'o' ? 'Odd' : 'Even'}`
        tbody += `<tr>
            <td>${sem}</td>
            <td>${data[type][i]['total_working_days']}</td>
            <td>${data[type][i]['leave_availed']}</td>
            <td>${data[type][i]['el_availed']}</td>
            <td>${data[type][i]['vl_prevented_total']}</td>
            <td>${data[type][i]['final_total']}</td>
            <td>${data[type][i]['sum_total']}</td>
            </tr>`
    }
    document.getElementById(`el_earned_${type}_table`).getElementsByTagName("tbody")[0].innerHTML = tbody
}

get_el_earned()
function setIframeHeight() {
    const iframe = document.querySelector('iframe');
    if (iframe) {
        iframe.style.height = iframe.contentWindow.document.body.scrollHeight + 'px';
    }
}

// Adjust iframe height when the content is loaded
window.onload = setIframeHeight;

// Adjust iframe height when the content inside the iframe changes
window.addEventListener('resize', setIframeHeight);
