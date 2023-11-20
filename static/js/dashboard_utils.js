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
    const active = document.getElementsByClassName("active");
    active[0].className = active[0].className.replace(" active", "");
    element.className += " active";
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