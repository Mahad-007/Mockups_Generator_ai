# MockupAI - Product Mockup Generator

## Project Overview

An AI-powered product mockup generator that uses Google's Gemini API to create professional, contextual product mockups. Users upload product images and receive realistic mockups placed in appropriate scenes with proper lighting, shadows, and reflections.

---

## Tech Stack

| Layer | Technology | Rationale |
|-------|------------|-----------|
| **Frontend** | Next.js 14 (App Router) | SSR, great DX, React ecosystem |
| **Styling** | Tailwind CSS + shadcn/ui | Rapid UI development, consistent design |
| **Canvas Editor** | Fabric.js | Client-side image manipulation |
| **Backend** | FastAPI (Python) | Async, fast, excellent for AI workloads |
| **AI/ML** | Gemini API (2.0 Flash, Imagen 3) | Multimodal, image generation |
| **Image Processing** | Pillow, rembg, OpenCV | Background removal, compositing |
| **Database** | PostgreSQL + SQLAlchemy | Reliable, scalable |
| **Cache** | Redis | Session management, rate limiting |
| **Storage** | AWS S3 / Cloudflare R2 | Image storage |
| **Auth** | NextAuth.js + JWT | Flexible authentication |
| **Deployment** | Docker + Railway/Vercel | Easy scaling |

---

## Project Structure

```
Mockups_Generator/
├── claude.md                    # This file - implementation guide
├── docker-compose.yml           # Local development setup
├── .env.example                 # Environment variables template
│
├── backend/                     # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Settings and configuration
│   │   │
│   │   ├── api/                 # API Routes
│   │   │   ├── __init__.py
│   │   │   ├── v1/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── router.py    # Main v1 router
│   │   │   │   ├── mockups.py   # Mockup generation endpoints
│   │   │   │   ├── products.py  # Product upload/management
│   │   │   │   ├── scenes.py    # Scene templates
│   │   │   │   ├── brands.py    # Brand management
│   │   │   │   ├── exports.py   # Export endpoints
│   │   │   │   └── chat.py      # Conversational refinement
│   │   │   └── deps.py          # Dependencies (auth, db)
│   │   │
│   │   ├── core/                # Core business logic
│   │   │   ├── __init__.py
│   │   │   ├── gemini.py        # Gemini API client
│   │   │   ├── image_processor.py   # Image manipulation
│   │   │   ├── background_remover.py # BG removal logic
│   │   │   ├── scene_generator.py   # Scene generation
│   │   │   ├── compositor.py    # Image compositing
│   │   │   ├── brand_extractor.py   # Brand DNA extraction
│   │   │   └── export_optimizer.py  # Platform-specific exports
│   │   │
│   │   ├── models/              # Database models
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── mockup.py
│   │   │   ├── brand.py
│   │   │   └── scene_template.py
│   │   │
│   │   ├── schemas/             # Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── user.py
│   │   │   ├── product.py
│   │   │   ├── mockup.py
│   │   │   ├── brand.py
│   │   │   └── generation.py
│   │   │
│   │   ├── services/            # Business services
│   │   │   ├── __init__.py
│   │   │   ├── mockup_service.py
│   │   │   ├── product_service.py
│   │   │   ├── brand_service.py
│   │   │   └── export_service.py
│   │   │
│   │   └── utils/               # Utilities
│   │       ├── __init__.py
│   │       ├── storage.py       # S3/R2 operations
│   │       ├── rate_limiter.py
│   │       └── helpers.py
│   │
│   ├── tests/                   # Backend tests
│   ├── requirements.txt
│   ├── Dockerfile
│   └── alembic/                 # Database migrations
│
├── frontend/                    # Next.js Frontend
│   ├── app/
│   │   ├── layout.tsx           # Root layout
│   │   ├── page.tsx             # Landing page
│   │   ├── (auth)/
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   ├── dashboard/
│   │   │   ├── page.tsx         # User dashboard
│   │   │   └── layout.tsx
│   │   ├── generate/
│   │   │   └── page.tsx         # Main generation interface
│   │   ├── editor/
│   │   │   └── [id]/page.tsx    # Mockup editor
│   │   ├── brands/
│   │   │   └── page.tsx         # Brand management
│   │   └── api/                 # API routes (NextAuth, etc.)
│   │
│   ├── components/
│   │   ├── ui/                  # shadcn/ui components
│   │   ├── layout/
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── Footer.tsx
│   │   ├── upload/
│   │   │   ├── ProductUploader.tsx
│   │   │   └── DragDropZone.tsx
│   │   ├── generation/
│   │   │   ├── SceneSelector.tsx
│   │   │   ├── StylePicker.tsx
│   │   │   ├── GenerationForm.tsx
│   │   │   └── ResultsGrid.tsx
│   │   ├── editor/
│   │   │   ├── CanvasEditor.tsx
│   │   │   ├── LayerPanel.tsx
│   │   │   └── ToolBar.tsx
│   │   ├── chat/
│   │   │   ├── ChatInterface.tsx
│   │   │   └── MessageBubble.tsx
│   │   └── export/
│   │       ├── ExportModal.tsx
│   │       └── PlatformPresets.tsx
│   │
│   ├── lib/
│   │   ├── api.ts               # API client
│   │   ├── utils.ts
│   │   └── constants.ts
│   │
│   ├── hooks/
│   │   ├── useGeneration.ts
│   │   ├── useCanvas.ts
│   │   └── useChat.ts
│   │
│   ├── stores/                  # Zustand stores
│   │   ├── generationStore.ts
│   │   └── editorStore.ts
│   │
│   ├── styles/
│   │   └── globals.css
│   │
│   ├── public/
│   │   └── templates/           # Preview images
│   │
│   ├── package.json
│   ├── tailwind.config.ts
│   ├── next.config.js
│   └── Dockerfile
│
└── shared/                      # Shared types/constants
    └── types/
        └── index.ts
```

---

## Feature Implementation Plan

### Phase 1: MVP Core (Foundation)

**Goal**: Upload product → Remove background → Generate 1 basic mockup

#### 1.1 Backend Setup
- [ ] Initialize FastAPI project with proper structure
- [ ] Set up PostgreSQL database connection
- [ ] Configure Alembic for migrations
- [ ] Create basic User, Product, Mockup models
- [ ] Set up S3/R2 storage integration
- [ ] Implement file upload endpoint

#### 1.2 Gemini API Integration
- [ ] Create Gemini API client wrapper
- [ ] Implement vision analysis for product detection
- [ ] Set up Imagen 3 for scene generation
- [ ] Create prompt templates for mockup generation
- [ ] Handle API errors and rate limiting

#### 1.3 Background Removal
- [ ] Integrate rembg library
- [ ] Implement edge refinement
- [ ] Add transparency handling
- [ ] Create fallback to Gemini vision for complex products

#### 1.4 Basic Scene Generation
- [ ] Create scene prompt builder
- [ ] Implement single scene generation
- [ ] Add product placement logic
- [ ] Generate basic shadows

#### 1.5 Frontend MVP
- [ ] Set up Next.js project with App Router
- [ ] Create landing page
- [ ] Build product upload component
- [ ] Implement generation flow
- [ ] Display generated mockup

---

### Phase 2: Scene Library & Templates

**Goal**: 20+ template scenes with basic customization

#### 2.1 Scene Template System
- [ ] Design scene template data structure
- [ ] Create SceneTemplate model and migrations
- [ ] Build template management API
- [ ] Implement template categories (lifestyle, studio, outdoor, etc.)

#### 2.2 Pre-built Scene Library
- [ ] Create 20+ scene prompts covering:
  - Studio scenes (white, colored, gradient backgrounds)
  - Lifestyle scenes (desk, kitchen, bathroom, outdoor)
  - E-commerce scenes (Amazon-style, catalog)
  - Social media optimized scenes
  - Seasonal scenes (summer, winter, holiday)
- [ ] Generate preview thumbnails for each template
- [ ] Add scene tags and search functionality

#### 2.3 Basic Customization
- [ ] Add color customization for backgrounds
- [ ] Implement lighting direction controls
- [ ] Add surface material options (wood, marble, fabric)
- [ ] Create angle/perspective presets

#### 2.4 Frontend Scene Selector
- [ ] Build SceneSelector component with grid view
- [ ] Add category filtering
- [ ] Implement search functionality
- [ ] Create preview on hover
- [ ] Add "favorite templates" feature

---

### Phase 3: Conversational AI Refinement

**Goal**: Chat-based mockup refinement with multi-turn context

#### 3.1 Chat System Backend
- [ ] Create chat session management
- [ ] Implement conversation history storage
- [ ] Build context-aware prompt construction
- [ ] Create refinement instruction parser

#### 3.2 Gemini Conversational Integration
- [ ] Set up multi-turn conversation with Gemini
- [ ] Implement image-to-image refinement
- [ ] Create refinement prompt templates:
  - Lighting adjustments
  - Background changes
  - Color modifications
  - Style transfers
  - Element additions/removals
- [ ] Handle ambiguous requests gracefully

#### 3.3 Refinement Types
- [ ] "Make it warmer/cooler" - color temperature
- [ ] "Add morning light" - lighting changes
- [ ] "Change to wooden table" - surface changes
- [ ] "Make background blurry" - depth of field
- [ ] "Add plants/props" - element addition
- [ ] "Make it more minimal" - style adjustment
- [ ] "Center the product" - positioning

#### 3.4 Chat UI Components
- [ ] Build ChatInterface component
- [ ] Create message history display
- [ ] Add typing indicators
- [ ] Implement suggestion chips for common refinements
- [ ] Show before/after comparison
- [ ] Add "undo" functionality

---

### Phase 4: Batch Generation & Export

**Goal**: Generate multiple variations, platform-specific exports

#### 4.1 Batch Generation System
- [ ] Create batch job queue (Redis + Celery/ARQ)
- [ ] Implement parallel generation
- [ ] Add progress tracking
- [ ] Handle partial failures gracefully

#### 4.2 Variation Generation
- [ ] Generate 5-10 variations per request
- [ ] Vary:
  - Angles (front, 45°, side)
  - Lighting (soft, dramatic, natural)
  - Backgrounds (3-4 options)
  - Styles (minimal, lifestyle, premium)
- [ ] Implement seed control for reproducibility

#### 4.3 Export Optimizer
- [ ] Create platform presets:
  ```
  Instagram Post: 1080x1080
  Instagram Story: 1080x1920
  Amazon Main: 1000x1000 (white bg)
  Amazon Lifestyle: 1500x1500
  Website Hero: 1920x1080
  Facebook Ad: 1200x628
  Pinterest: 1000x1500
  Print (300dpi): Custom sizes
  ```
- [ ] Implement smart cropping
- [ ] Add format options (PNG, JPG, WebP)
- [ ] Create quality presets
- [ ] Generate zip for batch downloads

#### 4.4 Export UI
- [ ] Build ExportModal component
- [ ] Create platform preset selector
- [ ] Add custom size input
- [ ] Show preview before export
- [ ] Implement batch export progress

---

### Phase 5: Brand DNA Features

**Goal**: Brand consistency across all mockups

#### 5.1 Brand Profile System
- [ ] Create Brand model (colors, fonts, style, mood)
- [ ] Build brand CRUD API
- [ ] Implement brand-to-user association
- [ ] Add default brand per user

#### 5.2 Brand Extraction AI
- [ ] Extract colors from uploaded logos
- [ ] Analyze website URLs for brand style
- [ ] Detect brand mood (playful, professional, luxury, etc.)
- [ ] Generate brand description for prompts

#### 5.3 Brand-Aware Generation
- [ ] Inject brand colors into scene prompts
- [ ] Match lighting to brand mood
- [ ] Suggest on-brand scene templates
- [ ] Maintain style consistency across mockups

#### 5.4 Brand Management UI
- [ ] Build brand creation wizard
- [ ] Create color palette editor
- [ ] Add logo upload and analysis
- [ ] Show brand-influenced previews
- [ ] Enable brand switching per project

---

### Phase 6: Context-Aware Scene Suggestions

**Goal**: AI analyzes products and suggests relevant scenes

#### 6.1 Product Analysis
- [ ] Use Gemini Vision to analyze uploaded products
- [ ] Detect product category:
  - Electronics/Tech
  - Beauty/Skincare
  - Food/Beverage
  - Fashion/Apparel
  - Home/Furniture
  - Sports/Fitness
- [ ] Extract product attributes (color, size, material)
- [ ] Identify target audience hints

#### 6.2 Smart Recommendation Engine
- [ ] Map product categories to scene types
- [ ] Score scene relevance based on:
  - Product category match
  - Color harmony
  - Brand alignment
  - Trending scenes for category
- [ ] Return ranked scene suggestions

#### 6.3 Trending Scene Analysis
- [ ] Track popular scenes per category
- [ ] Integrate with design trend APIs/data
- [ ] Update recommendations based on season
- [ ] Show "trending in your industry" badge

#### 6.4 Suggestion UI
- [ ] Show AI-recommended scenes first
- [ ] Display relevance indicators
- [ ] Add "Why this scene?" explanations
- [ ] Allow feedback to improve suggestions

---

### Phase 7: Smart Product Masking & Compositing

**Goal**: Realistic product placement with proper shadows/reflections

#### 7.1 Advanced Background Removal
- [ ] Improve edge detection for complex products
- [ ] Handle transparent/glass products
- [ ] Process reflective surfaces (metal, glossy)
- [ ] Preserve product shadows when needed

#### 7.2 Intelligent Compositing
- [ ] Detect scene lighting direction
- [ ] Generate matching product shadows
- [ ] Add realistic reflections on surfaces
- [ ] Adjust product color for scene lighting
- [ ] Scale product appropriately for scene

#### 7.3 Perspective Matching
- [ ] Detect scene perspective
- [ ] Transform product to match
- [ ] Handle multiple products in scene
- [ ] Add depth-of-field effects

#### 7.4 Quality Enhancement
- [ ] Upscale final output
- [ ] Apply subtle noise matching
- [ ] Color grade to match scene
- [ ] Final polish pass

---

### Phase 8: User System & Scale

**Goal**: Full user management, history, subscriptions

#### 8.1 Authentication System
- [ ] Implement NextAuth.js with multiple providers:
  - Email/password
  - Google OAuth
  - GitHub OAuth
- [ ] Create user registration flow
- [ ] Add email verification
- [ ] Implement password reset

#### 8.2 User Dashboard
- [ ] Show generation history
- [ ] Display usage statistics
- [ ] List saved products
- [ ] Show brand profiles
- [ ] Recent mockups gallery

#### 8.3 Subscription System
- [ ] Define tier structure:
  ```
  Free: 5 mockups/month, basic scenes
  Pro ($19/mo): 100 mockups, all scenes, batch export
  Agency ($49/mo): Unlimited, API access, team seats
  ```
- [ ] Integrate Stripe for payments
- [ ] Implement usage tracking
- [ ] Add overage handling
- [ ] Create upgrade prompts

#### 8.4 Team Features (Agency Tier)
- [ ] Team creation and management
- [ ] Role-based permissions
- [ ] Shared brand profiles
- [ ] Shared template library
- [ ] Usage analytics per team member

---

### Phase 9: Canvas Editor

**Goal**: Client-side editing for fine-tuning mockups

#### 9.1 Fabric.js Integration
- [ ] Set up Fabric.js canvas
- [ ] Load generated mockup as base
- [ ] Add product layer management
- [ ] Implement zoom/pan controls

#### 9.2 Editing Tools
- [ ] Move/rotate/scale product
- [ ] Adjust layer order
- [ ] Crop and resize canvas
- [ ] Add text overlays
- [ ] Draw shapes/annotations

#### 9.3 Adjustment Controls
- [ ] Brightness/contrast
- [ ] Saturation/hue
- [ ] Shadow opacity
- [ ] Blur/sharpen

#### 9.4 Editor UI
- [ ] Build ToolBar component
- [ ] Create LayerPanel
- [ ] Add keyboard shortcuts
- [ ] Implement undo/redo history
- [ ] Auto-save drafts

---

### Phase 10: API & Integrations

**Goal**: Public API, third-party integrations

#### 10.1 Public API
- [ ] Design RESTful API for external use
- [ ] Create API key management
- [ ] Implement rate limiting per tier
- [ ] Write API documentation (OpenAPI/Swagger)
- [ ] Add webhook support for async generation

#### 10.2 Integrations
- [ ] Shopify app integration
- [ ] Figma plugin
- [ ] Canva integration
- [ ] WordPress plugin
- [ ] Zapier integration

#### 10.3 White-label Support
- [ ] Custom domain support
- [ ] Remove branding options
- [ ] Custom color themes
- [ ] Embedded widget

---

## API Endpoints Reference

### Products
```
POST   /api/v1/products/upload          # Upload product image
GET    /api/v1/products                  # List user's products
GET    /api/v1/products/{id}             # Get product details
DELETE /api/v1/products/{id}             # Delete product
```

### Mockups
```
POST   /api/v1/mockups/generate          # Generate single mockup
POST   /api/v1/mockups/batch             # Generate batch mockups
GET    /api/v1/mockups                   # List user's mockups
GET    /api/v1/mockups/{id}              # Get mockup details
DELETE /api/v1/mockups/{id}              # Delete mockup
POST   /api/v1/mockups/{id}/export       # Export mockup
```

### Chat/Refinement
```
POST   /api/v1/chat/sessions             # Create chat session
POST   /api/v1/chat/sessions/{id}/message # Send refinement message
GET    /api/v1/chat/sessions/{id}        # Get session history
```

### Scenes
```
GET    /api/v1/scenes/templates          # List scene templates
GET    /api/v1/scenes/templates/{id}     # Get template details
GET    /api/v1/scenes/suggestions        # Get AI suggestions for product
```

### Brands
```
POST   /api/v1/brands                    # Create brand profile
GET    /api/v1/brands                    # List user's brands
GET    /api/v1/brands/{id}               # Get brand details
PUT    /api/v1/brands/{id}               # Update brand
DELETE /api/v1/brands/{id}               # Delete brand
POST   /api/v1/brands/extract            # Extract brand from URL/logo
```

### Export
```
POST   /api/v1/export/single             # Export single mockup
POST   /api/v1/export/batch              # Export batch as zip
GET    /api/v1/export/presets            # Get platform presets
```

### Users
```
POST   /api/v1/auth/register             # Register new user
POST   /api/v1/auth/login                # Login
GET    /api/v1/users/me                  # Get current user
PUT    /api/v1/users/me                  # Update profile
GET    /api/v1/users/me/usage            # Get usage stats
```

---

## Environment Variables

```env
# Application
APP_ENV=development
APP_SECRET_KEY=your-secret-key
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/mockupai

# Redis
REDIS_URL=redis://localhost:6379

# Gemini API
GEMINI_API_KEY=your-gemini-api-key

# Storage (S3/R2)
S3_BUCKET_NAME=mockupai-uploads
S3_ACCESS_KEY=your-access-key
S3_SECRET_KEY=your-secret-key
S3_ENDPOINT_URL=https://...  # For R2

# Stripe (for subscriptions)
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# OAuth
GOOGLE_CLIENT_ID=...
GOOGLE_CLIENT_SECRET=...
```

---

## Development Commands

```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev

# Database
alembic upgrade head          # Run migrations
alembic revision --autogenerate -m "message"  # Create migration

# Docker
docker-compose up -d          # Start all services
docker-compose down           # Stop all services
```

---

## Current Implementation Status

- [x] Phase 1: MVP Core (Completed)
  - SQLite database with async SQLAlchemy
  - Product upload with background removal (rembg)
  - Gemini API integration for mockup generation
  - 20 scene templates
  - Local file storage
  - Frontend generation flow
- [ ] Phase 2: Scene Library
- [ ] Phase 3: Conversational AI
- [ ] Phase 4: Batch & Export
- [ ] Phase 5: Brand Features
- [ ] Phase 6: Context-Aware Suggestions
- [ ] Phase 7: Smart Compositing
- [ ] Phase 8: User System
- [ ] Phase 9: Canvas Editor
- [ ] Phase 10: API & Integrations

---

## Notes for Claude

When working on this project:
1. Always check this file for context on the project structure
2. Follow the phase order - each phase builds on previous ones
3. Use FastAPI best practices (dependency injection, Pydantic models)
4. Use Next.js App Router conventions
5. Keep Gemini API calls abstracted in the `core/gemini.py` module
6. Write tests for critical paths
7. Update this file's status checkboxes as features are completed
