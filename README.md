# Financial Data Portal

A comprehensive financial data portal that captures market data, FTD analysis, swap theory models, and more.

## Features

- Real-time and historical price data from Polygon.io
- Failure-to-Deliver (FTD) data analysis
- Technical indicators and analytics
- Swap cycle and volatility cycle analysis
- User management with watchlists and alerts
- RESTful API for data access

## Project Structure

```
financial_portal/
├── financial_portal_api/       # Backend API
│   ├── src/
│   │   ├── database/           # SQLite database
│   │   ├── models/             # Database models
│   │   ├── routes/             # API routes
│   │   ├── services/           # Business logic services
│   │   ├── static/             # Static files
│   │   └── main.py             # Main application file
│   └── venv/                   # Virtual environment
├── run.sh                      # Script to run the application
├── test_api.py                 # Script to test the API
└── README.md                   # This file
```

## Setup

1. Clone the repository
2. Run the application:

```bash
./run.sh
```

3. Access the API at http://localhost:5000/api
4. Access the dashboard at http://localhost:5000/dashboard.html

## API Endpoints

### Securities

- `GET /api/securities` - List all securities
- `GET /api/securities/search?q=GME` - Search securities
- `GET /api/securities/GME` - Get security details
- `GET /api/securities/GME/price` - Get price data
- `GET /api/securities/GME/ftd` - Get FTD data
- `GET /api/securities/GME/indicators` - Get technical indicators
- `GET /api/securities/GME/swap-cycles` - Get swap cycle analysis
- `GET /api/securities/GME/volatility-cycles` - Get volatility cycle analysis
- `GET /api/securities/GME/correlations` - Get market correlations

### Users

- `GET /api/users` - List all users
- `POST /api/users` - Create a new user
- `GET /api/users/{id}` - Get user details
- `PUT /api/users/{id}` - Update a user
- `DELETE /api/users/{id}` - Delete a user
- `GET /api/users/{id}/watchlists` - Get user watchlists
- `POST /api/users/{id}/watchlists` - Create a new watchlist
- `GET /api/users/{id}/settings` - Get user settings
- `PUT /api/users/{id}/settings` - Update user settings
- `GET /api/users/{id}/alerts` - Get user alerts
- `POST /api/users/{id}/alerts` - Create a new alert

## Testing

Run the test script to verify the API is working correctly:

```bash
./test_api.py
```

You can specify a ticker symbol to test with:

```bash
./test_api.py AAPL
```

## Development

### Adding a new API endpoint

1. Create a new route file in `financial_portal_api/src/routes/`
2. Register the route blueprint in `financial_portal_api/src/routes/__init__.py`
3. Implement the necessary service logic in `financial_portal_api/src/services/`

### Adding a new model

1. Create a new model file in `financial_portal_api/src/models/`
2. Import the model in `financial_portal_api/src/models/__init__.py`

## License

This project is licensed under the MIT License.

