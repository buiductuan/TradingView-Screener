import json
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from starlette.requests import Request
from tradingview import Query, col
from helpers import google_sheet

app = FastAPI()

templates = Jinja2Templates(directory="templates")

# Custom filter to format numbers with commas (thousands separator)
def format_number(value: float) -> str:
    return f"{value:,.2f}"


# Add the custom filter to the Jinja2 environment
templates.env.filters['format_number'] = format_number

credentials = None
columns = ['close',
           'open',
           'high',
           'low',
           'volume',
           #    'change_percent',
           'market_cap_basic',
           'RSI',
           'MACD.macd',
           'MACD.signal',
           'MACD.hist',
           'ATR',
           'BB.upper',
           'BB.lower',
           'SMA10',
           'EMA10'
           ]


@app.get("/authorize")
async def authorize():
    global credentials
    res = google_sheet.authorize()
    if not res['is_redirect']:
        credentials = res['credentials']
        return RedirectResponse('/')
    return RedirectResponse(res['auth_url'])


@app.get("/oauth2callback")
async def oauth2callback(request: Request):
    global credentials
    credentials = google_sheet.oauth2callback(request)
    return RedirectResponse('/')


@app.post("/api/google-sheet")
async def google_sheet_post(request: Request):
    global credentials
    payload = await request.json()
    print(payload)
    market = payload.get('market') or 'crypto'
    limit = payload.get('limit') or '10'
    _, df = (Query().select(
        *columns).set_markets(market).limit(int(limit)).get_scanner_data())
    google_sheet.write_to_google_sheets(
        credentials=credentials, spreadsheet_id='1YLZOHMQC7yt1Ui9affJcEnlof5LSf0LQgObZ7sq3Kmc', sheet_range='Trang tính1!A2', data=df)
    return {
        "status": True,
        "data": []
    }


@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    market = request.query_params.get('market') or 'crypto'
    limit = request.query_params.get('limit') or '10'
    data = (Query().select(
        *columns).set_markets(market).limit(int(limit)).get_scanner_data_raw())
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "credentials": credentials, "columns": columns, "limit": limit,
            "market": market, "total": data['totalCount'], "data": data['data']}
    )
