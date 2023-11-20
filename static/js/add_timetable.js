const subjectstag = document.getElementById('subjects');
const naanmudhalvantag = document.getElementById('naan');
const subjectsapi = 'http://127.0.0.1:5000/api/retrive_all_subjects';
let html; 
html += '<option value="000000">No Class</option>';

fetch(subjectsapi)
  .then(response => {
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    return response.json();
  })
  .then(dataArray => {
    for (const item of dataArray) {
      const id = item[0];
      const name = item[1];
      html += `<option value="${id}">${name}</option>`;
    }
    subjectstag.innerHTML = html;
  })
  .catch(error => {
    console.error('There was a problem with the fetch operation:', error);
  });


  naanmudhalvantag.addEventListener("input", function(event) {
    var value = naanmudhalvantag.value.toLowerCase();
  
    for (var i = 1; i <= 8; i++) {
      var tagName = value + '_' + i;
      var tags = document.getElementsByName(tagName);
  
      for (var j = 0; j < tags.length; j++) {
        tags[j].value = '000000';
        tags[j].readOnly = true;
      }
    }
  });
  