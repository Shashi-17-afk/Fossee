"""Data parsing and analytics using Pandas."""
import pandas as pd


REQUIRED_COLUMNS = ['Equipment Name', 'Type', 'Flowrate', 'Pressure', 'Temperature']


def parse_csv(file) -> pd.DataFrame:
    """Parse uploaded CSV and validate columns."""
    df = pd.read_csv(file)
    df.columns = df.columns.str.strip()
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
    return df[REQUIRED_COLUMNS]


def compute_summary(df: pd.DataFrame) -> dict:
    """Compute total count, averages, and equipment type distribution."""
    numeric_cols = ['Flowrate', 'Pressure', 'Temperature']
    averages = df[numeric_cols].mean().round(2).to_dict()
    type_counts = df['Type'].value_counts().to_dict()
    return {
        'total_count': len(df),
        'averages': averages,
        'equipment_type_distribution': type_counts,
    }


def get_summary_and_records(file) -> tuple[dict, list]:
    """Parse CSV and return summary + list of records for API/PDF."""
    df = parse_csv(file)
    summary = compute_summary(df)
    records = df.to_dict(orient='records')
    for r in records:
        for k, v in r.items():
            if isinstance(v, float) and pd.notna(v):
                r[k] = round(v, 2)
    return summary, records
