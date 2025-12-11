# MockupAI - Quick Start Guide

## 🚀 Quick Start (Easiest Method)

### 1. Install System Prerequisites (One-time setup)

```bash
# Install Python venv and pip
sudo apt update
sudo apt install -y python3-venv python3-pip
```

### 2. Start the Application

```bash
cd /home/mahad/PROJECTS/PersonalProjects/Mockups_Generator
./start-dev.sh
```

This script will automatically:
- ✅ Create a virtual environment
- ✅ Install all Python dependencies
- ✅ Run database migrations
- ✅ Start the backend server (port 8000)
- ✅ Start the frontend server (port 3000)

### 3. Access the Application

- **Frontend (Main App)**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

### 4. Stop the Application

```bash
./stop-dev.sh
```

Or press `Ctrl+C` in the terminal running the servers.

---

## 📋 Manual Setup (Alternative)

If you prefer to run things manually:

### Backend Setup

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
cd backend
pip install -r requirements.txt

# 3. Run migrations
python -m alembic upgrade head

# 4. Start backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Setup (in a new terminal)

```bash
cd frontend
npm run dev
```

---

## 🎨 Features Available

### Phase 1-8 (Completed):
- ✅ Product upload with background removal
- ✅ AI mockup generation with 25+ scene templates
- ✅ Conversational AI refinement
- ✅ Batch generation with variations
- ✅ Platform-specific exports
- ✅ Brand DNA system
- ✅ Context-aware scene suggestions
- ✅ Smart compositing with lighting
- ✅ User system with tiers

### Phase 9 (Canvas Editor - Just Completed!):
- ✅ Full Fabric.js canvas editor
- ✅ Layer management
- ✅ Image adjustments (brightness, contrast, saturation, blur)
- ✅ Undo/redo functionality
- ✅ Auto-save drafts
- ✅ Keyboard shortcuts

---

## 🔑 Environment Variables

The `.env` file is already configured with:
- ✅ Gemini API key (for AI generation)
- ✅ SQLite database (no setup needed)
- ✅ Local file storage (no S3 needed)

For production, you may want to configure:
- PostgreSQL database
- Redis for caching
- S3/R2 for file storage
- Stripe for payments

---

## 🐛 Troubleshooting

### Backend won't start?
```bash
# Check the logs
tail -f backend.log

# Common issues:
# - Missing dependencies: pip install -r backend/requirements.txt
# - Port 8000 in use: lsof -i :8000 (then kill the process)
```

### Frontend won't start?
```bash
# Check the logs
tail -f frontend.log

# Common issues:
# - Port 3000 in use: lsof -i :3000 (then kill the process)
# - Missing node modules: cd frontend && npm install
```

### Database issues?
```bash
# Reset the database
rm mockupai.db
cd backend && python -m alembic upgrade head
```

---

## 📱 Test the Application

### 1. Upload a Product
- Go to http://localhost:3000
- Click "Upload Product"
- Upload a product image (e.g., a bottle, phone, or package)

### 2. Generate Mockups
- Select a scene template
- Click "Generate Mockup"
- Wait for AI to generate the mockup

### 3. Edit in Canvas Editor
- Click on a generated mockup
- Click "Edit" to open the canvas editor
- Try adding text, shapes, or adjusting colors
- Use keyboard shortcuts: Ctrl+Z (undo), Ctrl+S (save)

### 4. Export
- Export mockups in various platform presets
- Download individual mockups or batch export

---

## 🎯 Next Steps

- **Phase 10**: Public API & Integrations (Coming soon)
- Shopify app integration
- Figma plugin
- WordPress plugin

---

## 📚 Documentation

- Full documentation: See `claude.md`
- API documentation: http://localhost:8000/docs (when running)
- Architecture: See project structure in `claude.md`

---

## 💡 Tips

1. **Use keyboard shortcuts** in the canvas editor for faster editing
2. **Create brand profiles** for consistent styling across mockups
3. **Use batch generation** to create multiple variations at once
4. **Try conversational refinement** to adjust mockups with natural language

---

## 🆘 Need Help?

- Check `backend.log` and `frontend.log` for errors
- Review the API docs at http://localhost:8000/docs
- Check the git history for recent changes
- Review `claude.md` for detailed implementation notes

Happy mocking! 🎨✨
