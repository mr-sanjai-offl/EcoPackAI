"""
Analytics Routes (Step 4 & 6)

REST endpoints that serve aggregated BI data.
These endpoints are designed specifically to be consumed by frontend
charting libraries (like Recharts or Plotly).

Why we format data this way (Step 6):
- Material Frequency: Returns an array of objects which can be directly fed into a Recharts <BarChart> or <Treemap>.
- Daily Trend: Returns date/predictions pairs perfectly suited for a <LineChart>.
- Category Breakdown: Perfect for a <PieChart>.
"""
from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.services.analytics_service import AnalyticsService
from app.schemas.response import (
    AnalyticsOverviewResponse,
    MaterialFrequencyResponse,
    CategoryBreakdownResponse,
    DailyTrendResponse
)

router = APIRouter()


@router.get(
    "/overview",
    response_model=AnalyticsOverviewResponse,
    summary="Get High-Level KPIs"
)
async def get_overview(db: Session = Depends(get_db)):
    """Retrieve top-level business metrics like CO2 and Cost savings."""
    return AnalyticsService.get_overview_kpis(db)


@router.get(
    "/materials",
    response_model=List[MaterialFrequencyResponse],
    summary="Get Material Recommendation Frequency"
)
async def get_materials(top_n: int = 10, db: Session = Depends(get_db)):
    """Retrieve the most frequently recommended materials (for Bar/Treemap charts)."""
    return AnalyticsService.get_material_frequency(db, top_n)


@router.get(
    "/categories",
    response_model=List[CategoryBreakdownResponse],
    summary="Get Category Usage Breakdown"
)
async def get_categories(db: Session = Depends(get_db)):
    """Retrieve request volume grouped by product category (for Pie charts)."""
    return AnalyticsService.get_category_breakdown(db)


@router.get(
    "/trends",
    response_model=List[DailyTrendResponse],
    summary="Get Daily Prediction Trends"
)
async def get_trends(db: Session = Depends(get_db)):
    """Retrieve daily request volumes over time (for Line/Area charts)."""
    return AnalyticsService.get_daily_trend(db)


@router.get(
    "/export",
    summary="Export Sustainability Report to CSV"
)
async def export_report(db: Session = Depends(get_db)):
    """Generate and download a CSV report of recent AI recommendations."""
    csv_data = AnalyticsService.export_sustainability_report_csv(db)
    return Response(
        content=csv_data,
        media_type="text/csv",
        headers={
            "Content-Disposition": "attachment; filename=ecopackai_sustainability_report.csv"
        }
    )
