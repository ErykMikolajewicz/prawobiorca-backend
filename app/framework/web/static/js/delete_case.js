document.addEventListener("DOMContentLoaded", () => {
  document
    .querySelectorAll('[data-bs-toggle="popover"]')
    .forEach((button) => {

      const caseId = button.closest("li")
        .querySelector("input[name='caseId']")
        ?.value;

      const content = `
        <form action="/user/cases/delete" method="post">
          <input type="hidden" name="caseId" value="${caseId}">
          <p class="mb-2">Na pewno usunąć?</p>
          <button type="submit" class="btn btn-sm btn-danger w-100">
            Potwierdź
          </button>
        </form>
      `;

      new bootstrap.Popover(button, {
        html: true,
        content: content,
        container: "body",
        trigger: "focus",
        sanitize: false,  
      });
    });
});