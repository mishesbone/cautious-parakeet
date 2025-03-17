 // JavaScript to show/hide the fixed-amount div based on the selected option
 const selectOption = document.getElementById("create");
 const fixedAmountDiv = document.querySelector(".fixed-amount");

 selectOption.addEventListener("change", function () {
   if (selectOption.value === "basic") {
     fixedAmountDiv.style.display = "block"; // Show the div
   } else {
     fixedAmountDiv.style.display = "none"; // Hide the div for other options
   }
 });

 // JavaScript to show/hide the fixed-amount div based on the selected option
 const selectOptio = document.getElementById("create");
 const fixedAmountDi = document.querySelector(".fixed-amoun");

 selectOptio.addEventListener("change", function () {
   if (selectOptio.value === "transport") {
     fixedAmountDi.style.display = "block"; // Show the div
   } else {
     fixedAmountDi.style.display = "none"; // Hide the div for other options
   }
 });

 // JavaScript to show/hide the fixed-amount div based on the selected option
 const selectOpti = document.getElementById("create");
 const fixedAmountD = document.querySelector(".fixed-amou");

 selectOpti.addEventListener("change", function () {
   if (selectOpti.value === "housing") {
     fixedAmountD.style.display = "block"; // Show the div
   } else {
     fixedAmountD.style.display = "none"; // Hide the div for other options
   }
 });