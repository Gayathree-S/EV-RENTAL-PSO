# AI-Powered Smart EV Rental Management System

An Electric Vehicle (EV) rental booking platform that extends a grid-aware
siting/sizing research paper's PSO-only simulation by adding a Genetic
Algorithm comparison on the identical fitness function, wrapping both
algorithms in a working full-stack booking application (FastAPI + Next.js +
SQLite), and including a charging-demand prediction feature trained on the
paper's own renter-behavior dataset.

---

## Base Paper Reference & How This Project Extends It

**Citation:**
> A. Almutairi, "Optimizing Electric Vehicle Rental Services: Identifying
> Optimal Size and Locations for Permitting," *Arabian Journal for Science
> and Engineering*, vol. 51, pp. 11197-11208, 2026.

### What the base paper did

- Applied Particle Swarm Optimization (PSO) to jointly select the number,
  location (bus nodes), and fleet size of EV rental centers on a modified
  IEEE 33-bus radial distribution network.
- Enforced voltage constraints ([0.95, 1.05] p.u.) through an AC power-flow
  fitness function that penalizes losses and bus-voltage violations.
- Presented a pure simulation study -- no application layer, no booking
  system, no user interface.

### What this project adds

| Addition | Detail |
|---|---|
| **(a) GA comparison** | A Genetic Algorithm (binary tournament selection, single-point crossover, Gaussian mutation, elitism) is implemented on the **identical** encoding and fitness function as PSO, enabling a direct, apples-to-apples algorithm comparison -- directly addressing the paper's own stated future work on comparing meta-heuristics. |
| **(b) Full-stack application** | FastAPI REST backend + Next.js (App Router) frontend + SQLite database provide a complete EV rental booking system: user registration/login, center browsing, vehicle booking, and an admin dashboard -- none of which exist in the base paper. |
| **(c) Charging-demand prediction** | A `RandomForestRegressor` trained on the paper's `ev_renter_behavior.csv` dataset predicts per-booking charging energy (kWh) at booking time, integrating ML inference directly into the booking flow. |

---

## Tech Stack

| Layer | Technology |
|---|---|
| **Backend** | FastAPI (Python) - SQLAlchemy ORM - SQLite (`app.db`) - Uvicorn ASGI server |
| **Frontend** | Next.js 14 (App Router, JavaScript) - Tailwind CSS - Recharts |
| **Optimization** | Custom PSO (`pso_optimizer.py`) - Custom GA (`ga_optimizer.py`) - NumPy - pandapower (AC power flow on modified IEEE 33-bus network) |
| **Machine Learning** | scikit-learn `RandomForestRegressor` - pickle model persistence |
| **Auth / Security** | passlib + bcrypt password hashing (no JWT -- demo scope) |
| **Hardware** | CPU-only throughout -- no GPU dependencies |

---

## Prerequisites

| Tool | Tested Version |
|---|---|
| Python (inside venv) | **3.12.8** |
| Node.js | **v22.16.0** |
| npm | included with Node |

---

## Setup Instructions

### 1. Clone / navigate to the project root

```powershell
cd d:\FINAL-YR-PROJECT   # or wherever the repo is located
```

### 2. Create and activate the Python virtual environment

```powershell
# Skip if venv/ already exists
python -m venv venv

# Activate -- Windows PowerShell:
.\venv\Scripts\Activate.ps1

# Activate -- Windows CMD:
# .\venv\Scripts\activate.bat

# Activate -- macOS / Linux:
# source venv/bin/activate
```

### 3. Install backend Python dependencies

```powershell
pip install -r backend/requirements.txt
```

### 4. Install frontend Node dependencies

```powershell
cd frontend
npm install
cd ..
```

> **Note:** `backend/data/app.db`, `backend/data/benchmark_results.json`,
> and `backend/data/charging_prediction_model.pkl` are all already present
> from earlier build steps. You do **not** need to regenerate them unless
> you modify the source CSVs or want a fresh database.

---

## How to Run

Start the **backend first**, then the **frontend**. Both must be running
simultaneously for the full application to work.

> **Important:** The virtual environment lives at the **project root** (`venv/`).
> Always activate it **before** `cd backend` -- not from inside the backend directory.

### Step 1 -- (Optional) Seed the database

Only required if `backend/data/app.db` is missing or you deleted it to start fresh.
Run these commands **from the project root**:

```powershell
# From the project root:
.\venv\Scripts\Activate.ps1          # activate venv first
cd backend
..\venv\Scripts\python.exe -m app.db.seed
cd ..
```

### Step 2 -- Start the backend API server

Run these commands **from the project root** (venv activation is shown for clarity):

```powershell
# From the project root:
.\venv\Scripts\Activate.ps1          # activate venv first
cd backend
..\venv\Scripts\uvicorn app.main:app --reload --port 8000
```

API available at: **http://localhost:8000**
Health check: **http://localhost:8000/health** returns `{"status": "ok"}`

### Step 3 -- Start the frontend development server

Open a **second terminal** (venv not required for frontend):

```powershell
cd frontend
npm run dev
```

Frontend available at: **http://localhost:3000**

### Step 4 -- Open the application

Navigate to **http://localhost:3000** in your browser.

---

## Demo Login Credentials

| Role | Email | Password |
|---|---|---|
| **Admin** | `admin@demo.com` | `demo1234` |
| Regular User | `user@demo.com` | `demo1234` |

- **Admin** can access `/admin` -- all bookings table + PSO vs GA benchmark
  analytics dashboard with Recharts convergence curves.
- **Regular users** can browse rental centers, book vehicles, and view their
  own booking history.
- New regular-user accounts can be self-registered at `/register` -- no
  admin action needed.

> **Warning:** These are demo-only credentials. Change them before any real deployment.

---

## Key Results Summary

### PSO vs GA Optimizer Benchmark

Both algorithms were run with 30 iterations/generations, 15
particles/individuals, on the modified IEEE 33-bus network. Full benchmark
data is stored in `backend/data/benchmark_results.json`.

| Case | Algorithm | Best Fitness | Violations | Time (s) |
|------|-----------|-------------:|:----------:|---------:|
| N=2  | PSO       | -187.3207    | 0          | 28.86    |
| N=2  | GA        | -187.3207    | 0          | 28.24    |
| N=10 | PSO       | 4738.0751    | 5          | 28.50    |
| N=10 | GA        | 5648.2849    | 6          | 26.55    |

**Interpretation based on the actual data:**

- **N=2 (small fleet):** Both algorithms converge to the **same optimal
  fitness (-187.3207)** with zero voltage violations, showing that for a
  low-dimensional search space the problem is easily solvable by either
  method. PSO reached this solution by iteration 3; GA required 15
  generations.
- **N=10 (full network):** PSO produces a meaningfully better solution
  (4738 vs 5648, ~16% lower fitness) with one fewer voltage violation.
  Both algorithms still have violations at 30 iterations, consistent with
  the reduced demo iteration budget; a full 100-iteration run would be
  expected to continue improving. This result is consistent with PSO's
  known strength in continuous-space problems relative to GA crossover
  operators on larger search spaces.

### Charging-Demand Prediction Model

Trained on `ev_renter_behavior.csv` (140 rows, 80/20 train/test split,
`RandomForestRegressor`, `n_estimators=100`, `random_state=42`):

| Split | MAE | R2 |
|---|---|---|
| Train | 12.16 kWh | 0.5663 |
| **Test** | **26.74 kWh** | **-0.3272** |

> **Honest caveat:** The negative test R2 and high test MAE are expected
> consequences of training on only 140 rows of real-world, noisy renter
> data. This is a **proof-of-concept integration feature** that demonstrates
> the booking-to-ML pipeline end-to-end, and is **not** a production-grade
> predictor. MAE (~27 kWh against a dataset range of ~10-112 kWh) is the
> more interpretable error metric for this demo.

---

## Known Limitations

1. **Simplified authentication** -- Session management uses `localStorage`
   to store `{user_id, name, email, is_admin}`. There are no JWT tokens,
   no refresh tokens, and no server-side session validation middleware.
   This is deliberate for academic demo scope; do not deploy to production
   without replacing this with a proper auth layer.

2. **Reduced benchmark settings** -- PSO and GA are both run with 30
   iterations/generations and a population of 15 for demo runtime
   (~28 s per run). The base paper's equivalent settings are closer to
   100 iterations with larger populations; the N=10 results in particular
   would continue improving with more compute budget.

3. **Approximated per-unit EV load profile** -- The 5.9225 kW/EV peak load
   used in the power-flow module is derived by aggregating the 140
   empirical renter charging windows from `ev_renter_behavior.csv`. The
   base paper does not publish its exact EV load-profile derivation, so
   this is a stated approximation, not a reproduced value.

4. **Small prediction dataset** -- The charging-demand ML model is trained
   on 140 rows. With this little data, generalisation is limited and test
   R2 is negative. A dataset one or two orders of magnitude larger would
   be needed for a reliable model.

5. **Fitness function penalty constants** -- `C_loss = 100` and
   `C_viol = 1000` (applied to active power loss and voltage violations
   respectively) were chosen by the project team. The base paper does not
   specify exact penalty constant values, so these are tunable
   approximations.

---

## Project Structure

Actual folder tree as of final build (generated from disk inspection;
`venv/`, `node_modules/`, `__pycache__/`, and `.next/` omitted for brevity):

```
FINAL-YR-PROJECT/
├── venv/                              # Root Python virtual environment
├── .gitignore
├── README.md                          # this file (only README in repo)
│
├── backend/
│   ├── requirements.txt               # Pinned CPU-only Python dependencies
│   ├── data/
│   │   ├── app.db                     # SQLite database (seeded)
│   │   ├── benchmark_results.json     # PSO vs GA results for N=2 and N=10
│   │   ├── bus_loads.csv              # IEEE 33-bus active/reactive load data
│   │   ├── line_params.csv            # Distribution line resistance/reactance
│   │   ├── ev_renter_behavior.csv     # 140-row renter charging behavior dataset
│   │   ├── charging_prediction_model.pkl  # Trained RandomForestRegressor
│   │   ├── network_notes.md           # Power system modelling notes
│   │   └── validate_data.py           # Task 2 dataset validation script
│   └── app/
│       ├── __init__.py
│       ├── main.py                    # FastAPI entrypoint; GET /health
│       ├── core/                      # Config placeholder (currently empty)
│       ├── models/
│       │   ├── __init__.py            # Re-exports all ORM models
│       │   ├── user.py                # User ORM model
│       │   ├── center.py              # RentalCenter ORM model
│       │   ├── vehicle.py             # Vehicle ORM model
│       │   └── booking.py             # Booking ORM model
│       ├── schemas/
│       │   ├── __init__.py            # Re-exports all Pydantic schemas
│       │   ├── user.py                # UserCreate, UserOut schemas
│       │   ├── center.py              # RentalCenterOut schema
│       │   └── booking.py             # BookingCreate, BookingOut schemas
│       ├── db/
│       │   ├── __init__.py
│       │   ├── session.py             # SQLAlchemy engine + SessionLocal
│       │   ├── seed.py                # Database seed script (Task 8)
│       │   └── validate_db.py         # Task 8 DB validation script
│       ├── api/
│       │   ├── __init__.py            # APIRouter assembly
│       │   ├── auth.py                # POST /auth/register, POST /auth/login
│       │   ├── centers.py             # GET /centers, GET /centers/{id}
│       │   ├── bookings.py            # POST /bookings, GET /bookings, GET /bookings/user/{id}
│       │   ├── optimizer.py           # GET /optimizer/results
│       │   └── validate_api.py        # Task 9 API validation script
│       └── services/
│           ├── power_flow.py          # pandapower IEEE 33-bus AC power flow
│           ├── pso_optimizer.py       # Particle Swarm Optimization
│           ├── ga_optimizer.py        # Genetic Algorithm
│           ├── benchmark.py           # PSO vs GA benchmark runner (Task 6)
│           ├── load_profile.py        # EV aggregate load profile builder
│           ├── prediction_model.py    # RandomForest charging-demand model
│           ├── validate_power_flow.py # Task 3 power-flow validation
│           ├── validate_pso.py        # Task 4 PSO validation
│           ├── validate_ga.py         # Task 5 GA validation
│           └── validate_prediction.py # Task 7 prediction model validation
│
└── frontend/
    ├── package.json
    ├── next.config.mjs
    ├── postcss.config.mjs
    ├── jsconfig.json
    ├── eslint.config.mjs
    ├── .env.local                     # NEXT_PUBLIC_API_URL=http://localhost:8000
    ├── public/                        # Static SVG assets
    └── app/
        ├── layout.js                  # Root layout with Navbar
        ├── page.js                    # / Landing page
        ├── globals.css
        ├── components/
        │   └── Navbar.js              # Shared navigation bar
        ├── lib/
        │   ├── api.js                 # Centralised fetch helpers
        │   └── auth.js                # localStorage session helpers
        ├── login/
        │   └── page.js                # /login Sign-in form
        ├── register/
        │   └── page.js                # /register New user registration
        ├── centers/
        │   └── page.js                # /centers Rental center catalog
        ├── book/
        │   └── [vehicleId]/
        │       └── page.js            # /book/[vehicleId] Booking form
        └── admin/
            └── page.js                # /admin Admin dashboard
```

---

## Future Work

- **Full sensitivity analysis** across additional N-location cases (N=3, 5,
  7, ...), matching the base paper's Sections 5.1-5.3 and enabling a richer
  comparison table.
- **Live optimizer re-run from admin UI** -- currently the benchmark results
  are pre-computed and served statically; a future feature would allow an
  admin to trigger a fresh PSO/GA run from the dashboard and see live
  convergence updates.
- **Additional meta-heuristics** -- the base paper's own future-work section
  names Grey Wolf Optimizer (GWO) and other swarm methods as candidates
  for comparison; these could be added using the same shared
  encoding/fitness infrastructure already in place.
- **Production-grade auth** -- replace the current localStorage session with
  JWT tokens, HTTP-only cookies, and server-side role middleware.
- **Larger prediction dataset** -- a dataset of 1000+ real-world renter
  trips would substantially improve the charging-demand model generalisation.

---

## End-to-End Test Results (Task 12)

Full integration walkthrough with backend and frontend running
simultaneously -- all 12 steps passed with no bugs found:

| # | Step | Result |
|---|------|--------|
| 1 | `GET /health` returns `{"status": "ok"}` | PASS |
| 2 | `POST /auth/register` -- new user created | PASS |
| 3 | `POST /auth/login` -- credentials verified, frontend redirects to `/centers` | PASS |
| 4 | `GET /centers` -- all 10 PSO-optimized centers with nested vehicles | PASS |
| 5 | `POST /bookings` -- vehicle reserved, ML-predicted kWh displayed | PASS |
| 6 | Post-booking `is_available` flipped to `false`, visible on `/centers` reload | PASS |
| 7 | Double-booking same vehicle returns HTTP 400 with clear error | PASS |
| 8 | Admin login (`admin@demo.com`) returns `is_admin: true`, redirects to `/admin` | PASS |
| 9 | Admin `GET /bookings` -- all bookings with nested user/vehicle, sorted newest first | PASS |
| 10 | Admin bookings table -- all columns display correctly | PASS |
| 11 | `GET /optimizer/results` returns 30-point PSO and GA convergence histories; Recharts renders both lines | PASS |
| 12 | Wrong password returns HTTP 401; logout clears localStorage and redirects to `/login` | PASS |

---

## Status

**All 13 tasks complete.**
