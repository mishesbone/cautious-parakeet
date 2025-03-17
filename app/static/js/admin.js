// Select list items and the toggle button
const listItems = document.querySelectorAll('.navigation li');
const toggle = document.querySelector('.toggle');
const navigation = document.querySelector('.navigation');
const main = document.querySelector('.main');

// Function to add the 'hovered' class to the selected list item
function setActiveLink() {
  listItems.forEach(item => {
    item.classList.remove('hovered');
  });
  this.classList.add('hovered');
}

// Add event listeners for mouseover to each list item
listItems.forEach(item => {
  item.addEventListener('mouseover', setActiveLink);
});

// Menu Toggle
toggle.addEventListener('click', () => {
  navigation.classList.toggle('active');
  main.classList.toggle('active');
});



listItems.forEach(item => {
  item.addEventListener('click', (event) => {
    event.preventDefault();  // Prevent the default jump-to-anchor behavior
    const targetId = item.getAttribute('data-content-id');
    const targetElement = document.querySelector(`#${targetId}`);
    if (targetElement) {
      window.scrollTo({
        behavior: 'smooth',
        top: targetElement.offsetTop
      });
    }
  });
});

listItems.forEach(item => {
  item.addEventListener('click', () => {
    navigation.classList.remove('active');
    main.classList.remove('active');
  });
});


document.addEventListener('keydown', (event) => {
  if (event.key === 'ArrowUp' || event.key === 'ArrowDown') {
    const activeIndex = Array.from(listItems).findIndex(item => item.classList.contains('hovered'));
    if (activeIndex !== -1) {
      listItems[activeIndex].classList.remove('hovered');
      const nextIndex = (event.key === 'ArrowDown') ? (activeIndex + 1) % listItems.length : (activeIndex - 1 + listItems.length) % listItems.length;
      listItems[nextIndex].classList.add('hovered');
    }
  }
});

