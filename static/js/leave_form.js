let required_leave_from;
let required_leave_to;
let url;
let classes_count;
let html;
let staff_id;
let script;

leave_type = document.getElementById("leave_type");
leave_type.addEventListener('input', function(event) {
  var input = event.target.value;
  if (input == 'Medical Leave (ML)' || input == 'Earned Leave (EL)' || input == 'Special Casual Leave (SPCL)' || input == 'Restricted Holiday (RH)')
  {
    document.getElementById('goouttowndiv').style.display = 'none';
    document.getElementById('outoftowndiv').style.display = 'none';
    document.getElementById('prediv').style.display = '';
    document.getElementById('sufdiv').style.display = '';
    document.getElementById('leaveadddiv').style.display = '';
  }
  else if (input == 'Casual Leave (CL)')
  {
    document.getElementById('goouttowndiv').style.display = '';
    document.getElementById('outoftowndiv').style.display = '';
    document.getElementById('prediv').style.display = 'none';
    document.getElementById('sufdiv').style.display = 'none';
    document.getElementById('leaveadddiv').style.display = 'none';
  }
  
});

function formatDate(inputDate) 
{
    const dateParts = inputDate.split('-');
    const formattedDate = `${dateParts[2]}-${dateParts[1]}-${dateParts[0]}`;
    return formattedDate;
}

async function getStaffClasses(staff, fdate, tdate) {
    const apiUrl = `/api/get_staffs_classes/${staff}/${fdate}/${tdate}`;
    return fetch(apiUrl)
      .then(response => {
        if (!response.ok) {
          throw new Error(`HTTP error! Status: ${response.status}`);
        }
        return response.json();
      })
      .then(data => {
        return data;
      })
      .catch(error => {
        throw new Error('Fetch error:', error);
      });
  }
  
  
async function get_staff_id_from_name(name) {
    const url = `/api/get_staff_id_from_name/${name}`;
    const response = await fetch(url);
  
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
  
    const data = await response.json();
    if (Array.isArray(data) && data.length > 0) {
      return data[0]; // Return the first element of the array
    } else {
      throw new Error('Data is empty or not an array');
    }
  }
  
// Corrected getFreeStaffs function with proper initialization
async function getFreeStaffs(day, period, semester, department) {
  const apiUrl = `/api/get_free_staffs/${day}/${period}/${semester}/${department}`;
  try {
    const response = await fetch(apiUrl);
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }
    const data = await response.json();
    let processedData = ''; // Initialize processedData
    for (const item of data) {
      processedData += `<option value="${item[1]}">${item[0]}</option>`;
    }
    return processedData; // Return the processed data
  } catch (error) {
    console.error('Fetch error:', error); // Log the error
    return ''; // Return an empty string or handle the error as needed
  }
}

// // Corrected addclasses function with async keyword and html initialization
// async function addclasses(data) {
//   let html = ''; // Initialize html
//   let datalength = data.length;
//   for (let i = 0; i < datalength; i++) {
//     let dataa = data[i];
//     try {
//       let staffsfreee = await getFreeStaffs(dataa[0], dataa[2], dataa[4], dataa[5]);
//       html += `<tr>
//         <td style="border: 1px solid var(--bs-table-color);"><input class="form-control" type="text" value="${dataa[1]}" style="width: 125px;" readonly /></td>
//         <td style="border: 1px solid var(--bs-table-color);"><input class="form-control" type="text" value="${dataa[0]}" style="width: 75px;" readonly /></td>
//         <td style="border: 1px solid var(--bs-table-color);"><input class="form-control" type="text" value="${dataa[2]}" style="width: 60px;" readonly /></td>
//         <td style="border: 1px solid var(--bs-table-color);"><input class="form-control" type="text" value="${dataa[3]}" readonly /></td>
//         <td style="border: 1px solid var(--bs-table-color);"><input id="insub_${i}" class="form-control" type="text" style="width: 150px;" list="freedata_${i}" /></td>
//         <datalist id="freedata_${i}">${staffsfreee}</datalist>
//         <td style="border: 1px solid var(--bs-table-color);"><input list="subdata_${i}" class="form-control" type="text" style="width: 150px;" /></td>
//         <datalist id="subdata_${i}"></datalist>
//       </tr>`;
//       script += `var subject_${i} = document.getElementById('sub_${i}');
//       inpusubject_${i}tElement.addEventListener('input', function(event) {
//         var input_${i} = event.target.value;
//         ChangeSubjects('insub_${i}', '${dataa[5]}', 'subdata_${i}');
//     });`
//     } catch (error) {
//       console.error('Error fetching free staffs:', error);
//     }
//   }
//   var script = document.createElement('script');
//   script.innerHTML = script;
//   return html;
// }


// function ChangeSubjects(input, department, output)
// {
//   let inputt = document.getElementById(input).value;
//   let outputt = document.getElementById(output);
//   const apiurl = '/api/ChangeSubjects/'+ department +'/'+ inputt
//   fetch(apiurl)
//   .then (response => {
//     if (!response.ok) {
//       throw new Error(`HTTP error! Status: ${response.status}`);
//     }
//     return response.json();
//   })
//   .then(data =>{
//     for(let dat in data){
//       html += `<option value="${dat[0]}">${dat[1]}</option>`
//     }
//     outputt.innerHTML = scriptt;
//   })
// }

async function addclasses(data) {
  let html = ''; // Initialize html
  let script = ''; // Initialize script
  let datalength = data.length;
  for (let i = 0; i < datalength; i++) {
    let dataa = data[i];
    try {
      let staffsfreee = await getFreeStaffs(dataa[0], dataa[2], dataa[4], dataa[5]);
      html += `<tr>
      <td style="border: 1px solid var(--bs-table-color);"><input id="date_${i}" class="form-control" type="text" value="${dataa[1]}" style="width: 125px;" readonly /></td>
      <td style="border: 1px solid var(--bs-table-color);"><input id="day_${i}"class="form-control" type="text" value="${dataa[0]}" style="width: 75px;" readonly /></td>
      <td style="border: 1px solid var(--bs-table-color);"><input id="period_${i}" class="form-control" type="text" value="${dataa[2]}" style="width: 60px;" readonly /></td>
      <td style="border: 1px solid var(--bs-table-color);"><input id="subject_${i}" class="form-control" type="text" value="${dataa[3]}" readonly /></td>
      <td style="border: 1px solid var(--bs-table-color);"><input id="insub_${i}" class="form-control" type="text" style="width: 150px;" list="freedata_${i}" /></td>
      <datalist id="freedata_${i}">${staffsfreee}</datalist>
      <td style="border: 1px solid var(--bs-table-color);"><input id="outsub_${i}" list="subdata_${i}" class="form-control" type="text" style="width: 150px;" /></td>
      <datalist id="subdata_${i}"></datalist>
      </tr>`;
      script += `
      var subject_${i} = document.getElementById('insub_${i}');
      subject_${i}.addEventListener('input', function(event) {
        var input_${i} = event.target.value;
        ChangeSubjects('insub_${i}', '${dataa[5]}', 'subdata_${i}');
      });
      `
    } catch (error) {
      console.error('Error fetching free staffs:', error);
    }
  }
  var scriptElement = document.createElement('script');
  classbody = document.getElementById('clasbod');
  classbody.innerHTML = html;
  scriptElement.innerHTML = script;
  document.body.appendChild(scriptElement); // Append the script to the document body
}

function ChangeSubjects(input, department, output) {
  let inputt = document.getElementById(input).value;
  let outputt = document.getElementById(output);
  const apiurl = '/api/changeStaff/' + department + '/' + inputt;
  fetch(apiurl)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      let optionsHtml = ''; // Initialize optionsHtml
      for (let dat in data) {
        optionsHtml += `<option value="${data[dat][0]}">${data[dat][1]}</option>`;
      }
      outputt.innerHTML = optionsHtml; // Set the innerHTML of the output element
    })
    .catch(error => {
      console.error('Error fetching subjects:', error);
    });
}

  
async function setChanges() {
  required_leave_from = document.getElementsByName('reqfrom');
  required_leave_from = required_leave_from[0].value;
  required_leave_to = document.getElementsByName('reqto');
  required_leave_to = required_leave_to[0].value;
  staff_name = window.parent.window.parent.document.getElementById("staff_data").getAttribute("data-name");
  staff_id = window.parent.document.getElementById("staff_data").getAttribute("data-id");
  classes = await getStaffClasses(staff_id, formatDate(required_leave_from), formatDate(required_leave_to));
  classes_count = classes.length;
  addclasses(classes);
}

function printFormattedDate() {
  const today = new Date();
  const year = today.getFullYear();
  const month = today.getMonth() + 1;
  const day = today.getDate();
  const formattedYear = year.toString().padStart(4, '0');
  const formattedMonth = month.toString().padStart(2, '0');
  const formattedDay = day.toString().padStart(2, '0');
  const formattedDate = `${formattedDay}-${formattedMonth}-${formattedYear}`;
  return formattedDate;
}


async function generate() 
{
  const leave_type = document.getElementById('leave_type').value;
  if (leave_type == 'Medical Leave (ML)' || leave_type == 'Earned Leave (EL)' || leave_type == 'Special Casual Leave (SPCL)' || leave_type == 'Restricted Holiday (RH)')
  {
  const namee = window.parent.document.getElementById("staff_data").getAttribute("data-name");
  const desi = document.getElementById('designation').value;
  const department = document.getElementById('department').value;
  const reasonforleave = document.getElementById('reasonforleave').value;
  const reqfrom = document.getElementById('reqfrom').value;
  const reqto = document.getElementById('reqto').value;
  const prefrom = document.getElementById('prefrom').value;
  const preto = document.getElementById('preto').value;
  const suffrom = document.getElementById('suffrom').value;
  const sufto = document.getElementById('sufto').value;
  const leaveadd = document.getElementById('leaveadd').value;
  const notes = document.getElementById('notes').value;
  const today = printFormattedDate();
  const inputDataArray = [];
  const tableRows = document.querySelectorAll("#clasbod tr");
  
  tableRows.forEach(function (row) {
    const inputFields = row.querySelectorAll("input");
    const rowData = [];

    inputFields.forEach(function (input) {
      const fieldValue = input.value;
      rowData.push(fieldValue);
    });

    inputDataArray.push(rowData);
  });

  const leaves = inputDataArray.map((data, index) => {
    return [index + 1, data[0], `${data[3]} to ${data[5]}`, data[5], ''];
  });

  const dataToSend = {
    objectData: {
      name: namee,
      dest: desi,
      dep: department,
      type: leave_type,
      reason: reasonforleave,
      prefix: `From: ${prefrom} to: ${preto}`,
      date: `From: ${reqfrom} To: ${reqto}`,
      suffix: `From: ${suffrom} To: ${sufto}`,
      address: leaveadd,
      notes: notes,
      todte: today
    },
    leaves
  };
  await fetch('/api/generate/el', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(dataToSend)
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      console.log(data);
      download(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });
  }
  
  else if (leave_type == 'Casual Leave (CL)')
  {
  const namee = window.parent.document.getElementById("staff_data").getAttribute("data-name");
  const desi = document.getElementById('designation').value;
  const department = document.getElementById('department').value;
  const reasonforleave = document.getElementById('reasonforleave').value;
  const reqfrom = document.getElementById('reqfrom').value;
  const reqto = document.getElementById('reqto').value;
  const ingoouttown = document.getElementById('ingoouttown').value
  const inoutoftown = document.getElementById('inoutoftown').value
  const today = printFormattedDate();
  const inputDataArray = [];
  const tableRows = document.querySelectorAll("#clasbod tr");
  
  tableRows.forEach(function (row) {
    const inputFields = row.querySelectorAll("input");
    const rowData = [];

    inputFields.forEach(function (input) {
      const fieldValue = input.value;
      rowData.push(fieldValue);
    });

    inputDataArray.push(rowData);
  });

  const leaves = inputDataArray.map((data, index) => {
    return [index + 1, data[0], `${data[3]} to ${data[5]}`, data[5], ''];
  });

  const dataToSend = {
    objectData: {
      name: namee,
      department: `${desi} / ${department}`,
      type: leave_type,
      reason: reasonforleave,
      fromto: `From: ${reqfrom} To: ${reqto}`,
      address: leaveadd,
      yesno : ingoouttown,
      add : inoutoftown,
      fdate : reqfrom,
      tdate : reqto,
      date : today
    },
    leaves
  };
  await fetch('/api/generate/cl', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(dataToSend)
  })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      download(data);
    })
    .catch(error => {
      console.error('Error:', error);
    });

  }
  
}


function download(path)
{
  url = "/api/download/"+path;
  const newWindow = window.open(url, '_blank');
}