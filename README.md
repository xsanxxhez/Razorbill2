
Razorbill — Geospatial AI Analysis Platform (Demo)
A raw demo of a geospatial AI analysis platform designed for quantitative analysts and quant traders.

Overview
Razorbill is an experimental full‑stack prototype that combines a 3D geospatial visualizer (“Razorball”) with an NLP‑driven AI layer and data pipelines for exploratory analysis. The goal is to turn heterogeneous inputs (natural language prompts, structured datasets, or external data sources) into actionable geospatial objects and analytical layers, enabling analysts to search for statistical edge and refine hypotheses through probabilistic framing.

This repository represents an early-stage demo and is currently frozen due to technical and financial constraints.
<img width="1710" height="1107" alt="image" src="https://github.com/user-attachments/assets/62b7b1ef-47d8-4604-bc0b-89e4a83e1610" />
What it can do (demo scope)
3D geospatial visualization of data layers (interactive globe viewer).

Render and explore multiple thematic layers (e.g., roads/buildings/parks/water, weather/temperature, population/density, earthquakes, pollution, satellite imagery — depending on connected sources).

NLP-assisted “data routing”:

Interprets user queries and routes them to the most relevant datasource.

Extracts location + requested layer type from natural language.

Large-scale analysis concept (prototype direction):

Connect pipelines for ingest → transform → analyze → visualize.

Statistical exploration to identify potential edge (hypothesis generation).

Probabilistic adjustment of signals (research direction) to maximize expected ROI (conceptual in this demo).

Privacy-preserving Web3 direction (planned):

A blockchain-enabled application intended to act as an independent data aggregator.

Designed to preserve anonymity for individuals providing sensitive data, helping reduce legal exposure risks for data contributors.

Architecture
This repo is split into two parts:

frontend/ — Vite + React UI with CesiumJS-based 3D visualization (“Razorball” viewer).

backend/ — Python backend (Flask) that powers query interpretation, datasource routing, and AI-assisted parsing.

Tech stack (current)
Frontend:

Vite + React

CesiumJS (3D globe / terrain / layer rendering)

Backend:

Python + Flask

OpenRouter API for LLM calls (query routing + request parsing)

Requests-based HTTP client

Key concepts (high-level)
Razorball: a 3D viewer that can display arbitrary “data layers” as geospatial objects.

NLP → Geospatial objects: the AI layer aims to transform loosely structured input into real geospatial primitives (points/lines/polygons) that can be visualized and analyzed.

Quant-oriented analysis: pipelines are intended to support statistical research workflows and signal evaluation.

Getting started (local)
Prerequisites
Node.js 18+

Python 3.10+ (recommended)

(Optional) Cesium Ion token (for terrain / assets)

OpenRouter API key

1) Frontend
bash
cd frontend
npm install
npm run dev
Open: http://localhost:5173

2) Backend
bash
cd backend
python3 -m venv venv
source venv/bin/activate

pip install -r requirements.txt
python app.py
If requirements.txt is missing or incomplete (common in raw demos), install dependencies manually:

bash
pip install flask flask-cors python-dotenv requests h3
3) Environment variables (IMPORTANT)
Do not hardcode API keys in source code. Use environment variables instead.
​

Backend (backend/.env, add to .gitignore):


​

Project status
Razorbill is currently frozen. Maintaining and scaling the platform requires infrastructure, operational effort, and funding that are currently not accessible to the co-founders.

Roadmap (planned / ideas)
More robust ingestion and ETL pipelines (batch + streaming).

Stronger statistical toolchain for quant research workflows (feature engineering, evaluation, simulation).

Model/router improvements: better schema validation, more deterministic outputs.

Web3 aggregator module for anonymous, consumer-sourced sensitive data.

Production-grade deployment and observability.

Security note
If any secret keys were ever committed:

Revoke/regenerate them immediately.

Remove them from history before making the repo public.

Team
Co-founders:

Alexander Ageenko

Eugene Hancharou
