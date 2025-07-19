document.addEventListener("DOMContentLoaded", function () {
  // Flash message removal
  const flashMessages = document.getElementById("flash-messages");
  if (flashMessages) {
    setTimeout(() => {
      flashMessages.remove();
    }, 3000);
  }

  // Handle ticket detail view
  const detailButtons = document.querySelectorAll(".view-details-btn");

  detailButtons.forEach(btn => {
    btn.addEventListener("click", function () {
      const ticketId = this.getAttribute("data-id");

      fetch(`/employee/ticket/${ticketId}/json/`)
        .then(response => response.json())
        .then(data => {
          const modalContent = document.getElementById("ticketDetailContent");

          let html = `
            <p><strong>Title:</strong> ${data.title}</p>
            <p><strong>Description:</strong> ${data.description}</p>
            <p><strong>Client:</strong> ${data.client}</p>
            <p><strong>Priority:</strong> ${data.priority}</p>
            <p><strong>Status:</strong> ${data.status}</p>
            <p><strong>Created At:</strong> ${data.created_at}</p>
          `;

          if (data.status === "completed") {
            html += `
              <p><strong>Issue Description:</strong> ${data.issue_description || 'N/A'}</p>
              <p><strong>Solution:</strong> ${data.solution || 'N/A'}</p>
              ${data.signoff_attachment ? `<p><strong>Signoff File:</strong> ${data.signoff_attachment}</p>` : ''}
            `;
          } else {
            html += `
              <form method="POST" enctype="multipart/form-data" id="completeTicketForm">
                <div class="mb-3">
                  <label class="form-label">Issue Description</label>
                  <textarea name="issue_description" class="form-control" required></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Solution</label>
                  <textarea name="solution" class="form-control" required></textarea>
                </div>
                <div class="mb-3">
                  <label class="form-label">Signoff Attachment</label>
                  <input type="file" name="signoff_attachment" class="form-control">
                </div>
                <input type="hidden" name="ticket_id" value="${data.id}">
                <div class="d-flex justify-content-end gap-2 mt-3">
                  <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                  <button type="submit" class="btn btn-success">Complete</button>
                </div>
              </form>
            `;
          }

          modalContent.innerHTML = html;

          // Rebind form submission inside modal
          const completeForm = document.getElementById("completeTicketForm");
          if (completeForm) {
            completeForm.addEventListener("submit", function (e) {
              e.preventDefault();
              const formData = new FormData(completeForm);

              fetch("/employee/ticket/complete/", {
                method: "POST",
                body: formData,
                headers: {
                  "X-CSRFToken": getCookie("csrftoken")
                }
              })
                .then(response => response.json())
                .then(data => {
                  const modalEl = document.getElementById("ticketDetailModal");
                  const modalInstance = bootstrap.Modal.getInstance(modalEl);
                  if (modalInstance) modalInstance.hide();

                  // Clean up blur/backdrop
                  document.querySelectorAll(".modal-backdrop").forEach(el => el.remove());
                  document.body.classList.remove("modal-open");
                  document.body.style.overflow = "";

                  // Show flash message
                  if (data.message) {
                    showToast(data.message, "success");
                    setTimeout(() => window.location.reload(), 1500);
                  } else if (data.error) {
                    showToast(data.error, "danger");
                  }
                })
                .catch(() => showToast("Something went wrong", "danger"));
            });
          }
        });
    });
  });

  // CSRF token helper
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie) {
      document.cookie.split(";").forEach(cookie => {
        const trimmed = cookie.trim();
        if (trimmed.startsWith(name + "=")) {
          cookieValue = decodeURIComponent(trimmed.substring(name.length + 1));
        }
      });
    }
    return cookieValue;
  }

  // Toast display function
  function showToast(message, type = "success") {
    const toast = document.getElementById("flash-toast");
    const body = document.getElementById("flash-message-content");
    const header = toast.querySelector(".toast-header");

    body.textContent = message;
    header.className = "toast-header text-white bg-" + type;

    const bsToast = new bootstrap.Toast(toast, { delay: 3000 });
    bsToast.show();
  }
});


window.addEventListener('pageshow', function () {
  document.body.classList.remove('modal-open');
  document.querySelectorAll('.modal-backdrop').forEach(el => el.remove());
});


//email setting togle js logic

 const enableEmail = document.getElementById('enableEmail');
  const notifyAssignment = document.getElementById('notifyAssignment');
  const notifyCompletion = document.getElementById('notifyCompletion');

  enableEmail.addEventListener('change', function () {
    const checked = this.checked;
    notifyAssignment.checked = checked;
    notifyCompletion.checked = checked;
  });