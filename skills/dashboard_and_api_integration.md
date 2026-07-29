# Dashboard and API Integration

## Overview
The **dashboard_and_api_integration** micro-skill focuses on creating a real-time HTML dashboard that visualizes data and integrates it with a Flask API to provide RESTful endpoints for data interaction and manipulation. This setup enables users to monitor file processing statuses, view statistics, and interact with the system through both the web interface and third-party applications.

## HTML Dashboard Generation

### Purpose
The HTML dashboard serves as a user-friendly interface to monitor the status of file processing tasks. It displays key statistics such as classification results, metadata, cloud storage status, and more. The dashboard supports automatic refreshing to reflect the latest processing results.

### Key Components and Structure
- **HTML Structure**: The dashboard is structured with a header, a container for statistics and panels, and a footer for additional information or actions.
- **Styling**: CSS is used to style the dashboard for a clean and responsive design.
- **Dynamic Updates**: JavaScript, along with libraries like Chart.js, is used to handle dynamic data updates and visualizations.

#### Example Code
```html
<!DOCTYPE html>
<html lang="zh-TW">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OCR Bot Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
    <style>
        /* CSS styles for the dashboard */
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
        }
        header {
            background-color: #333;
            color: #fff;
            padding: 1em;
        }
        .container {
            padding: 1em;
        }
        .stats-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 1em;
        }
        .panel {
            border: 1px solid #ccc;
            padding: 1em;
        }
    </style>
</head>
<body>
    <header>
        <h1>OCR Bot Dashboard</h1>
        <div class="actions">
            <!-- Action buttons for user interactions -->
        </div>
    </header>
    <div class="container">
        <!-- Statistics grid -->
        <div class="stats-grid">
            <!-- Stat cards displaying key metrics -->
            <div class="stat-card">
                <h2>Total Files Processed</h2>
                <p id="total-files">0</p>
            </div>
            <div class="stat-card">
                <h2>Classification Accuracy</h2>
                <p id="accuracy">0%</p>
            </div>
            <!-- Add more stat cards as needed -->
        </div>
        <!-- Panels -->
        <div class="grid-2">
            <!-- Document list -->
            <div class="panel">
                <h2>Document List</h2>
                <table id="document-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Name</th>
                            <th>Status</th>
                        </tr>
                    </thead>
                    <tbody>
                        <!-- Document rows will be populated dynamically -->
                    </tbody>
                </table>
            </div>
            <!-- Upload form -->
            <div class="panel">
                <h2>Upload Document</h2>
                <form id="upload-form" enctype="multipart/form-data">
                    <input type="file" name="file">
                    <button type="submit">Upload</button>
                </form>
            </div>
        </div>
    </div>
    <script>
        // JavaScript for dynamic updates
        document.getElementById('upload-form').addEventListener('submit', function(e) {
            e.preventDefault();
            const fileInput = document.querySelector('input[type="file"]');
            const formData = new FormData();
            formData.append('file', fileInput.files[0]);

            fetch('/api/process', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                // Handle success
                alert('File uploaded successfully!');
                // Refresh stats and document list
                fetchStatsStats();
                fetchDocumentList();
            })
            .catch(error => {
                console.error('Error uploading file:', error);
                alert('Error uploading file.');
            });
        });

        function fetchStats() {
            fetch('/api/stats')
            .then(response => response.json())
            .then(data => {
                document.getElementById('total-files').textContent = data.total_files;
                document.getElementById('accuracy').textContent = data.accuracy + '%';
                // Update other stats as needed
            })
            .catch(error => {
                console.error('Error fetching stats:', error);
            });
        }

        function fetchDocumentList() {
            fetch('/api/docs')
            .then(response => response.json())
            .then(data => {
                const tableBody = document.querySelector('#document-table tbody');
                tableBody.innerHTML = '';
                data.docs.forEach(doc => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${doc.id}</td>
                        <td>${doc.name}</td>
                        <td>${doc.status}</td>
                    `;
                    tableBody.appendChild(row);
                });
            })
            .catch(error => {
                console.error('Error fetching document list:', error);
            });
        }

        // Initial data fetch
        fetchStats();
        fetchDocumentList();

        // Health check
        fetch('/api/health')
        .then(response => response.json())
        .then(data => {
            if (data.status !== 'ok') {
                console.error('Health check failed');
            }
        })
        .catch(error => {
            console.error('Health check error:', error);
        });
    </script>
</body>
</html>
```

### Common Errors and Prevention
- **Error**: The dashboard fails to update in real-time or displays incorrect data.
- **Prevention**: Use JavaScript for dynamic data updates and ensure the backend API provides accurate statistics. Implement error handling to catch and manage any issues during data fetching.

## Flask API Integration

### Purpose
The Flask API integrates with the file processing pipeline to provide RESTful endpoints for uploading files, querying processing statuses, and retrieving statistical data. This setup allows users to interact with the file processing system through the web interface or third-party applications.

### Key Components and Structure
- **Endpoints**:
  - `POST /api/process`: Uploads and processes a file.
  - `GET /api/stats`: Retrieves statistical data.
  - `GET /api/docs`: Retrieves a list of documents.
  - `GET /api/health`: Checks the health status of the API.
- **Flask Application**: The Flask application is configured to run on a specified host and port, enabling it to handle incoming requests.

#### Example Code
```python
from flask import Flask, request, jsonify
from pipeline import Pipeline

app = Flask(__name__)

@app.route('/api/process', methods=['POST'])
def process_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    pipeline = Pipeline()
    result = pipeline.process_file(file)
    return jsonify(result), 200

@app.route('/api/stats', methods=['GET'])
def get_stats():
    pipeline = Pipeline()
    stats = pipeline.get_stats()
    return jsonify(stats), 200

@app.route('/api/docs', methods=['GET'])
def get_docs():
    pipeline = Pipeline()
    docs = pipeline.get_docs()
    return jsonify(docs), 200

@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8865)
```

### Common Errors and Prevention
- **Error**: API endpoints fail to work or return incorrect data.
- **Prevention**: Conduct thorough testing to ensure each endpoint can handle requests correctly and return accurate data. Implement validation for incoming requests to prevent errors due to missing or malformed data.

## Integration Tips
- **Data Consistency**: Ensure that the data displayed on the dashboard is consistent with the data provided by the API. Use caching mechanisms if necessary to improve performance.
- **Security**: Implement authentication and authorization mechanisms to secure the API endpoints. Use HTTPS to encrypt data in transit.
- **Scalability**: Design the system to handle increased load by using scalable infrastructure and efficient data processing pipelines.
- **Error Handling**: Implement comprehensive error handling in both the frontend and backend to provide meaningful feedback to users and facilitate debugging.

## Conclusion
By integrating a real-time HTML dashboard with a Flask API, you can create a robust system for visualizing and interacting with data. This setup not only enhances user experience but also provides a flexible interface for developers to build upon.