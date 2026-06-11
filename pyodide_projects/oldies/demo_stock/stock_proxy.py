# pip install fastapi uvicorn yfinance
# run server with:
#    uvicorn stock_proxy:app --reload --port 8001

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
from fastapi.responses import JSONResponse
import pandas as pd

app = FastAPI()

# Enable CORS: allow all origins (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Or ["http://localhost:8000"] etc.
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_data")
def get_data(ticker: str = Query(..., min_length=1)):
    try:
        df = yf.download(ticker, period="6mo", interval="1d", auto_adjust=False)
        df = df.dropna()

        # Flatten MultiIndex if present
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.reset_index()
        df["Date"] = df["Date"].astype(str)

        return JSONResponse(content=df.to_dict(orient="records"))
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
