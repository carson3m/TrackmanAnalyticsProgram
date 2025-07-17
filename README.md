# Trackman Analytics Program

A FastAPI-based web application for analyzing Trackman baseball data and generating pitcher reports.

## Features

- CSV upload and processing
- Team and pitcher selection
- PDF report generation with pitch analysis
- Authentication and authorization

## Local Development

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the development server:
```bash
python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

3. Access the API at: http://localhost:8000
4. View API documentation at: http://localhost:8000/docs

## AWS Deployment

### Prerequisites
- AWS account
- AWS CLI installed and configured
- EB CLI installed (`pip install awsebcli`)

### Deploy to AWS Elastic Beanstalk

1. Initialize EB application:
```bash
eb init -p python-3.12 trackman-analytics
```

2. Create environment:
```bash
eb create trackman-analytics-prod
```

3. Deploy:
```bash
eb deploy
```

4. Open the application:
```bash
eb open
```

### Environment Variables

Set these in the AWS Elastic Beanstalk console:
- `SECRET_KEY`: Your JWT secret key
- `DATABASE_URL`: Database connection string (if using external DB)

## API Endpoints

- `POST /api/csv/upload` - Upload CSV file (Admin only)
- `GET /api/csv/team_pitchers?team={team}` - Get pitchers for a team
- `GET /api/metrics/download_pdf?team={team}&pitcher={pitcher}` - Download pitcher report PDF
- `POST /api/auth/login` - User authentication

## License

[Your License Here] 