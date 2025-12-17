# 💰 Interest Calculator

A clean, full-stack web application that calculates Simple Interest and Compound Interest using Google Sheets as the calculation engine.

## What This Does

This app lets you enter a principal amount, interest rate, and time period, then instantly calculates both Simple Interest and Compound Interest. The cool part? All calculations happen in Google Sheets using formulas, so you can see and modify them anytime.

**Tech Stack:**
- **Frontend**: React 18 with modern CSS
- **Backend**: Python FastAPI REST API
- **Calculation Engine**: Google Sheets with formulas

## How It Works

```
User enters data in browser → React sends to FastAPI → API writes to Google Sheets
                                                            ↓
User sees results ← React displays ← FastAPI reads ← Google Sheets calculates
```

The flow is simple:
1. You enter Principal, Rate, and Time in the web interface
2. Frontend sends these values to the backend API
3. Backend writes them to a Google Sheet (Input sheet)
4. Google Sheets automatically calculates using formulas (Calc sheet)
5. Backend reads the results (Output sheet)
6. You see Simple Interest and Compound Interest on screen

## Prerequisites

Before you start, make sure you have:
- **Python 3.8+** installed
- **Node.js 16+** installed
- A **Google Account** (for Google Sheets and Cloud Platform)

## Quick Start

### Step 1: Google Cloud Setup

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (name it whatever you like)
3. Enable the **Google Sheets API**:
   - Navigate to "APIs & Services" → "Library"
   - Search for "Google Sheets API" and enable it
4. Create a **Service Account**:
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "Service Account"
   - Name it (e.g., "interest-calculator-service")
   - Click through the prompts (skip optional steps)
5. Generate a **JSON key**:
   - Click on your service account
   - Go to "Keys" tab
   - Click "Add Key" → "Create new key" → Choose "JSON"
   - Save this file as `credentials.json` in the `backend/` folder

### Step 2: Google Sheet Setup

1. Create a new Google Sheet
2. Get the Sheet ID from the URL:
   ```
   https://docs.google.com/spreadsheets/d/YOUR_SHEET_ID_HERE/edit
   ```
3. Share the sheet with your service account email (found in credentials.json as `client_email`)
   - Give it **Editor** permissions
4. Create **three worksheets** named exactly: `Input`, `Calc`, `Output`

**Input sheet structure:**
| A | B |
|---|---|
| Field | Value |
| Principal | (empty - API will fill) |
| Rate | (empty - API will fill) |
| Time | (empty - API will fill) |

**Calc sheet - Add these formulas:**
- Cell B2: `=Input!B2 * Input!B3 * Input!B4 / 100`
- Cell B3: `=Input!B2 * ((1 + Input!B3/100)^Input!B4 - 1)`

**Output sheet - Add these formulas:**
- Cell B2: `=Calc!B2`
- Cell B3: `=Calc!B3`

### Step 3: Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

Create a `.env` file in the `backend/` folder:
```env
GOOGLE_SHEET_ID=your_sheet_id_from_url
GOOGLE_CREDENTIALS_PATH=credentials.json
API_HOST=0.0.0.0
API_PORT=8000
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

Start the backend:
```bash
python -m app.main
```

The API will be running at `http://localhost:8001` (docs at `http://localhost:8000/docs`)

### Step 4: Frontend Setup

```bash
cd frontend
npm install
```

Create a `.env` file in the `frontend/` folder:
```env
REACT_APP_API_URL=http://localhost:8000
```

Start the frontend:
```bash
npm start
```

The app will open at `http://localhost:3000`

## Quick Test

Once everything is running:
1. Open http://localhost:3000
2. Enter these test values:
   - Principal: **10000**
   - Rate: **5.5**
   - Time: **3**
3. Click "Calculate Interest"
4. You should see:
   - Simple Interest: **₹1,650.00**
   - Compound Interest: **₹1,742.41**

## Project Structure

```
aspyr_project/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── main.py      # API routes and endpoints
│   │   ├── config.py    # Configuration settings
│   │   ├── models.py    # Data validation models
│   │   └── services/
│   │       └── google_sheets.py  # Google Sheets integration
│   ├── credentials.json  # Your Google service account key (don't commit!)
│   ├── requirements.txt  # Python dependencies
│   └── .env             # Backend configuration
├── frontend/            # React frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── InterestCalculator.jsx  # Main calculator component
│   │   │   └── InterestCalculator.css  # Styles
│   │   ├── services/
│   │   │   └── api.js   # API communication
│   │   ├── App.js       # Root component
│   │   └── index.js     # Entry point
│   ├── package.json     # Node dependencies
│   └── .env            # Frontend configuration
└── README.md           # This file!
```

## API Endpoints

The backend provides these endpoints:

- `GET /` - Welcome message
- `GET /health` - Check if API and Google Sheets are connected
- `GET /verify` - Verify Google Sheet structure
- `POST /calculate` - Calculate interest (send principal, rate, time)
- `GET /docs` - Interactive API documentation (Swagger UI)

## Troubleshooting

**"Credentials file not found"**
- Make sure `credentials.json` is in the `backend/` folder
- Check that the path in your `.env` file is correct

**"Spreadsheet not found"**
- Double-check the Sheet ID in your `.env` file
- Make sure you shared the sheet with your service account email
- Verify the service account has Editor permissions

**"Unable to connect to server"**
- Make sure the backend is running on port 8000
- Check that `REACT_APP_API_URL` in frontend `.env` matches the backend URL
- Try accessing http://localhost:8000/health directly in your browser

**Calculations don't work**
- Verify the three worksheets (Input, Calc, Output) exist with exact names
- Check that formulas are correctly entered in the Calc and Output sheets
- Make sure cells aren't accidentally formatted as text

## Made With

- **FastAPI** - Modern Python web framework
- **React** - UI library
- **Google Sheets API** - Serverless calculation engine
- **gspread** - Python Google Sheets client
- **Uvicorn** - ASGI server

## License

Feel free to use this project for learning and personal use.

---

**Note**: Keep your `credentials.json` file private. Never commit it to version control or share it publicly.

## 📝 API Documentation

Once the backend is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Main Endpoint

**POST /calculate**

Request:
```json
{
  "principal": 10000,
  "rate": 5.5,
  "time": 3
}
```

Response:
```json
{
  "simpleInterest": 1650.0,
  "compoundInterest": 1742.41
}
```

## 🎨 Features

- ✅ Clean, modern React UI
- ✅ Input validation
- ✅ Loading states
- ✅ Error handling
- ✅ Responsive design
- ✅ RESTful API
- ✅ Google Sheets integration
- ✅ Auto-recalculation
- ✅ Type validation
- ✅ CORS support

## 🚧 Optional Enhancements

- [ ] Add historical calculation storage
- [ ] Export results to PDF
- [ ] Multiple currency support
- [ ] Graphical visualization of interest over time
- [ ] Authentication and user accounts
- [ ] Rate comparison from different banks
- [ ] Email notifications
- [ ] Mobile app version

## 📄 License

MIT License

## 👥 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📞 Support

For issues and questions, please open an issue in the repository.
"# Interest-Calculator" 
"# Interest-Calculator" 
"# Interest-Calculator" 
"# Interest-Calculator" 
