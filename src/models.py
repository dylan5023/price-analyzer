from pydantic import BaseModel, Field, ConfigDict

class PriceInput(BaseModel):
    model_config = ConfigDict(str_strip_whitespace=True)
    sku: str = Field(min_length=1)
    our_price: float = Field(gt=0)
    competitor_price: float = Field(gt=0)

class PriceResult(BaseModel):
    sku: str
    price_gap_percent: float = Field(allow_inf_nan=False)
    is_outlier: bool 
    review_required: bool 
