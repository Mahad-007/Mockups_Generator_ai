# MockupAI

Upload a product photo and get product mockups that look like they were shot in a real scene. MockupAI removes the background, uses Gemini to pick scenes that suit the product and composites the product into them. You can then adjust the result in a canvas editor and export it in the sizes you need.

## Features

- **Background removal** with `rembg`
- **Scene suggestions**: Gemini looks at the product and suggests settings that fit it
- **Mockup generation**: composites the product into a scene with matching lighting and shadows
- **Chat refinement**: describe changes in plain language ("warmer light", "put it on marble")
- **Batch generation**: run many scene and variation combinations as a background job and track its progress
- **Brand kits**: save your colors and logo, and pull brand colors from a logo or a website URL
- **Canvas editor** (Fabric.js) with layers, adjustments, undo and redo, and autosave
- **Export presets** for Instagram (post, story, reel cover), Amazon (main and lifestyle) and other sizes, either one at a time or in batches
- Accounts with JWT auth, plus teams

## Stack

| | |
| --- | --- |
| Frontend | Next.js 14, TypeScript, Tailwind, shadcn/ui, Fabric.js, Zustand, NextAuth |
| Backend | FastAPI, SQLAlchemy (async), Alembic, Pydantic |
| AI and images | Google Gemini (`gemini-2.0-flash-exp`), rembg, Pillow |
| Storage | SQLite and a local `uploads/` folder by default |

## Running it locally

You need Python 3.10+, Node 18+ and a [Gemini API key](https://aistudio.google.com/app/apikey).

```bash
git clone https://github.com/Mahad-007/Mockups_Generator_ai.git
cd Mockups_Generator_ai
cp backend/.env.example backend/.env   # add GEMINI_API_KEY
./start-dev.sh
```

`start-dev.sh` creates a virtualenv, installs dependencies, runs the migrations and starts both servers:

- App: http://localhost:3000
- API: http://localhost:8000
- API docs (Swagger): http://localhost:8000/docs

Run `./stop-dev.sh` to stop everything. To run the steps by hand instead, see [QUICKSTART.md](QUICKSTART.md) and [MANUAL_START.md](MANUAL_START.md).

## API overview

All routes are under `/api/v1`:

| Group | What it does |
| --- | --- |
| `/products` | Upload products and remove backgrounds |
| `/scenes` | Scene templates and AI suggestions |
| `/mockups` | Generate and list mockups |
| `/chat` | Refine a mockup through conversation |
| `/batch` | Batch jobs, their status and results |
| `/brands` | Brand kits and logo upload |
| `/exports` | Single, batch and multi-preset export |
| `/auth`, `/users`, `/teams` | Accounts and teams |

## Tests

```bash
cd backend && pytest
```
