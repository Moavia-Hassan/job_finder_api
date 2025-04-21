// DOM elements
const jobSearchForm = document.getElementById('jobSearchForm');
const searchButton = document.getElementById('searchButton');
const progressSection = document.getElementById('progressSection');
const resultsSection = document.getElementById('resultsSection');
const errorAlert = document.getElementById('errorAlert');
const progressBar = document.getElementById('progressBar');
const currentStep = document.getElementById('currentStep');
const progressPercent = document.getElementById('progressPercent');
const statusMessage = document.getElementById('statusMessage');
const resultsContainer = document.getElementById('resultsContainer');
const jobCount = document.getElementById('jobCount');

// State variables
let isSearching = false;
let statusCheckInterval = null;
let lastProgress = 0;

// Add event listeners
document.addEventListener('DOMContentLoaded', () => {
    jobSearchForm.addEventListener('submit', handleFormSubmit);
});

// Handle form submission
async function handleFormSubmit(event) {
    event.preventDefault();
    
    if (isSearching) return;
    
    // Reset previous results
    resetUI();
    
    // Collect form data
    const formData = new FormData(jobSearchForm);
    
    try {
        // Show loading state
        isSearching = true;
        searchButton.disabled = true;
        searchButton.innerHTML = '<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Searching...';
        progressSection.classList.remove('d-none');
        
        // Submit search request
        const response = await fetch('/api/search', {
            method: 'POST',
            body: formData
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to start job search');
        }
        
        // Start checking status
        startStatusCheck();
        
    } catch (error) {
        showError(error.message);
        resetSearchState();
    }
}

// Check status periodically
function startStatusCheck() {
    // First check quickly (200ms)
    statusCheckInterval = setInterval(checkStatus, 200);
    
    // After 2 seconds, slow down to check every 500ms
    setTimeout(() => {
        clearInterval(statusCheckInterval);
        statusCheckInterval = setInterval(checkStatus, 500);
    }, 2000);
}

// Check current status of the job search
async function checkStatus() {
    try {
        const response = await fetch('/api/status');
        const data = await response.json();
        
        // Update progress UI
        updateProgressUI(data);
        
        // If finished, show results
        if (!data.is_scraping) {
            clearInterval(statusCheckInterval);
            fetchResults();
        }
        
    } catch (error) {
        showError('Error checking status: ' + error.message);
        resetSearchState();
        clearInterval(statusCheckInterval);
    }
}

// Fetch results when job search is complete
async function fetchResults() {
    try {
        const response = await fetch('/api/results');
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.error || 'Failed to fetch results');
        }
        
        const results = await response.json();
        displayResults(results);
        
    } catch (error) {
        showError(error.message);
    } finally {
        resetSearchState();
    }
}

// Update progress UI
function updateProgressUI(status) {
    // Set current step text
    currentStep.textContent = status.current_step;
    
    // Smoothly update progress bar if it's changed
    if (status.progress !== lastProgress) {
        // Animate the progress bar change
        animateProgressBar(lastProgress, status.progress);
        lastProgress = status.progress;
    }
    
    if (status.message) {
        statusMessage.textContent = status.message;
    }
    
    if (status.error) {
        showError(status.error);
        clearInterval(statusCheckInterval);
        resetSearchState();
    }
}

// Animates the progress bar from start to end value
function animateProgressBar(startValue, endValue) {
    const duration = 300; // milliseconds
    const startTime = performance.now();
    
    function updateProgress(currentTime) {
        const elapsedTime = currentTime - startTime;
        const progress = Math.min(elapsedTime / duration, 1);
        
        // Calculate current value using easing function
        const currentValue = startValue + (endValue - startValue) * progress;
        
        // Update progress bar
        progressBar.style.width = `${currentValue}%`;
        progressBar.setAttribute('aria-valuenow', currentValue);
        progressPercent.textContent = `${Math.round(currentValue)}%`;
        
        // Continue animation if not finished
        if (progress < 1) {
            requestAnimationFrame(updateProgress);
        }
    }
    
    requestAnimationFrame(updateProgress);
}

// Display job results
function displayResults(jobs) {
    resultsSection.classList.remove('d-none');
    
    // Update job count
    const jobsCount = Array.isArray(jobs) ? jobs.length : 0;
    jobCount.textContent = `${jobsCount} jobs`;
    
    // Clear previous results
    resultsContainer.innerHTML = '';
    
    // If no jobs found
    if (!jobs || jobsCount === 0) {
        resultsContainer.innerHTML = `
            <div class="col-12 text-center py-5">
                <i class="bi bi-search" style="font-size: 3rem; color: #ccc;"></i>
                <h4 class="mt-3">No matching jobs found</h4>
                <p class="text-muted">Try adjusting your search criteria</p>
            </div>
        `;
        return;
    }
    
    // Add each job card
    jobs.forEach(job => {
        const companyInitial = job.company_name ? job.company_name.charAt(0) : 
                              (job.company ? job.company.charAt(0) : '?');
        
        const jobTitle = job.job_title || job.title || 'Unknown Title';
        const company = job.company_name || job.company || 'Unknown Company';
        const location = job.location || 'Not specified';
        const salary = job.salary || 'Not specified';
        const jobType = job.job_type || 'Not specified';
        const description = job.description || job.job_description || 'No description available';
        const applyLink = job.apply_link || '#';
        
        const jobCard = document.createElement('div');
        jobCard.className = 'col-md-6';
        jobCard.innerHTML = `
            <div class="card job-card h-100 shadow-sm">
                <div class="card-body">
                    <div class="d-flex mb-3">
                        <div class="company-logo me-3">
                            ${companyInitial}
                        </div>
                        <div>
                            <h5 class="card-title mb-1">${jobTitle}</h5>
                            <div class="text-muted">${company}</div>
                        </div>
                    </div>
                    
                    <div class="mb-3">
                        <span class="badge badge-job-type me-2">${jobType}</span>
                        <span class="badge badge-job-type badge-location me-2">
                            <i class="bi bi-geo-alt"></i> ${location}
                        </span>
                        <span class="badge badge-job-type badge-salary">
                            <i class="bi bi-cash"></i> ${salary}
                        </span>
                    </div>
                    
                    <p class="card-text job-description mb-3">${description}</p>
                    
                    <a href="${applyLink}" target="_blank" class="btn btn-sm btn-primary apply-btn">
                        <i class="bi bi-box-arrow-up-right"></i> Apply Now
                    </a>
                </div>
            </div>
        `;
        
        resultsContainer.appendChild(jobCard);
    });
}

// Show error message
function showError(message) {
    errorAlert.textContent = message;
    errorAlert.classList.remove('d-none');
}

// Reset search state
function resetSearchState() {
    isSearching = false;
    searchButton.disabled = false;
    searchButton.innerHTML = '<i class="bi bi-search"></i> Search Jobs';
}

// Reset UI elements
function resetUI() {
    errorAlert.textContent = '';
    errorAlert.classList.add('d-none');
    progressBar.style.width = '0%';
    progressBar.setAttribute('aria-valuenow', 0);
    currentStep.textContent = 'Initializing...';
    progressPercent.textContent = '0%';
    statusMessage.textContent = '';
    resultsSection.classList.add('d-none');
    resultsContainer.innerHTML = '';
    lastProgress = 0;
    
    if (statusCheckInterval) {
        clearInterval(statusCheckInterval);
    }
} 