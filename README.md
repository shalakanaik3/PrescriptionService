# 🏥 HMS Prescription Microservice

A robust, containerized microservice built for the Hospital Management System (HMS). This module handles prescription lifecycle management, data persistence, and provides an integrated dashboard for medical staff.

## 🚀 Key Features

* **Microservice Architecture:** Independent service with its own isolated SQLite database (Database-per-service pattern).
* **Automated Data Seeding:** Automatically populates the database with 220 records from the `hms_prescriptions_indian.csv` dataset upon startup.
* **Standardized API:** Follows OpenAPI 3.0 specs with versioned endpoints (`/v1/`).
* **Security & Compliance:** Implements **PII Masking** for `patient_id` in system logs to protect sensitive data.
* **Resilience:** Includes standard error response structures and `correlationId` tracking for distributed tracing.
* **Integrated UI:** A built-in Bootstrap dashboard for real-time prescription creation and viewing.

---

## 🛠️ Tech Stack

- **Backend:** Python 3.14 + FastAPI
- **Database:** SQLAlchemy + SQLite
- **Frontend:** Jinja2 Templates + Bootstrap 5
- **Containerization:** Docker & Kubernetes (Minikube)
- **Data Handling:** Pandas

---

## 🏃 Getting Started

### Prerequisites
- Docker Desktop
- Python 3.9+ (if running locally)

### Option 1: Running with Docker (Recommended)
1. Build the image:
   ```bash
   docker build -t prescription-service .
   ```
2. Run the container:
   ```bash
   docker run -d -p 8000:8000 --name hms-prescription-service prescription-service
   ```

### Option 2: Running Locally
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Start the server:
   ```bash
   python -m uvicorn main:app --port 8000
   ```

---

## 📊 API Access & Testing

Once the service is running, you can access:

| Endpoint | Description |
| :--- | :--- |
| `http://localhost:8000/` | **User Dashboard** (Frontend UI) |
| `http://localhost:8000/docs` | **Swagger UI** (API Documentation) |
| `GET /v1/prescriptions` | Retrieve all prescription records |
| `POST /v1/prescriptions` | Create a new prescription |

---

## 🔐 Compliance & Standards

### PII Masking Example
System logs are configured to mask sensitive identifiers. 
**Actual Log Output:**
`{"timestamp": "2026-05-02...", "message": "Prescription Created", "data": {"patient_id": "***", "medication": "Paracetamol"}}`

### Error Structure
All errors follow the mandated project structure:
```json
{
  "code": "INVALID_APPOINTMENT",
  "message": "Prescription must be linked to a valid appointment",
  "correlationId": "REQ-12345"
}
```

---

## 📂 Project Structure
```text
prescription-service/
├── main.py              # Application logic & API routes
├── templates/           # Frontend HTML files
│   └── index.html       # Dashboard UI
├── Dockerfile           # Container configuration
├── k8s-manifest.yaml    # Kubernetes deployment & service
├── requirements.txt     # Python dependencies
└── hms_prescriptions_indian.csv # Seed data
```