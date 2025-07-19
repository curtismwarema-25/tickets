document.addEventListener('DOMContentLoaded', () => {
  const toggleSidebar = document.getElementById('toggleSidebar');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');

  if (toggleSidebar && sidebar && mainContent) {
    toggleSidebar.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      mainContent.classList.toggle('collapsed');
    });
  }
});

const searchInput = document.querySelector('input[type="search"]');
const dropdown = document.getElementById('searchDropdown');

let debounceTimeout;

searchInput.addEventListener('input', function () {
  clearTimeout(debounceTimeout);

  const query = this.value.trim();
  if (query.length < 2) {
    dropdown.style.display = 'none';
    return;
  }

  debounceTimeout = setTimeout(() => {
    fetch(`/admin/search/?q=${encodeURIComponent(query)}`)
      .then(res => res.json())
      .then(data => {
        renderDropdown(data);
      });
  }, 300);
});

function renderDropdown(data) {
  if (!data) return;

  let html = '';

  if (data.tickets.length > 0) {
    html += `<h6 class="dropdown-header">🎫 Tickets</h6>`;
    data.tickets.forEach(ticket => {
      html += `<a class="dropdown-item" href="/admin/tickets/#ticket-${ticket.id}">${ticket.title}</a>`;
    });
  }

  if (data.clients.length > 0) {
    html += `<h6 class="dropdown-header">👤 Clients</h6>`;
    data.clients.forEach(client => {
      html += `<a class="dropdown-item" href="/admin/clients/#client-${client.id}">${client.name}</a>`;
    });
  }

  if (data.employees.length > 0) {
    html += `<h6 class="dropdown-header">🛠 Employees</h6>`;
    data.employees.forEach(emp => {
      html += `<a class="dropdown-item" href="/admin/employees/#employee-${emp.id}">${emp.name}</a>`;
    });
  }

  if (!html) html = `<span class="dropdown-item text-muted">No results found</span>`;

  dropdown.innerHTML = html;
  dropdown.style.display = 'block';
}
document.addEventListener('click', function (e) {
  if (!searchInput.contains(e.target) && !dropdown.contains(e.target)) {
    dropdown.style.display = 'none';
  }
});

// Prevent sidebar tickets dropdown from closing on item click
document.addEventListener('DOMContentLoaded', function() {
  const ticketsDropdownMenu = document.querySelector('#ticketsDropdown + .dropdown-menu');
  if (ticketsDropdownMenu) {
    ticketsDropdownMenu.addEventListener('click', function (e) {
      e.stopPropagation();
    });
  }
});

//messages
  document.addEventListener('DOMContentLoaded', function () {
    const alert = document.querySelector('.alert');
    if (alert) {
      setTimeout(() => {
        alert.classList.remove('show');
        alert.classList.add('hide');
      }, 3000);
    }
  });

  // Edit modal
  const editModal = document.getElementById('editClientModal');
  editModal.addEventListener('show.bs.modal', function (event) {
    const btn = event.relatedTarget;
    document.getElementById('edit-client-id').value = btn.getAttribute('data-id');
    document.getElementById('edit-name').value = btn.getAttribute('data-name');
    document.getElementById('edit-email').value = btn.getAttribute('data-email');
    document.getElementById('edit-phone').value = btn.getAttribute('data-phone');
    document.getElementById('edit-company').value = btn.getAttribute('data-company');
  });

  // Delete modal
  const deleteModal = document.getElementById('confirmDeleteModal');
  deleteModal.addEventListener('show.bs.modal', function (event) {
    const btn = event.relatedTarget;
    const clientId = btn.getAttribute('data-id');
    const clientName = btn.getAttribute('data-name');

    document.getElementById('deleteClientName').textContent = clientName;
    document.getElementById('deleteClientForm').action = `/admin/clients/delete/${clientId}/`;
  });

  // Auto-close flash messages
  setTimeout(() => {
    document.querySelectorAll('.alert').forEach(alert => {
      bootstrap.Alert.getOrCreateInstance(alert).close();
    });
  }, 3000);

// Store original values for comparison
let originalPriority = '';
let originalTechnician = '';
let ticketTitle = '';

// Edit Ticket Modal Handler
document.getElementById('editTicketModal')?.addEventListener('show.bs.modal', function (event) {
  const button = event.relatedTarget;
  const ticketId = button.getAttribute('data-id');
  
  // Store the ticket title and original values for confirmation messages
  ticketTitle = button.getAttribute('data-title');
  
  // Set values for all fields
  document.getElementById('edit-ticket-id').value = ticketId;
  document.getElementById('edit-title').value = ticketTitle;
  document.getElementById('edit-description').value = button.getAttribute('data-description');
  
  // Store original values and set the fields
  originalPriority = button.getAttribute('data-priority');
  originalTechnician = button.getAttribute('data-technician');
  
  document.getElementById('edit-priority').value = originalPriority;
  document.getElementById('edit-technician').value = originalTechnician;
  
  document.getElementById('edit-deadline').value = button.getAttribute('data-deadline');
  
  // Handle status (now a read-only input)
  document.getElementById('edit-status').value = button.getAttribute('data-status')?.replace('_', ' ')?.charAt(0).toUpperCase() + 
    button.getAttribute('data-status')?.slice(1).replace('_', ' ');
  
  // Handle client display
  const clientId = button.getAttribute('data-client-id');
  const clientName = button.getAttribute('data-client-name');
  document.getElementById('edit-client').value = clientId;
  document.getElementById('edit-client-display').value = clientName;
});

// Add change event listeners for priority and technician
document.getElementById('edit-priority')?.addEventListener('change', function(e) {
  if (this.value !== originalPriority) {
    if (!confirm(`Do you really want to change the priority level for ticket "${ticketTitle}" from ${originalPriority} to ${this.value}?`)) {
      this.value = originalPriority; // Revert if canceled
    }
  }
});

document.getElementById('edit-technician')?.addEventListener('change', function(e) {
  if (this.value !== originalTechnician) {
    const newTechName = this.options[this.selectedIndex].text;
    const oldTechName = originalTechnician ? 
      this.querySelector(`option[value="${originalTechnician}"]`)?.text : 
      'Unassigned';
    
    if (!confirm(`Do you want to reassign ticket "${ticketTitle}" from ${oldTechName} to ${newTechName}?`)) {
      this.value = originalTechnician; // Revert if canceled
    }
  }
});

// Form submission handler
document.querySelector('#editTicketModal form')?.addEventListener('submit', function(e) {
  const formData = new FormData(this);
  formData.delete('title');  // Remove read-only fields
  formData.delete('description');
  formData.delete('deadline');
  formData.delete('client_display');
  formData.delete('status');
});
