   // Get all the links you want to render when clicked
   const links = document.querySelectorAll('.navigation a');

   // Add click event listeners to each link
   links.forEach(link => {
       link.addEventListener('click', (event) => {
           event.preventDefault(); // Prevent the default link behavior

           // Get the href attribute of the clicked link
           const href = link.getAttribute('href');

           // Redirect to the URL
           window.location.href = href;
       });
   });