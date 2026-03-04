const dropdownItems = document.querySelectorAll('.dropdown-item');
const dropdownButton = document.getElementById('dropdown-button');

function updateDropdownValue(val) {
    dropdownButton.textContent = val;
}
dropdownItems.forEach(item => {
    item.addEventListener("click", () => {
        updateDropdownValue(item.textContent);
    });
})