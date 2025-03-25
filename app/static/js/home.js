// For job criteria preview and update
document.body.addEventListener('htmx:afterSwap', function(event) {
    if (event.detail.target.id === 'job-criteria-preview') {
        const updateBtn = document.getElementById('update-criteria-btn');
        if (updateBtn) {
            updateBtn.addEventListener('click', function() {
                const jobCriteria = JSON.parse(document.getElementById('job-criteria-json').textContent);
                
                fetch("/update-job-criteria", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        job_criteria: jobCriteria
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        const successDiv = document.createElement('div');
                        successDiv.style.padding = '12px';
                        successDiv.style.marginTop = '16px';
                        successDiv.style.backgroundColor = 'var(--success-background)';
                        successDiv.style.color = 'var(--success-font)';
                        successDiv.style.borderRadius = '4px';
                        successDiv.innerHTML = 'Job criteria updated successfully!';
                        document.getElementById('job-criteria-preview').appendChild(successDiv);
                        
                        setTimeout(() => {
                            successDiv.remove();
                        }, 5000);
                    } else {
                        const errorDiv = document.createElement('div');
                        errorDiv.style.padding = '12px';
                        errorDiv.style.marginTop = '16px';
                        errorDiv.style.backgroundColor = 'var(--error-background)';
                        errorDiv.style.color = 'var(--error-font)';
                        errorDiv.style.borderRadius = '4px';
                        errorDiv.innerHTML = `Failed to update job criteria: ${data.error}`;
                        document.getElementById('job-criteria-preview').appendChild(errorDiv);
                    }
                })
                .catch(error => {
                    console.error('Error:', error);
                    const errorDiv = document.createElement('div');
                    errorDiv.style.padding = '12px';
                    errorDiv.style.marginTop = '16px';
                    errorDiv.style.backgroundColor = 'var(--error-background)';
                    errorDiv.style.color = 'var(--error-font)';
                    errorDiv.style.borderRadius = '4px';
                    errorDiv.innerHTML = `Error: ${error.message}`;
                    document.getElementById('job-criteria-preview').appendChild(errorDiv);
                });
            });
        }
    }
});

// CV Upload Form with Progress Bar
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('cv-upload-form');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    if (uploadForm) {
        // Debug to check if elements are found
        console.log("Upload form found:", uploadForm);
        console.log("Progress container:", progressContainer);
        console.log("Progress bar:", progressBar);
        
        uploadForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            // Show the progress container by removing d-none class
            progressContainer.classList.remove('d-none');
            console.log("Progress container should now be visible");
            analyzeBtn.disabled = true;
            
            const fileInput = document.getElementById('cv_files');
            const files = fileInput.files;
            
            if (files.length === 0) {
                alert('Please select at least one file');
                progressContainer.style.display = 'none';
                analyzeBtn.disabled = false;
                return;
            }
            
            const formData = new FormData();
            for (let i = 0; i < files.length; i++) {
                formData.append('cv_files', files[i]);
            }
            
            const xhr = new XMLHttpRequest();
            
            xhr.upload.addEventListener('progress', function(e) {
                if (e.lengthComputable) {
                    const percentComplete = Math.round((e.loaded / e.total) * 30);
                    updateProgressBar(percentComplete, 'Uploading files...');
                }
            });
            
            xhr.addEventListener('load', function() {
                if (xhr.status === 200) {
                    updateProgressBar(100, 'Analysis complete!');
                    window.location.href = "/analysis";
                } else if (xhr.status === 202) {
                    const data = JSON.parse(xhr.responseText);
                    const jobId = data.job_id;
                    pollAnalysisProgress(jobId);
                } else {
                    progressStatus.textContent = 'Error: ' + xhr.statusText;
                    progressBar.classList.remove('bg-primary');
                    progressBar.classList.add('bg-danger');
                    analyzeBtn.disabled = false;
                }
            });
            
            xhr.addEventListener('error', function() {
                progressStatus.textContent = 'Upload failed. Please try again.';
                progressBar.setAttribute('appearance', 'error');
                analyzeBtn.disabled = false;
            });
            
            xhr.open('POST', '/upload-cv', true);
            xhr.send(formData);
            
            updateProgressBar(0, 'Preparing files...');
        });
    }
    
    function updateProgressBar(percent, statusText) {
        progressBar.setAttribute('aria-valuenow', percent);
        progressBar.style.width = percent + '%';
        progressBar.innerHTML = `<span>${percent}%</span>`;
        progressStatus.textContent = statusText;
        
        if (percent === 100) {
            progressBar.classList.remove('progress-bar-animated');
            progressBar.classList.add('bg-success');
        }
    }
    
    function pollAnalysisProgress(jobId) {
        const pollInterval = setInterval(function() {
            fetch('/check-progress?job_id=' + jobId)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'processing') {
                        const percent = 30 + Math.round(data.progress * 70);
                        updateProgressBar(percent, data.message || 'Analyzing CVs...');
                    } else if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        updateProgressBar(100, 'Analysis complete!');
                        window.location.href = "/analysis";
                    } else if (data.status === 'failed') {
                        clearInterval(pollInterval);
                        progressStatus.textContent = 'Analysis failed: ' + data.message;
                        progressBar.classList.remove('bg-primary');
                    progressBar.classList.add('bg-danger');
                        analyzeBtn.disabled = false;
                    }
                })
                .catch(error => {
                    console.error('Error polling progress:', error);
                });
        }, 1000);
    }
});