# Manual Start Instructions

If the automated script doesn't work, follow these steps manually:

## Terminal 1: Backend

```bash
# 1. Install system dependencies (run once)
sudo apt install -y python3-venv python3-pip

# 2. Create virtual environment
cd /home/mahad/PROJECTS/PersonalProjects/Mockups_Generator
python3 -m venv venv

# 3. Activate virtual environment
source venv/bin/activate

# 4. Install Python dependencies
cd backend
pip install -r requirements.txt

# 5. Run database migrations
python -m alembic upgrade head

# 6. Create upload directories
mkdir -p ../uploads/{products,mockups,refinements,exports,logos}

# 7. Start backend server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Keep this terminal running.

## Terminal 2: Frontend

Open a new terminal window and run:

```bash
cd /home/mahad/PROJECTS/PersonalProjects/Mockups_Generator/frontend
npm run dev
```

Keep this terminal running too.

## Access the App

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

## To Stop

Press `Ctrl+C` in both terminals.
