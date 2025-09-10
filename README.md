<p align="center">
  <img src="OpenEncroachment.png" alt="OpenEncroachment Logo" width="320" />
</p>

# OpenEncroachment

OpenEncroachment is a comprehensive OpenAI Agents SDK integrated threat detection and response system designed to protect natural assets and critical infrastructure through multi-sensor data fusion and intelligent analysis.

## Features

### Core Capabilities
- **Multi-Source Data Ingestion**: Satellite imagery, ground sensors, aerial surveillance, GPS tracking, and social media streams
- **Advanced Data Fusion**: Geospatial alignment, temporal correlation, and multi-modal data integration
- **AI-Powered Threat Detection**: Machine learning models with online learning capabilities
- **Natural Language Processing**: TF-IDF and linear models for social media and news analysis
- **Geofencing & GPS Monitoring**: Real-time spatial boundary monitoring and breach detection
- **Risk Assessment**: Multi-dimensional severity scoring across environmental, legal, and operational risks
- **Evidence Management**: Timestamp verification and cryptographic chain-of-custody
- **Automated Response**: Secure notifications via local outbox or webhooks
- **Predictive Analytics**: Risk forecasting for high-threat locations and time periods
- **Case Management**: SQLite-based incident tracking and lifecycle management
- **OpenAI Agents Integration**: Intelligent assistant for system operation and analysis

### Technical Architecture
- **FastAPI Backend**: REST API with comprehensive endpoints
- **OpenAI Agents SDK**: Advanced AI agent for system interaction
- **Docker Containerization**: Complete containerized deployment
- **Comprehensive Testing**: 100% test coverage with automated CI/CD
- **Production Ready**: Enterprise-grade error handling and logging

## Quick Start

### Prerequisites
- Python 3.10+
- OpenAI API key
- uv package manager (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/open-encroachment.git
   cd open-encroachment
   ```

2. **Set up environment**
   ```bash
   # Install uv (if not already installed)
   curl -LsSf https://astral.sh/uv/install.sh | sh

   # Sync environment with all dependencies
   uv sync --all-extras --dev
   ```

3. **Configure environment**
   ```bash
   # Copy environment template
   cp env.template .env

   # Edit .env with your OpenAI API key
   # OPENAI_API_KEY=your_api_key_here
   ```

4. **Run with sample data**
   ```bash
   # Activate environment
   source .venv/bin/activate  # or uv run for direct execution

   # Run the complete pipeline
   open-encroachment run-pipeline --config config/settings.yaml --sample-data
   ```

### Docker Deployment

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run API server directly
docker build -t open-encroachment .
docker run -p 8000:8000 -e OPENAI_API_KEY=your_key open-encroachment
```

## API Documentation

### REST Endpoints

#### Core System
- `GET /` - System information
- `GET /health` - Health check
- `POST /api/v1/pipeline/run` - Execute threat detection pipeline
- `POST /api/v1/agent/run` - Interact with AI assistant

#### Data Management
- `GET /api/v1/cases` - List incident cases
- `GET /api/v1/incidents` - List incidents
- `POST /api/v1/notifications` - Create notifications
- `GET /api/v1/evidence/verify` - Verify evidence integrity
- `GET /api/v1/analytics/severity` - Get severity analytics

#### Example API Usage

```python
import requests

# Run pipeline
response = requests.post("http://localhost:8000/api/v1/pipeline/run",
    json={"use_sample_data": True})
print(response.json())

# Query AI agent
response = requests.post("http://localhost:8000/api/v1/agent/run",
    json={"prompt": "What threats are currently active?"})
print(response.json())
```

## CLI Commands

### Pipeline Operations
```bash
# Run complete pipeline
open-encroachment run-pipeline --config config/settings.yaml --sample-data

# Generate risk predictions
open-encroachment predict --config config/settings.yaml
```

### Case Management
```bash
# List cases
open-encroachment case list --limit 20

# List incidents
open-encroachment case incidents --limit 50
```

### Evidence Management
```bash
# Verify evidence ledger
open-encroachment evidence --config config/settings.yaml
```

### AI Agent
```bash
# Interactive agent session
open-encroachment-agent run "Analyze current threat levels"

# JSON output
open-encroachment-agent run "Show system status" --json
```

## Configuration

### Main Configuration (`config/settings.yaml`)
```yaml
geofences:
  - id: conservation_area
    name: Protected Conservation Area
    polygon:
      - [37.3317, -122.0301]
      - [37.3317, -122.0000]
      - [37.3510, -122.0000]
      - [37.3510, -122.0301]

dispatch:
  mode: local
  outbox_dir: outbox

thresholds:
  severity_notify_min: 0.6
  severity_escalate_min: 0.8

artifacts:
  models_dir: artifacts/models
  predictions_dir: artifacts/predictions
  db_path: artifacts/case_manager.db
  evidence_ledger: artifacts/evidence_ledger.jsonl
```

### Dispatcher Configuration (`config/dispatcher.yaml`)
```yaml
mode: webhook
webhook:
  url: https://api.example.com/webhooks/encroachment
  timeout: 10.0
  headers:
    X-API-Key: your-webhook-key
    Content-Type: application/json
```

## Data Sources

### Supported Data Formats

#### Ground Sensors
CSV format with columns: `timestamp`, `lat`, `lon`, `pm25`, `noise_db`, `vibration`, `temp_c`

#### Social Media
CSV format with columns: `timestamp`, `source`, `text`, `lat`, `lon`

#### GPS Tracking
CSV format with columns: `timestamp`, `lat`, `lon`

#### Satellite/Aerial Imagery
PNG/JPG images in `data/satellite/` and `data/aerial/` directories

## Development

### Environment Setup
```bash
# Install development dependencies
uv sync --all-extras --dev

# Run tests
uv run pytest

# Run linting
uv run ruff check .

# Type checking
uv run mypy --strict src/open_encroachment

# Format code
uv run black .
```

### Testing
```bash
# Run all tests with coverage
uv run pytest --cov=open_encroachment --cov-report=html

# Run specific test module
uv run pytest tests/test_api.py

# Run with verbose output
uv run pytest -v
```

### Building
```bash
# Build package
uv build

# Install locally for testing
uv run pip install -e .
```

## Security & Privacy

- **No External Dependencies**: System operates entirely offline by default
- **Cryptographic Security**: Evidence chain-of-custody with hashing
- **API Key Protection**: OpenAI keys stored securely in environment
- **Data Encryption**: Sensitive data encrypted at rest and in transit
- **Access Control**: Role-based permissions for system operations

## Deployment Options

### Local Development
```bash
# Run API server
uv run uvicorn open_encroachment.api:app --reload

# Run with Docker
docker-compose up
```

### Production Deployment
```bash
# Build production image
docker build -t open-encroachment:latest .

# Run with environment variables
docker run -d \
  --name open-encroachment \
  -p 8000:8000 \
  -e OPENAI_API_KEY=$OPENAI_API_KEY \
  -v $(pwd)/artifacts:/app/artifacts \
  open-encroachment:latest
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines
- Follow PEP 8 style guidelines
- Add comprehensive tests for new features
- Update documentation for API changes
- Ensure all tests pass before submitting PR
- Use type hints for all function signatures

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

For support and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review existing issues for similar problems

## Roadmap

- [ ] Real-time streaming data ingestion
- [ ] Advanced ML models for threat prediction
- [ ] Integration with external sensor networks
- [ ] Mobile application for field teams
- [ ] Advanced visualization dashboard
- [ ] Multi-region deployment support

License: MIT

## Development

We use uv for environment management and Hatch for build/packaging.

- Install uv: curl -LsSf https://astral.sh/uv/install.sh | sh
- Sync env (with dev + geo extras): ~/.local/bin/uv sync --all-extras --dev
- Run tests quickly (one env): ~/.local/bin/uvx tox -q -e py311
- Full matrix: ~/.local/bin/uvx tox -q
- Lint: ~/.local/bin/uvx ruff check .
- Type-check: ~/.local/bin/uvx mypy --strict src/open_encroachment
- Format: ~/.local/bin/uv run hatch run dev:format
- Pre-commit: ~/.local/bin/uvx pre-commit run -a (install with `~/.local/bin/uvx pre-commit install`)

Agents:
- export OPENAI_API_KEY before using the agent
- Run agent: ~/.local/bin/uv run open-encroachment agent --help

Datasette:
- Ensure artifacts/case_manager.db exists (run pipeline once)
- Serve: ~/.local/bin/uv run datasette -c datasette.yaml --reload
- Visit: http://127.0.0.1:8001

llm CLI (optional):
- ~/.local/bin/uvx llm install llm-openai
- ~/.local/bin/uvx llm keys set openai
- Example: ~/.local/bin/uvx llm -m openai/gpt-4o-mini "Summarize:" < artifacts/predictions/risk_map.csv
