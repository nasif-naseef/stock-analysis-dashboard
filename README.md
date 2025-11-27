# Stock Analysis Dashboard

A comprehensive web application for automated stock data collection, analysis, and historical comparison.

## 🌟 Features

- 🔄 **Automated Data Collection**: Hourly data fetching from multiple sources
- 📊 **Interactive Visualizations**: Real-time charts and graphs
- 📈 **Historical Analysis**: Compare data across multiple timeframes (1h, 2h, 4h, 6h, 12h, 1d, 1w)
- ⚖️ **Multi-Ticker Comparison**: Side-by-side analysis of different stocks
- 📥 **Export Functionality**: Download data in CSV, JSON, or PDF formats

## 🚀 Quick Start

### Using Docker Compose (Recommended)

```bash
# Clone the repository
git clone https://github.com/nasif-naseef/stock-analysis-dashboard.git
cd stock-analysis-dashboard

# Set up environment variables
cp backend/.env.example .env

# Start all services
docker-compose up -d

# Run database migrations
docker-compose exec backend alembic upgrade head
```

Access the application:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

## 🐳 Docker Deployment

### Development

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Production

```bash
# Build and start
docker-compose -f docker-compose.prod.yml up -d

# Check status
docker-compose -f docker-compose.prod.yml ps
```

See [docs/DEPLOYMENT.md](docs/DEPLOYMENT.md) for detailed instructions.

## 📁 Project Structure

```
stock-analysis-dashboard/
├── backend/          # FastAPI backend
├── frontend/         # React frontend
└── docs/            # Documentation
```

## 🔧 Status

🚧 **Under Development** - Initial setup in progress

## 📝 License

MIT License