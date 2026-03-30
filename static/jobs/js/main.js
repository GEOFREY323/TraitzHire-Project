document.querySelectorAll('.save-job-btn').forEach(btn => {

btn.addEventListener('click', function() {

fetch(`/jobs/${this.dataset.jobPk}/save/`, {

method: 'POST',

headers: {
'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
}

})

.then(response => response.json())

.then(data => {

this.textContent = data.saved ? 'Saved' : 'Save Job';

this.classList.toggle('btn-primary', data.saved);
this.classList.toggle('btn-outline', !data.saved);

});

});

});