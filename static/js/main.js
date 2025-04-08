/**
 * Main JavaScript file for the Photosì Service Documentation site.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Handle mobile navigation toggle if needed
    const mobileNavToggle = document.getElementById('mobile-nav-toggle');
    const sidebar = document.querySelector('.sidebar');
    
    if (mobileNavToggle && sidebar) {
        mobileNavToggle.addEventListener('click', () => {
            sidebar.classList.toggle('show');
        });
    }
});
