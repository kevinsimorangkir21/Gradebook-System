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
            lastUpdatedElement.textContent = data.error 
                ? data.error 
                : `Last Updated: ${data.last_modified_date}`;
        })
        .catch(error => {
            lastUpdatedElement.textContent = 'Error fetching last modified date.';
            console.error('Error:', error);
        });
}

function getGrades() {
    const studentId = document.getElementById('studentId').value;
    const course = document.getElementById('course').value;
    const resultDiv = document.getElementById('result');
    const spinner = document.getElementById('spinner');

    if (!studentId || !course) {
        alert('Please enter Student ID and select a Course.');
        return;
    }

    resultDiv.innerHTML = '';
    spinner.style.display = 'block';

    fetch(`/get_grades?studentId=${studentId}&course=${course}`)
        .then(response => {
            if (!response.ok) throw new Error('Network response was not ok');
            return response.json();
        })
        .then(data => {
            spinner.style.display = 'none';

            if (data.error) {
                resultDiv.innerHTML = `<p>${data.error}</p>`;
                return;
            }

            data.grades.forEach(grade => {
                const gradeItem = document.createElement('div');
                gradeItem.classList.add('grade-item');
                gradeItem.innerHTML = `<span class="grade-header">${grade.assignment}</span><span>${grade.score}</span>`;
                resultDiv.appendChild(gradeItem);
            });
        })
        .catch(error => {
            spinner.style.display = 'none';
            resultDiv.innerHTML = '<p>Error retrieving grades.</p>';
            console.error('Error:', error);
        });
}
