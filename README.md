# EcoPackAI

**Production-grade AI-powered Sustainable Packaging Recommendation System.**

## Problem Statement
E-commerce and logistics sectors face immense packaging waste and inflated shipping costs due to sub-optimal packaging choices.

## Solution
EcoPackAI leverages Machine Learning to recommend the most sustainable, cost-effective, and dimensionally accurate packaging based on item dimensions, weight, fragility, and destination.

## Architecture
- **Frontend**: Next.js, Tailwind CSS, shadcn/ui
- **Backend**: FastAPI, PostgreSQL, SQLAlchemy
- **Machine Learning**: Scikit-Learn, XGBoost, Optuna
- **Deployment**: Docker, GitHub Actions

## ML Pipeline
```
Raw Data (Products + Materials)
    -> Pandera Validation
    -> Cleaning (Dimension Parsing, Dedup)
    -> Feature Engineering (Volume, Density, Material Efficiency)
    -> Cross-Join + Hard Filtering (Physics & Compliance)
    -> Ground Truth Score Generation
    -> Train/Val/Test Split (60/20/20)
    -> ColumnTransformer (StandardScaler + OneHotEncoder)
    -> Baseline Models (Linear, Tree, RF, XGBoost)
    -> Optuna Hyperparameter Optimization
    -> Final XGBoost Regressor (R2=0.94 on Test Set)
    -> Recommendation Engine (Top-5 Ranked Materials)
```

## Recommendation Engine
The system uses a Two-Stage Hybrid Architecture:
1. **Stage 1 (Rule-Based)**: Eliminates materials that violate physics (weight capacity) or compliance (food safety).
2. **Stage 2 (ML Ranking)**: XGBoost Regressor scores remaining materials on suitability (0-100), ranking them by predicted cost, CO2 emissions, and strength.

## Project Structure
```
EcoPackAI/
  data/
    external/          # Raw CSVs (product_categories, eco_packaging_materials)
    processed/         # Cleaned & engineered datasets
    artifacts/         # trained_model.joblib, preprocessor.joblib, registry
    reports/           # Feature importance plots, evaluation charts
  ml/
    data_engineering/  # validation.py, cleaning.py, feature_engineering.py, pipeline.py
    model_development/ # dataset_preparation.py, model_training.py, explainability.py,
                       # recommendation_engine.py, model_evaluation.py
  notebooks/           # EDA notebooks
  backend/             # (Phase 3: FastAPI)
  frontend/            # (Phase 4: Next.js)
```

## Quick Start
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Run Data Pipeline
python ml/data_engineering/pipeline.py

# Train Models
python ml/model_development/dataset_preparation.py
python ml/model_development/model_training.py

# Run Recommendation Engine Demo
python ml/model_development/recommendation_engine.py

# Evaluate & Register Model
python ml/model_development/model_evaluation.py
```

## Model Performance
| Model | R2 | RMSE | MAE |
|---|---|---|---|
| **XGBoost (Tuned)** | **0.942** | **0.771** | **0.084** |
| XGBoost (Baseline) | 0.995 | 0.222 | 0.123 |
| Random Forest | 0.990 | 0.304 | 0.040 |
| Decision Tree | 0.987 | 0.351 | 0.029 |
| Linear Regression | 0.902 | 0.971 | 0.483 |

## Production Artifacts
| Artifact | Purpose |
|---|---|
| `trained_model.joblib` | Serialized XGBoost model for inference |
| `preprocessor.joblib` | Fitted ColumnTransformer for feature scaling |
| `feature_metadata.json` | Feature names and counts for validation |
| `model_metrics.json` | MAE, RMSE, R2 on held-out test set |
| `training_config.json` | Best hyperparameters from Optuna |
| `model_registry.json` | Version, hash, date, environment metadata |

## Phases
- [x] Phase 0: Architecture & Requirements
- [x] Phase 1: Data Engineering Pipeline
- [x] Phase 2: ML Model Development & Recommendation Engine
- [ ] Phase 3: Backend API (FastAPI)
- [ ] Phase 4: Frontend (Next.js)
- [ ] Phase 5: Deployment (Docker, CI/CD)
