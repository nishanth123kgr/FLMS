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
    return search(id);
}

idInput.addEventListener('input', async () => {
        if (idInput.value.length === 5) {
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
    }
)


function uploadExcel() {
    let file = document.getElementById("excel_file").files[0];
    let formData = new FormData();
    formData.append("file", file);
    formData.append("info", JSON.stringify({
        "id": idInput.value,
        "name": name.value,
        "department": department.value,
        "doj": doj.value,
        "sheetName": document.getElementById("sheetName").value
    }))
    fetch("/staff/upload", {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            response.json().then(data => {
                if (data["error"])
                    alert(data["error"])
                else
                    alert("File uploaded successfully");
            })
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
    if (id.length === 5) {
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
            if (jsonData.length !== 0) {
                console.log(jsonData)
                let tableHead = ["Si.No", "ID", "Name", "Department", "Leave Type", "From", "To",
                    "Prefix From", "Prefix To", "Suffix From", "Suffix To", "Date of Joining", "Total", "Document"]
                let is_ML_MTL_LOP = false;
                switch (leaveType.value) {
                    case "ML":
                    case "MTL":
                    case "LOP":
                        tableHead = [...tableHead.slice(0, 11), "Medical Fitness on", ...tableHead.slice(11)]
                        is_ML_MTL_LOP = true;
                        break;
                    default:
                        break;
                }
                document.getElementById("table-head-upload").innerHTML = `<tr>${tableHead.map((item) => `<th>${item}</th>`).join("")}</tr>`
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
                            <td>${item[5] === null ? "Nil" : item[5]}</td>
                            <td>${item[6] === null ? "Nil" : item[6]}</td>
                            <td>${item[7] === null ? "Nil" : item[7]}</td>
                            <td>${item[8] === null ? "Nil" : item[8]}</td>
                            <td>${item[9]}</td>
                            <td>${item[10]}</td>
                            ${is_ML_MTL_LOP ? `<td>${item[11]}</td>` : ""}
                            <td><button onclick="showModal(this)">Upload</button></td>
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


// Handling Excel Upload for Staff, Get Sheet names
async function getSheetNames(fileInput, selectID) {
    let file = fileInput.files[0];
    let formData = new FormData();
    formData.append("file", file);
    await fetch("/staff/get_sheet_names", {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            response.json().then((data) => {
                console.log(data)
                data = data['sheet_names'];
                let select = document.getElementById(selectID);
                select.innerHTML = "";
                data.forEach((item) => {
                    select.innerHTML += `<option value="${item}">${item}</option>`
                })
            })
        } else {
            alert("Error uploading file");
        }
    })
}

leaveUploadID = document.getElementById('idElem')
leaveUploadID.addEventListener('input', async () => {
    if (leaveUploadID.value.length === 5) {
        let dataItem = getStaffData(leaveUploadID.value)
        dataItem.then(result => {
            if (result) {
                let nameElement = document.getElementById("nameElem");
                let deptElement = document.getElementById("depElem");
                console.log(result);
                nameElement.value = result[0][0];
                deptElement.value = result[0][1];
            } else {
                console.log("No such staff exists");
            }
        })

    }
})

// VL Upload
// Getting Data with ID
let vlUploadID = document.getElementById('vl_id')
vlUploadID.addEventListener('input', async () => {
        if (vlUploadID.value.length === 5) {
            let dataItem = getStaffData(vlUploadID.value)
            dataItem.then(result => {
                if (dataItem) {
                    console.log(result);

                    document.getElementById("vl_name").value = result[0][0];
                    document.getElementById("vl_dept").value = result[0][1];
                    document.getElementById("vl_doj").value = new Date(result[0][2]).toISOString().split('T')[0].split('-').reverse().join('-');

                } else {
                    console.log("No such staff exists");
                }
            })

        }
    }
)

// Upload VL
function uploadVL() {
    let file = document.getElementById("vl_file_input").files[0];
    let formData = new FormData();
    formData.append("file", file);

    let vl_id = vlUploadID.value
    let vl_sheet_name = document.getElementById("vl_sheet_name").value
    console.log(`/upload_vl/${vl_id}/${vl_sheet_name}`)
    console.log(formData)
    fetch(`/upload_vl/${vl_id}/${vl_sheet_name}`, {
        method: "POST",
        body: formData
    }).then(response => {
        if (response.ok) {
            response.json().then(data => {
                if (data["error"])
                    alert(data["error"])
                else
                    console.log(data["data"]);
                renderVLTable(data["data"]);

            })
        } else {
            alert("Error uploading file");
        }
    })
}

function getTotalDays(fromDate, toDate) {
    if (fromDate === null || toDate === null || fromDate === "NULL" || toDate === "NULL") {
        return 0;
    }
    const dateParts1 = fromDate.split('-');
    const dateParts2 = toDate.split('-');

// Create Date objects with the parsed parts
    const date1 = new Date(`${dateParts1[2]}-${dateParts1[1]}-${dateParts1[0]}`);
    const date2 = new Date(`${dateParts2[2]}-${dateParts2[1]}-${dateParts2[0]}`);

// Calculate the time difference in milliseconds
    const timeDifference = date2 - date1;

// Calculate the number of days
    const daysDifference = Math.floor(timeDifference / (1000 * 60 * 60 * 24));
    return daysDifference + 1

}

// Render VL Table
function renderVLTable(data) {
    sessionStorage.setItem("vlData", JSON.stringify(data));
    let vlTable = document.getElementById("vlTable");
    vlTable.parentElement.style.display = "flex";
    let vlHead = ["Si.No", "VL ID", "From", "To", "Total", "Availed From", "Availed To", "Total", "Prevented From", "Prevented To", "Total"]
    vlTable.getElementsByTagName("thead")[0].innerHTML = `<tr>${vlHead.map((item) => `<th>${item}</th>`).join("")}</tr>`
    let tbody = ""
    let sino = 0;
    for (const item in data) {
        let availed_from = ''
        let availed_to = ''
        let prevented_from = ''
        let prevented_to = ''
        let availed_total = ''
        let prevented_total = ''
        for (let i = 0; i < data[item]['Availed_from'].length; i++) {
            availed_from += `<div>${data[item]['Availed_from'][i] === 'NULL'?'-':data[item]['Availed_from'][i]}</div>`
            availed_to += `<div>${data[item]['Availed_to'][i] === 'NULL'?'-':data[item]['Availed_to'][i]}</div>`
            availed_total += `<div>${getTotalDays(data[item]['Availed_from'][i], data[item]['Availed_to'][i])}</div>`
        }
        for (let i = 0; i < data[item]['Prevented'].length; i++) {
            prevented_from += `<div>${data[item]['Prevented'][i][0]}</div>`
            prevented_to += `<div>${data[item]['Prevented'][i][1]}</div>`
            prevented_total += `<div>${getTotalDays(data[item]['Prevented'][i][0], data[item]['Prevented'][i][1])}</div>`
        }
        tbody += `<tr>
        <td>${++sino}</td>
        <td>${item}</td>
        <td>${data[item]['from'][0] === null ? "-" : data[item]['from'][0]}</td>
        <td>${data[item]['to'][0] === null ? "-" : data[item]['to'][0]}</td>
        <td>${getTotalDays(data[item]['from'][0], data[item]['to'][0])}</td>
        <td style="padding: 0">${availed_from}</td>
        <td style="padding: 0">${availed_to}</td>
        <td style="padding: 0">${availed_total}</td>
        <td style="padding: 0">${prevented_from?prevented_from:'-'}</td>
        <td style="padding: 0">${prevented_to?prevented_to:'-'}</td>
        <td style="padding: 0">${prevented_total?prevented_total:'0'}</td>
        </tr>`
    }
    vlTable.getElementsByTagName("tbody")[0].innerHTML = tbody;
}

// Update VL DB
function updateVLDB() {
    let data = sessionStorage.getItem("vlData");
    let staff_id = document.getElementById("vl_id").value
    if(!staff_id){
        alert("Please enter staff ID")
        return
    }
    if (data) {
        fetch(`/update_vl/${staff_id}`, {
            method: "POST",
            body: data
        }).then(response => {
            if (response.ok) {
                response.json().then(data => {
                    if (data["error"])
                        alert(data["error"])
                    else
                        alert("File uploaded successfully");
                })
            } else {
                alert("Error uploading file");
            }
        })
    } else {
        alert("No data to update");
    }
}

// Report Generation
function generateReport() {
    let staff_id = document.getElementById("reportInput").value
    if(!staff_id){
        alert("Please enter staff ID")
        return
    }
    fetch(`/generate_report/${staff_id}`, {
  method: "GET"
})
  .then(response => {
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    return response.blob(); // Get the file data as a blob
  })
  .then(blob => {
    // Create a URL for the blob data
    const blobUrl = window.URL.createObjectURL(blob);

    // Create a temporary anchor element
    const link = document.createElement('a');
    link.style.display = 'none';
    document.body.appendChild(link);

    // Set the href attribute of the anchor element to the blob URL
    link.href = blobUrl;

    // Specify the filename for the downloaded file (optional)
    link.download = `${staff_id}_el.xlsx`;

    // Trigger a click event on the anchor element to initiate the download
    link.click();

    // Clean up by revoking the blob URL and removing the anchor element
    window.URL.revokeObjectURL(blobUrl);
    document.body.removeChild(link);
  })
  .catch(error => {
    console.error('Error downloading the file:', error);
  });
}
