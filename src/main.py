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


# Danh sách các cột cần lấy dữ liệu
# All data: https://shner-elmo.github.io/TradingView-Screener/2.5.0/tradingview_screener/constants.html#COLUMNS
columns = ['close',
           'open',
           'high',
           'low',
           'volume',
           #'change_percent_24h',
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

# API xuất ra google sheet
@app.post("/api/google-sheet")
async def google_sheet_post(request: Request):
    global credentials
    payload = await request.json()
    market = payload.get('market') or 'crypto'
    limit = payload.get('limit') or '10'
    sheet_id = payload.get(
        'sheet_id') or '1YLZOHMQC7yt1Ui9affJcEnlof5LSf0LQgObZ7sq3Kmc'
    sheet_range = payload.get('sheet_range') or 'Trang tính1!A2'

    if sheet_id is not None and sheet_range is not None:
        with open('sheet.json', 'w') as token:
            token.write(json.dumps({
                "sheet_id": sheet_id,
                "sheet_range": sheet_range
            }))

    _, df = (Query().select(
        *columns).set_markets(market).limit(int(limit)).get_scanner_data())
    google_sheet.write_to_google_sheets(
        credentials=credentials, spreadsheet_id=sheet_id, sheet_range=sheet_range, data=df)
    return {
        "status": True,
        "data": []
    }

# Hiển thị của trang chủ
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    market = request.query_params.get('market') or 'crypto'
    limit = request.query_params.get('limit') or '10'
    sheet_id = None
    sheet_range = None
    try:
        with open('sheet.json', 'r') as file:
            data = json.load(file)
            sheet_id = data['sheet_id']
            sheet_range = data['sheet_range']
    except:
        pass

    data = (Query().select(
        *columns).set_markets(market).limit(int(limit)).get_scanner_data_raw())
    return templates.TemplateResponse(
        "index.html",
        {"request": request, "credentials": credentials, "columns": columns, "limit": limit,
            "market": market, "total": data['totalCount'], "data": data['data'], "sheet_id": sheet_id, "sheet_range": sheet_range}
    )
