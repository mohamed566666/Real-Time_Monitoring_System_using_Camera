# Real-Time Monitoring System

A powerful real-time face recognition monitoring system built with FastAPI and modern deep learning techniques. This system provides comprehensive APIs for user management, department organization, device monitoring, and face recognition capabilities.

## 📋 Prerequisites

- **Python**: Version 3.8 or higher
- **PostgreSQL**: Version 12 or higher

## 🚀 Technology Stack

- **Framework**: FastAPI (Python 3.8+)
- **Database**: PostgreSQL with SQLAlchemy ORM
- **AI/ML**: OpenCV, Face Recognition models (MobileFaceNet)

## 📁 Project Structure

├── server/
│ ├── app/
│ │ ├── application/ # Business logic layer
│ │ │ ├── services/ # Application services
│ │ │ └── usecases/ # Use cases implementation
│ │ ├── core/ # Core configurations
│ │ │ ├── config.py # Application settings
│ │ │ └── dependencies.py # Dependency injection
│ │ ├── domain/ # Domain layer
│ │ │ └── entities/ # Business entities
│ │ ├── infrastructure/ # External implementations
│ │ │ ├── aiModels/ # AI/ML models
│ │ │ ├── db/ # Database configurations
│ │ │ └── repositories/ # Data repositories
│ │ └── presentation/ # API layer
│ │ └── controllers/ # Route controllers
│ ├── models/ # Pre-trained models
│ └── requirements.txt # Python dependencies
└── README.md

## 🔧 Installation

### 1. Clone the Repository

### 2. Create Virtual Environment

# Windows

python -m venv venv
venv\Scripts\activate

# Linux/Mac

python3 -m venv venv
source venv/bin/activate

### 3. Install Dependencies

cd server
pip install -r requirements.txt

### 4. Download Model Files

Place the following model files in the server/models/ directory:

Face Detection Model:

deploy.prototxt

res10_300x300_ssd_iter_140000.caffemodel

Face Recognition Model:

MobileFaceNet/weights/mobilefacenet.onnx

### 5- Initialize Database

### 🏃‍♂️ Running the Application

uvicorn app.main:app --reload
