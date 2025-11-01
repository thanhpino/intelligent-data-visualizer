import pandas as pd
from fastapi import FastAPI, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path

app = FastAPI()
api_router = APIRouter(prefix="/api")

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

@app.get("/")
def read_root():
    return {"Hello": "World", "Status": "Backend is running!"}

def find_and_convert_date_column(df):
    """Hàm này tìm và chuyển đổi cột ngày tháng đầu tiên nó thấy."""
    for col in df.columns:
        if df[col].dtype == 'object':
            try:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True)
                return col, df
            except (ValueError, TypeError):
                continue
    return None, df

@api_router.get("/datasets/{dataset_id}/suggestions")
def get_suggestions(dataset_id: str):
    filepath = get_dataset_path(dataset_id)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")
    df = pd.read_csv(filepath)
    suggestions = []
    date_col, df = find_and_convert_date_column(df) 

    if date_col:
        suggestions.append({"id": f"resample_month", "text": f"Thống kê số lượng theo Tháng (cột: {date_col})", "type": "resample_month", "column": date_col})
        suggestions.append({"id": f"resample_quarter", "text": f"Thống kê số lượng theo Quý (cột: {date_col})", "type": "resample_quarter", "column": date_col})
    for col in df.columns:
        if col == date_col: 
            continue

        if pd.api.types.is_numeric_dtype(df[col]):
            suggestions.append({"id": f"sum_{col}", "text": f"Tính tổng của '{col}'", "type": "group_sum", "column": col})
            suggestions.append({"id": f"avg_{col}", "text": f"Tính trung bình của '{col}'", "type": "group_avg", "column": col})
        if pd.api.types.is_object_dtype(df[col]) and df[col].nunique() < 20:
            suggestions.append({"id": f"count_{col}", "text": f"Đếm số lượng theo '{col}'", "type": "value_counts", "column": col})

    return {"columns": df.columns.to_list(), "suggestions": suggestions}

@api_router.post("/datasets/{dataset_id}/analyze")
async def analyze_data(dataset_id: str, request: dict):
    filepath = get_dataset_path(dataset_id)
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="Dataset not found")

    df = pd.read_csv(filepath)
    analysis_type = request.get("type")
    column = request.get("column")
    group_by_col = request.get("group_by_col")

    if analysis_type in ["resample_month", "resample_quarter"]:
        df[column] = pd.to_datetime(df[column])
        freq = 'M' if analysis_type == "resample_month" else 'Q'
        
        result = df.set_index(column).resample(freq).size().reset_index(name='count')
        if freq == 'M':
            result[column] = result[column].dt.strftime('%Y-%m')
        else:
            result[column] = result[column].dt.to_period('Q').astype(str)
            
        return {
            "chart_type": "line", 
            "labels": result[column].to_list(),
            "data": result['count'].to_list(),
            "title": f"Xu hướng theo {'Tháng' if freq == 'M' else 'Quý'}"
        }
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

app.include_router(api_router)