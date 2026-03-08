const dropdownItems = document.querySelectorAll('.dropdown-item');
const dropdownButton = document.getElementById('dropdown-button');

function updateDropdownValue(val) {
    dropdownButton.textContent = val;
}
dropdownItems.forEach(item => {
    item.addEventListener("click", (e) => {
        e.preventDefault();
        updateDropdownValue(item.textContent);

        // Aktualizuj ukryte pola case_id w formularzach
        const caseId = item.getAttribute("data-case-id");
        const caseIdInputs = document.querySelectorAll('.selected-case-id');
        caseIdInputs.forEach(input => {
            input.value = caseId;
        });

        // Odblokuj przyciski dodawania po wybraniu sprawy
        const addButtons = document.querySelectorAll('.btn-on-list');
        addButtons.forEach(btn => {
            btn.disabled = false;
        });
    });
})