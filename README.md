# Plant Management System

A web application for managing and tracking plant care, including watering schedules, sunlight requirements, and plant characteristics.

## Features

- Plant information tracking
- Watering schedule management
- Sunlight requirements
- Plant characteristics (attracts birds, butterflies, etc.)

## Tech Stack

- Frontend: React with TypeScript, Vite
- Backend: Flask (Python)
- Database: MySQL

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   Create a `.env` file with the following variables:
   ```
   MYSQL_HOST=localhost
   MYSQL_USER=your_username
   MYSQL_PASSWORD=your_password
   MYSQL_DB=plant_database
   ```

5. Run the backend:
   ```bash
   python app.py
   ```

### Frontend Setup

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the development server:
   ```bash
   npm run dev
   ```

## API Endpoints

- `GET /api/plants/<plant_id>/attracts` - Get plant attraction information
- `GET /api/plants/<plant_id>/sunlight` - Get plant sunlight requirements

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request 