"""Load and normalize price data from CSV files."""

from pathlib import Path
import pandas as pd 
from src.exceptions import DataSourceError

PRICE_COLUMNS = ["our_price", "competitor_price"]

def load_rows(path:str | Path) -> list[dict]:
    """Read a CSV file and return normalized rows ready for validation.

    Only formatting issues are fixed here. Value-level validation is
    delegated to the Pydantic models.
    """

    try:
        df = pd.read_csv(path)
    except FileNotFoundError as e:
        raise DataSourceError(f"Cannot read price file: {path}") from e  
    
    # remove duplicate rows
    df = df.drop_duplicates()


    # remove comma
    for col in PRICE_COLUMNS:
        df[col] = df[col].astype(str).str.replace(",", "", regex=False)

    # change to list[dic]
    return df.to_dict('records')

    
    