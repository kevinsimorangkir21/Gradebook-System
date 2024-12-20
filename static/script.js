function updateLastModified() {
    const course = document.getElementById('course').value;
    const lastUpdatedElement = document.getElementById('lastUpdated');

    if (!course) {
        lastUpdatedElement.textContent = '';
        return;
    }

    fetch(`/last_modified/${course}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            lastUpdatedElement.textContent = data.error ? data.error : `Last Updated: ${data.last_modified_date}`;
        })
        .catch(error => {
            lastUpdatedElement.textContent = 'Error fetching last modified date.';
            console.error('Error:', error);
        });
}

function getGrades() {
    const course = document.getElementById('course').value;
    const studentId = document.getElementById('studentId').value;
    const resultDiv = document.getElementById('result');
    const spinner = document.getElementById('spinner');

    if (!course || !studentId) {
        resultDiv.innerHTML = '<p>Please select a course and enter a student ID.</p>';
        return;
    }

    spinner.style.display = 'block';
    resultDiv.innerHTML = '';

    fetch(`/grades/${course}/${studentId}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            spinner.style.display = 'none';
            if (data.error) {
                resultDiv.innerHTML = `<p>${data.error}</p>`;
            } else {
                let gradesHtml = `<h2>Grades for Student ID: ${studentId}</h2><ul>`;
                const categories = ['Name', 'Assignment 1', 'Assignment 2', 'Assignment 3', 'Assignment 4', 'Quiz 1', 'Quiz 2', 'Rata - Rata'];
                categories.forEach(category => {
                    if (data.hasOwnProperty(category)) {
                        gradesHtml += `<li class="grade-item"><span class="grade-header">${category}:</span> ${data[category]}</li>`;
                    }
                });
                gradesHtml += '</ul>';
                resultDiv.innerHTML = gradesHtml;
                resultDiv.classList.add('show');
            }
        })
        .catch(error => {
            spinner.style.display = 'none';
            resultDiv.innerHTML = '<p>Error fetching grades.</p>';
            console.error('Error:', error);
        });
}

function exportToPDF() {
    const course = document.getElementById('course').value;
    const studentId = document.getElementById('studentId').value;

    if (!course || !studentId) {
        alert('Please select a course and enter a student ID.');
        return;
    }

    window.open(`/export_pdf/${course}/${studentId}`, '_blank');
}

window.onload = updateLastModified;
