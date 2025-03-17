// Flag to toggle behavior of the #delete button
let addingCheckboxes = true;
    
// Add event listener to the #delete button
document.getElementById("delete").addEventListener("click", function() {
    const rows = document.querySelectorAll("tbody .table-cel");
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


 
   
// Get the input element, the table, and the display div
const inputElement = document.getElementById("selectPaycode");
const table = document.querySelector(".selectPaycode");
const displayDiv = document.getElementById("selectPaycodeDisplay");

// Add a click event listener to the input element
inputElement.addEventListener("click", function() {
    // Toggle the table's visibility
    if (table.style.display === "none" || table.style.display === "") {
        table.style.display = "table";
    } else {
        table.style.display = "none";
    }
});

// Add a change event listener to each checkbox
const checkboxes = document.querySelectorAll(".checkbox");
checkboxes.forEach(checkbox => {
    checkbox.addEventListener("change", function() {
        // Show the display div when a checkbox is checked
        if (checkbox.checked) {
            displayDiv.style.display = "block";

            const newTable = document.createElement("table");
            const newTbody = document.createElement("tbody");
            displayDiv.appendChild(newTable);
            newTable.appendChild(newTbody);

            // Find the parent <tr>
            const parentTr = checkbox.closest("tr");

            // Create a new <tr> to hold the second <td>
            const newTr = document.createElement("tr");
            
            // Clone the second <td> and append it to the new <tr>
            const secondTd = parentTr.querySelector("td:nth-child(2)");
            const clonedTd = secondTd.cloneNode(true);
            newTr.appendChild(clonedTd);

            // Append the new <tr> to the new table
            newTbody.appendChild(newTr);
        }
    });
});

// JavaScript to show/hide the fixed-amount div based on the selected option
const selectOption = document.getElementById("selectOption");
const fixedAmountDiv = document.querySelector(".fixed-amount");

selectOption.addEventListener("change", function () {
  if (selectOption.value === "Fixed Amount") {
    fixedAmountDiv.style.display = "block"; // Show the div
  } else {
    fixedAmountDiv.style.display = "none"; // Hide the div for other options
  }
});

// JavaScript to show the percentagePaycode div when "PERCENTAGE OF PAYCODE" is selected
const selectsOption = document.getElementById("selectOption");
const percentagePaycodeDiv = document.querySelector(".percentagePaycode");

selectsOption.addEventListener("change", function () {
  if (selectsOption.value === "Percentage of Paycode") {
    percentagePaycodeDiv.style.display = "block"; // Show the div
  } else {
    percentagePaycodeDiv.style.display = "none"; // Hide the div for other options
  }
});




$(document).ready(function () {
  $("button[type='submit']").on("click", function () {
    $("form").submit(); // Trigger the form submission
  });
});


