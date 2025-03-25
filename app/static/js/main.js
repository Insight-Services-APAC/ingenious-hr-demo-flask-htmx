/**
 * Main JavaScript for CV Analysis Tool
 */

// Initialize Bootstrap tooltips and popovers
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Handle HTMX events
document.body.addEventListener('htmx:afterSwap', function(event) {
    // Re-initialize tooltips and popovers after HTMX updates
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function(tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    var popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    var popoverList = popoverTriggerList.map(function(popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });
});

// Handle feedback submission responses
document.body.addEventListener('htmx:afterRequest', function(event) {
    if (event.detail.pathInfo.requestPath === '/submit-feedback') {
        const response = JSON.parse(event.detail.xhr.responseText);
        
        if (response.success) {
            // Create and show a success alert
            const alertDiv = document.createElement('div');
            alertDiv.className = 'alert alert-success feedback-alert';
            alertDiv.textContent = 'Thank you for your feedback!';
            document.body.appendChild(alertDiv);
            
            // Replace the feedback buttons with a success message
            const feedbackContainer = event.detail.target.closest('.card-body');
            feedbackContainer.innerHTML = '<div class="alert alert-success">Thank you for your feedback!</div>';
            
            // Remove the alert after animation completes
            setTimeout(function() {
                if (alertDiv.parentNode) {
                    alertDiv.parentNode.removeChild(alertDiv);
                }
            }, 4000);
        }
    }
});

// Add markdown rendering function to process analysis content
// Note: This would require a markdown library like marked.js to be included
// For a full implementation, you would include marked.js in the base template
// and use it to render markdown content