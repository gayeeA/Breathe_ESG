# Breathe ESG Prototype

A Django REST backend and React review dashboard for ingesting SAP fuel/procurement, utility electricity, and corporate travel export data.

## Run locally

1. Backend
   - Activate the Python environment and install dependencies:
     ```powershell
     cd c:\Users\HP\OneDrive\Desktop\project
     .venv\Scripts\python.exe -m pip install -r backend\requirements.txt
     .venv\Scripts\python.exe backend\manage.py migrate
     .venv\Scripts\python.exe backend\manage.py runserver
     ```

2. Frontend
   - Install Node packages and start Vite:
     ```powershell
     cd c:\Users\HP\OneDrive\Desktop\project\frontend
     npm install
     npm run dev
     ```

3. Use the web app
   - Open `http://localhost:5173` and upload CSV samples to `POST /api/imports/upload/`.
   - The review dashboard will show pending normalized rows and allow approval.

Sample import files:
   - `sample_data/sap_fuel.csv` — SAP fuel/procurement export with plant codes, quantities, and optional CO2 values.
   - `sample_data/utility_electricity.csv` — Utility electricity bill export with billing periods and meter usage.
   - `sample_data/travel_corporate.csv` — Corporate travel export with flights, hotels, and ground transport.

How to test end-to-end
   1. Start the backend and frontend locally.
   2. Open `http://localhost:5173`.
   3. Choose a source type and upload one of the sample files from `sample_data/`.
   4. Review the pending rows, inspect suspicious flags, and approve records.
# Sample data usage

This folder contains example CSV files for a realistic ESG import workflow.

## Files included
- `sap_fuel.csv` — SAP fuel/procurement export sample
- `utility_electricity.csv` — utility electricity bill export sample
- `travel_corporate.csv` — corporate travel expense export sample

## How to run

### Backend
From the repository root:
```powershell
cd c:\Users\HP\OneDrive\Desktop\project\backend
..\.venv\Scripts\python.exe manage.py runserver 8000
```

### Frontend
From the repository root:
```powershell
cd c:\Users\HP\OneDrive\Desktop\project\frontend
npm run dev -- --host 0.0.0.0 --port 5173
```

## Testing imports
1. Open the frontend at `http://localhost:5173/`.
2. Choose a source type.
3. Upload one of the sample CSV files from this folder.
4. Review pending records in the dashboard and approve them.
