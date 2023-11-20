const stafftag = document.getElementById('staffs');
const staffsapi = 'http://127.0.0.1:5000/api/retrive_all_staff'; 
let html;

fetch(staffsapi)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(dataArray => {
    console.log(dataArray);
    for (const item of dataArray) {
      const id = item[0];
      const name = item[1];
      html += `<option value="${id}">${name}</option>`;
    }
    stafftag.innerHTML = html;
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });
