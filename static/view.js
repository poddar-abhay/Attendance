const attendanceContainer = document.getElementById("attendance-container");
const datePicker = document.getElementById("date-picker");
const filterBtn = document.getElementById("filter-btn");

// Fetch all attendance data
async function fetchAllAttendance() {
    const response = await fetch('/get-attendance');
    const data = await response.json();
    return data;
}

// Fetch attendance for a specific date
async function fetchAttendanceByDate(date) {
    const response = await fetch(`/get-attendance-by-date?date=${date}`);
    const data = await response.json();
    return data;
}

// Render attendance data
function renderAttendance(data) {
    attendanceContainer.innerHTML = ""; // Clear existing data

    for (const date in data) {
        const entries = data[date];

        const table = document.createElement("table");
        let tableHTML = `
            <caption>${date}</caption>
            <thead>
                <tr>
                    <th>Student Name</th>
                </tr>
            </thead>
            <tbody>
        `;

        entries.forEach(entry => {
            tableHTML += `
                <tr>
                    <td>${entry.student}</td>
                </tr>
            `;
        });

        tableHTML += "</tbody>";
        table.innerHTML = tableHTML;
        attendanceContainer.appendChild(table);
    }
}

// Load all attendance on page load
window.onload = async () => {
    const data = await fetchAllAttendance();
    renderAttendance(data);
};

// Filter attendance by date
filterBtn.addEventListener("click", async () => {
    const date = datePicker.value;
    if (!date) {
        alert("Please select a date!");
        return;
    }
    const data = await fetchAttendanceByDate(date);
    renderAttendance(data);
});