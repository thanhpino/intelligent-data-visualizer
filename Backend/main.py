import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path 

app = FastAPI()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "datasets"

def get_dataset_path(dataset_id: str):
    return DATASET_DIR / f"{dataset_id}.csv"
@app.get("/api/datasets")
def get_datasets():
    if not DATASET_DIR.is_dir():
        return [] 
    files = [f.stem for f in DATASET_DIR.glob("*.csv")]
    return files
@app.get("/api/datasets/{dataset_id}/suggestions")
def get_suggestions(dataset_id: str):
    filepath = get_dataset_path(dataset_id)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(filepath)
    suggestions = []

    for col in df.columns:
        if pd.api.types.is_numeric_dtype(df[col]):
            suggestions.append({"id": f"sum_{col}", "text": f"Tính tổng của '{col}' theo từng nhóm", "type": "group_sum", "column": col})
            suggestions.append({"id": f"avg_{col}", "text": f"Tính trung bình của '{col}' theo từng nhóm", "type": "group_avg", "column": col})
        if pd.api.types.is_object_dtype(df[col]) and df[col].nunique() < 20:
            suggestions.append({"id": f"count_{col}", "text": f"Đếm số lượng theo từng '{col}'", "type": "value_counts", "column": col})

    return {"columns": df.columns.to_list(), "suggestions": suggestions}

@app.post("/api/datasets/{dataset_id}/analyze")
async def analyze_data(dataset_id: str, request: dict):
    filepath = get_dataset_path(dataset_id)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(filepath)
    analysis_type = request.get("type")
    column = request.get("column")
    group_by_col = request.get("group_by_col")

    if not all([analysis_type, column, group_by_col]):
        raise HTTPException(status_code=400, detail="Missing parameters")
    if column not in df.columns or group_by_col not in df.columns:
        raise HTTPException(status_code=400, detail="Invalid column name")
    if analysis_type == "group_sum":
        result = df.groupby(group_by_col)[column].sum().reset_index()
        chart_type = "bar"
    elif analysis_type == "group_avg":
        result = df.groupby(group_by_col)[column].mean().reset_index()
        chart_type = "bar"
    elif analysis_type == "value_counts":
        result = df[column].value_counts().reset_index()
        result.columns = [column, 'count']
        chart_type = "pie"
    else:
        raise HTTPException(status_code=400, detail="Invalid analysis type")

    return {
        "chart_type": chart_type,
        "labels": result[result.columns[0]].to_list(),
        "data": result[result.columns[1]].to_list(),
        "title": f"Phân tích '{column}' theo '{group_by_col}'"
    }