document.addEventListener("DOMContentLoaded", function () {
  const sidebar = document.querySelector(".main-sidebar");
  const navbar = document.querySelector(".navbar");

  // Prevent duplicate toggle buttons
  if (!document.querySelector("#sidebar-toggle-btn")) {
    // Create toggle button
    const toggleBtn = document.createElement("button");
    toggleBtn.id = "sidebar-toggle-btn";
    toggleBtn.classList.add(
      "btn",
      "btn-primary",
      "d-lg-none", // visible only on mobile
      "me-2"
    );
    toggleBtn.setAttribute("aria-label", "Toggle sidebar");
    
    // Use a professional hamburger icon (three bars)
    toggleBtn.innerHTML = `
      <span style="display:block; width:22px; height:2px; background:#fff; margin:4px 0;"></span>
      <span style="display:block; width:22px; height:2px; background:#fff; margin:4px 0;"></span>
      <span style="display:block; width:22px; height:2px; background:#fff; margin:4px 0;"></span>
    `;

    // Add button to navbar
    navbar.prepend(toggleBtn);

    // Toggle sidebar on click
    toggleBtn.addEventListener("click", () => {
      sidebar.classList.toggle("active");
    });

    // Close sidebar when clicking outside (mobile only)
    document.addEventListener("click", (e) => {
      if (
        window.innerWidth <= 768 &&
        sidebar.classList.contains("active") &&
        !sidebar.contains(e.target) &&
        !toggleBtn.contains(e.target)
      ) {
        sidebar.classList.remove("active");
      }
    });

    // Optional: Close sidebar on resize to desktop
    window.addEventListener("resize", () => {
      if (window.innerWidth > 768 && sidebar.classList.contains("active")) {
        sidebar.classList.remove("active");
      }
    });
  }
});
