
document.addEventListener('DOMContentLoaded', function () {
  // Initialize Bootstrap Toasts
  var toastElList = [].slice.call(document.querySelectorAll('.toast'));
  var toastList = toastElList.map(function (toastEl) {
    return new bootstrap.Toast(toastEl, { autohide: true, delay: 5000 });
  });
  toastList.forEach(toast => toast.show());

  // Initialize Bootstrap Alerts for dismissal
  var alertList = document.querySelectorAll('.alert-dismissible');
  alertList.forEach(function (alert) {
    new bootstrap.Alert(alert);
  });

  // Sidebar toggle functionality
  const toggleSidebar = document.getElementById('toggleSidebar');
  const sidebar = document.getElementById('sidebar');
  const mainContent = document.getElementById('mainContent');

  if (toggleSidebar && sidebar && mainContent) {
    toggleSidebar.addEventListener('click', () => {
      sidebar.classList.toggle('collapsed');
      mainContent.classList.toggle('expanded');
    });
  }
});
