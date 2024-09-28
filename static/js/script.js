document.addEventListener('DOMContentLoaded', (event) => {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('file-input');
    const errorMessage = document.getElementById('error-message');
    const loadingSpinner = document.getElementById('loading-spinner');

    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropZone.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropZone.addEventListener(eventName, unhighlight, false);
    });

    function highlight(e) {
        dropZone.classList.add('dragover');
    }

    function unhighlight(e) {
        dropZone.classList.remove('dragover');
    }

    dropZone.addEventListener('drop', handleDrop, false);
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', handleFiles);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        handleFiles({ target: { files: files } });
    }

    function handleFiles(e) {
        const files = e.target.files;
        if (files.length > 0) {
            const file = files[0];
            if (validateFile(file)) {
                uploadFile(file);
            } else {
                showError('Please upload only Excel (.xlsx, .xls) or CSV files.');
            }
        }
    }

    function validateFile(file) {
        const allowedExtensions = ['csv', 'xlsx', 'xls'];
        const fileExtension = file.name.split('.').pop().toLowerCase();
        return allowedExtensions.includes(fileExtension);
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        hideLoadingSpinner();
    }

    function showLoadingSpinner() {
        loadingSpinner.style.display = 'flex';
    }

    function hideLoadingSpinner() {
        loadingSpinner.style.display = 'none';
    }

    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);

        showLoadingSpinner();

        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            hideLoadingSpinner();

            if (!response.ok) {
                return response.json().then(err => { throw err; });
            }
            return response.text();
        })
        .then(html => {
            document.open();
            document.write(html);
            document.close();
        })
        .catch(error => {
            showError(error.error || 'An error occurred while uploading the file.');
        });
    }
});