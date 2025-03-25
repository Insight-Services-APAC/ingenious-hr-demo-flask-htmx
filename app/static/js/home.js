// CV Upload Form with Progress Bar
document.addEventListener('DOMContentLoaded', function() {
    const uploadForm = document.getElementById('cv-upload-form');
    const progressContainer = document.getElementById('upload-progress-container');
    const progressBar = document.getElementById('upload-progress-bar');
    const progressStatus = document.getElementById('progress-status');
    const analyzeBtn = document.getElementById('analyze-btn');
    
    if (uploadForm) {
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
                progressContainer.classList.add('d-none');
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
                    window.location.href = "/analysis/";
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
                progressBar.classList.remove('bg-primary');
                progressBar.classList.add('bg-danger');
                analyzeBtn.disabled = false;
            });
            
            xhr.open('POST', '/analysis/upload-cv', true);
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
            fetch('/analysis/check-progress?job_id=' + jobId)
                .then(response => response.json())
                .then(data => {
                    if (data.status === 'processing') {
                        const percent = 30 + Math.round(data.progress * 70);
                        updateProgressBar(percent, data.message || 'Analyzing CVs...');
                    } else if (data.status === 'completed') {
                        clearInterval(pollInterval);
                        updateProgressBar(100, 'Analysis complete!');
                        window.location.href = "/analysis/";
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

    // Job Criteria Form handling
    const jobCriteriaForm = document.getElementById('job-criteria-form');
    const loadingIndicator = document.getElementById('loading-indicator');
    const jobCriteriaPreview = document.getElementById('job-criteria-preview');

    if (jobCriteriaForm) {
        jobCriteriaForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            const fileInput = document.getElementById('job_criteria_file');
            if (!fileInput.files.length) {
                alert('Please select a file');
                return;
            }

            const formData = new FormData(jobCriteriaForm);
            
            // Show loading indicator
            loadingIndicator.classList.remove('d-none');
            
            fetch('/job-criteria/upload', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                loadingIndicator.classList.add('d-none');
                
                if (data.success) {
                    jobCriteriaPreview.innerHTML = renderJobCriteriaPreview(data);
                    
                    // Add event listener to the update button
                    const updateBtn = document.getElementById('update-criteria-btn');
                    if (updateBtn) {
                        updateBtn.addEventListener('click', function() {
                            updateJobCriteria(data.job_criteria);
                        });
                    }
                } else {
                    jobCriteriaPreview.innerHTML = `
                        <div class="alert alert-danger">
                            ${data.error || 'An error occurred while processing the file'}
                        </div>
                    `;
                }
            })
            .catch(error => {
                loadingIndicator.classList.add('d-none');
                jobCriteriaPreview.innerHTML = `
                    <div class="alert alert-danger">
                        Error: ${error.message || 'An unexpected error occurred'}
                    </div>
                `;
            });
        });
    }

    function renderJobCriteriaPreview(data) {
        return `
            <div class="card">
                <div class="card-header bg-light">
                    <ul class="nav nav-tabs card-header-tabs" id="criteria-tabs" role="tablist">
                        <li class="nav-item" role="presentation">
                            <button class="nav-link active" id="text-tab" data-bs-toggle="tab" data-bs-target="#text-content" type="button" role="tab" aria-controls="text-content" aria-selected="true">
                                Extracted Text
                            </button>
                        </li>
                        <li class="nav-item" role="presentation">
                            <button class="nav-link" id="json-tab" data-bs-toggle="tab" data-bs-target="#json-content" type="button" role="tab" aria-controls="json-content" aria-selected="false">
                                Generated JSON
                            </button>
                        </li>
                    </ul>
                </div>
                <div class="card-body">
                    <div class="tab-content" id="criteriaTabContent">
                        <div class="tab-pane fade show active" id="text-content" role="tabpanel" aria-labelledby="text-tab">
                            <div class="form-floating">
                                <textarea class="form-control" id="extracted-text" style="height: 200px" readonly>${data.extracted_text}</textarea>
                                <label for="extracted-text">Extracted Text from Document</label>
                            </div>
                        </div>
                        <div class="tab-pane fade" id="json-content" role="tabpanel" aria-labelledby="json-tab">
                            <pre id="job-criteria-json" class="bg-light p-3 rounded" style="max-height: 200px; overflow-y: auto;">${JSON.stringify(data.job_criteria, null, 2)}</pre>
                        </div>
                    </div>
                    
                    <div class="d-grid gap-2 mt-3">
                        <button id="update-criteria-btn" class="btn btn-primary">
                            <i class="fas fa-save me-2"></i> Update Job Criteria
                        </button>
                    </div>
                </div>
            </div>
        `;
    }

    function updateJobCriteria(jobCriteria) {
        fetch('/job-criteria/update', {
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
                successDiv.className = 'alert alert-success mt-3';
                successDiv.innerHTML = 'Job criteria updated successfully!';
                jobCriteriaPreview.appendChild(successDiv);
                
                setTimeout(() => {
                    if (successDiv.parentNode) {
                        successDiv.parentNode.removeChild(successDiv);
                    }
                }, 5000);
            } else {
                const errorDiv = document.createElement('div');
                errorDiv.className = 'alert alert-danger mt-3';
                errorDiv.innerHTML = `Failed to update job criteria: ${data.error || 'Unknown error'}`;
                jobCriteriaPreview.appendChild(errorDiv);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            const errorDiv = document.createElement('div');
            errorDiv.className = 'alert alert-danger mt-3';
            errorDiv.innerHTML = `Error: ${error.message || 'An unexpected error occurred'}`;
            jobCriteriaPreview.appendChild(errorDiv);
        });
    }
});