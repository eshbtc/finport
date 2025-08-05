# Render.com Deployment Guide

## Overview
This application is configured for deployment on Render.com with proper environment variable handling and production-ready settings.

## Environment Variables

Set these environment variables in your Render.com dashboard:

### Required Environment Variables:
```
POLYGON_API_KEY=your_polygon_api_key_here
SECRET_KEY=your_secure_secret_key_here
```

### Optional Environment Variables:
```
FLASK_DEBUG=False  # Set to 'True' for development debugging
RENDER=True        # Automatically set by Render.com
```

## Deployment Steps

1. **Connect Repository**: Link your GitHub repository to Render.com
2. **Configure Build Settings**:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
3. **Set Environment Variables**: Add the required environment variables above
4. **Deploy**: Render will automatically deploy your application

## Application Configuration

### Database
- Uses SQLite database stored in `/tmp/app.db` on Render.com
- Database is ephemeral and will be recreated on each deployment
- For production, consider using a persistent database service

### Static Files
- Static files are served from `src/static/`
- Includes dashboard.html and index.html

### API Services
- **Polygon API**: For market data
- **SEC EDGAR**: For FTD (Failure-to-Deliver) data
- **FTD Service**: Processes and stores FTD data

## Security Considerations

✅ **Fixed Issues**:
- Moved hardcoded API keys to environment variables
- Disabled debug mode in production
- Uses secure secret key from environment

⚠️ **Recommendations**:
- Use a persistent database (PostgreSQL) for production data
- Implement rate limiting for API endpoints
- Add authentication for sensitive endpoints
- Consider using HTTPS-only cookies

## Monitoring and Logs

- Application logs are available in Render.com dashboard
- Database operations are logged with timestamps
- API calls are tracked in the database

## Troubleshooting

### Common Issues:
1. **Database Errors**: Check if `/tmp` directory is writable
2. **API Key Issues**: Verify environment variables are set correctly
3. **Memory Issues**: Monitor memory usage in Render dashboard
4. **Timeout Issues**: Long-running FTD data processing may timeout

### Debug Mode:
Set `FLASK_DEBUG=True` temporarily to enable debug mode for troubleshooting.

## Performance Optimization

- FTD data processing is optimized for batch operations
- Static files are served efficiently
- Database queries are optimized with proper indexing
- API calls are logged and monitored

## Backup and Recovery

Since the database is ephemeral on Render.com:
- Consider implementing a backup strategy
- Use external database service for critical data
- Implement data export functionality for user data 