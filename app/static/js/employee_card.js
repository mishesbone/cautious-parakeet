 // Wait for the document to be ready
 $(document).ready(function () {
    // Hide the table initially (assuming it's on display: none)
    $("#deductionTable").hide();

    // Toggle the display when the "deduction" element is clicked
    $("#deductions").click(function () {
        $("#deductionTable").toggle();
    });
});

 // Wait for the document to be ready
 $(document).ready(function () {
    // Attach a click event handler to the checkboxes
    $(".checkbox").click(function () {
        // Find all checked checkboxes
        const checkedCheckboxes = $(".checkbox:checked");

        // Create a new table to hold the checked rows
        let newTable = "<table><thead><tr><th>Deduction</th><th>Code</th><th>Method of Computation</th></tr></thead><tbody>";

        // Loop through the checked checkboxes and collect data
        checkedCheckboxes.each(function () {
            const $row = $(this).closest("tr");
            const rowData = {
                name: $row.find("td:eq(1)").text(),
                code: $row.find("td:eq(2)").text(),
                method: $row.find("td:eq(3)").text()
            };

            // Append the checked row data to the new table
            newTable += `<tr><td>${rowData.name}</td><td>${rowData.code}</td><td>${rowData.method}</td></tr>`;
        });

        // Close the new table
        newTable += "</tbody></table>";

        // Display the new table in the "display" div
        $("#display").html(newTable);

        // Show the "display" div if there are checked checkboxes, hide it otherwise
        if (checkedCheckboxes.length > 0) {
            $("#display").show();
        } else {
            $("#display").hide();
        }
    });
});


 //BENEFIT FUNCTIONALITY
 $(document).ready(function () {
    // Hide the table initially (assuming it's on display: none)
    $("#BenefitTable").hide();

    // Toggle the display when the "deduction" element is clicked
    $("#benefit").click(function () {
        $("#BenefitTable").toggle();
    });
});

$(document).ready(function () {
    // Attach a click event handler to the checkboxes
    $(".checkboxs").click(function () {
        // Find all checked checkboxes
        const checkedCheckboxe = $(".checkboxs:checked");

        // Create a new table to hold the checked rows
        let newTable = "<table><thead><tr><th>Benefit</th><th>Code</th><th>Method of Computation</th></tr></thead><tbody>";

        // Loop through the checked checkboxes and collect data
        checkedCheckboxe.each(function () {
            const $row = $(this).closest("tr");
            const rowData = {
                name: $row.find("td:eq(1)").text(),
                code: $row.find("td:eq(2)").text(),
                method: $row.find("td:eq(3)").text()
            };

            // Append the checked row data to the new table
            newTable += `<tr><td>${rowData.name}</td><td>${rowData.code}</td><td>${rowData.method}</td></tr>`;
        });

        // Close the new table
        newTable += "</tbody></table>";

        // Display the new table in the "display" div
        $("#benefit-display").html(newTable);

        // Show the "display" div if there are checked checkboxes, hide it otherwise
        if (checkedCheckboxe.length > 0) {
            $("#benefit-display").show();
        } else {
            $("#benefit-display").hide();
        }
    });
});


// Flag to toggle behavior of the #delete button
let addingCheckboxes = true;

// Add event listener to the #delete button
document.getElementById("delete").addEventListener("click", function() {
    const rows = document.querySelectorAll("tbody .table-cell");
    if (addingCheckboxes) {
        rows.forEach(row => {
            const checkboxCell = document.createElement("td");
            const checkbox = document.createElement("input");
            checkbox.type = "checkbox";
            checkboxCell.appendChild(checkbox);
            row.appendChild(checkboxCell);
        });
        this.textContent = "Delete Rows";
    } else {
        const checkboxes = document.querySelectorAll("tbody input[type=checkbox]");
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const row = checkbox.parentElement.parentElement;
                // Remove the row
                row.remove();
            }
        });

        // Hide the checkboxes
        checkboxes.forEach(checkbox => {
            checkbox.style.display = "none";
        });

        this.textContent = "Add Checkboxes";
    }
    addingCheckboxes = !addingCheckboxes;
});

// JavaScript to handle checkbox interactions if needed
const checkboxes = document.querySelectorAll(".checkbox");

checkboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        // Handle checkbox change event here
        if (checkbox.checked) {
            // Checkbox is checked
            console.log("Checkbox checked:", checkbox.parentElement.textContent.trim());
        } else {
            // Checkbox is unchecked
            console.log("Checkbox unchecked:", checkbox.parentElement.textContent.trim());
        }
    });
});





    // Get the checkbox elements
    const checkboxs = document.querySelectorAll('.checkbox');

    // Get the deduction-display div
    const deductionDisplay = document.getElementById('deduction-display');

    checkboxs.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.checked) {
                // Get the associated deduction details (you can fetch from data attributes or another source)
                const deductionName = this.parentElement.nextElementSibling.innerText;
                const deductionCode = this.parentElement.nextElementSibling.nextElementSibling.innerText;
                const computationMethod = this.parentElement.nextElementSibling.nextElementSibling.nextElementSibling.innerText;

                // Create a message to display
                const message = `Deduction: ${deductionName}, Code: ${deductionCode}, Method: ${computationMethod}`;

                // Display the message in the deduction-display div
                deductionDisplay.textContent = message;
            } else {
                // Clear the message when the checkbox is unchecked
                deductionDisplay.textContent = '';
            }
        });
    });



    document.getElementById("delete").addEventListener("click", function () {
        const checkboxes = document.querySelectorAll("tbody input[type=checkbox]");
        const checkedRows = [];
        
        checkboxes.forEach(checkbox => {
            if (checkbox.checked) {
                const row = checkbox.closest("tr");
                const employeeId = row.querySelector('.table-cell:nth-child(1)').textContent; // Get the employee ID from the first cell
                checkedRows.push(employeeId);
            }
        });
    
        // Check if any checkbox is checked
        if (checkedRows.length > 0) {
            if (confirm("Are you sure you want to delete the selected entries?")) {
                // Make an AJAX request to delete the selected entries
                fetch('/' + company_id + '/delete_employee/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ employee_ids: checkedRows })
                })
                .then(response => {
                    if (response.ok) {
                        // If deletion is successful, remove the selected rows from the table
                        checkedRows.forEach(employeeId => {
                            const row = document.querySelector(`.table-cell:nth-child(1):contains('${employeeId}')`).closest("tr");
                            row.remove();
                        });
                    } else {
                        // Handle deletion failure
                        alert('Failed to delete selected entries.');
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                });
            }
        } else {
            alert('Please select entries to delete.');
        }
    });
    