# SCC Criminal Cases RAG System

A Retrieval-Augmented Generation (RAG) system for Canadian Supreme Court criminal cases. This system allows users to ask questions about criminal law cases and receive answers with relevant citations.

## Project Structure

```bash
/
├── backend/                 # Backend Python code
│   ├── src/                 # Source code
│   │   ├── api/             # FastAPI web service
│   │   ├── data_collection/ # Web scraping and data collection
│   │   ├── processor/       # Data processing and cleaning
│   │   ├── embeddings/      # Vector embeddings generation
│   │   ├── rag/             # RAG implementation
│   │   ├── utils/           # Utility functions
│   │   ├── config.py        # Configuration settings
│   │   └── main.py          # Entry point
│   └── scripts/             # Utility scripts
├── frontend/                # React frontend
│   ├── public/              # Public assets
│   └── src/                 # Source code
│       ├── components/      # React components
│       ├── services/        # API services
│       └── contexts/        # React contexts
├── data/                    # Data storage
│   ├── raw/                 # Raw HTML files
│   ├── processed/           # Processed data
│   └── vectors/             # Vector embeddings
├── docs/                    # Documentation
│   ├── api.md               # API documentation
│   ├── deployment.md        # Deployment guide
│   └── dependencies.md      # Dependencies information
├── docker/                  # Docker configuration
│   ├── backend.Dockerfile   # Backend container configuration
│   └── frontend.Dockerfile  # Frontend container configuration
├── .env.example             # Example environment variables
├── build_multiarch.sh       # Multi-architecture build script
├── docker-compose.yml       # Docker Compose configuration
├── docker-compose-build.yml # Docker Compose build configuration
├── run_pipeline.py          # Data pipeline script (Python)
├── run_pipeline.sh          # Data pipeline script (Bash)
├── run_pipeline.bat         # Data pipeline script (Windows)
└── README.md                # This file
```

## Features

- **Web Scraping**: Automatically scrape and download Supreme Court of Canada criminal case decisions
- **Data Processing**: Clean and extract relevant information from case documents
- **Vector Search**: Create embeddings and search for semantically relevant case information
- **RAG System**: Combine retrieval with large language models to generate accurate answers
- **Web Interface**: User-friendly chat interface for asking questions
- **Cross-Architecture Support**: Deploy on both x86/AMD64 and ARM64 architectures
- **Reverse Proxy Integration**: Support for deployment behind reverse proxies with proper API routing

## Getting Started

### Prerequisites

- Docker and Docker Compose
- OpenAI API key for embeddings and generation (or Anthropic API key as an alternative)

### Environment Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/scc-criminal-rag.git
   cd scc-criminal-rag
   ```

2. Create a `.env` file in the project root with your API keys:

   ```bash
   OPENAI_API_KEY=your_openai_api_key
   ANTHROPIC_API_KEY=your_anthropic_api_key
   ```

### Running with Docker

1. Build and start the containers:

   ```bash
   docker-compose up -d
   ```

2. Access the web interface at `http://localhost:8080`

### Multi-Architecture Support

The system supports deployment on both x86/AMD64 and ARM64 architectures. Use the provided `build_multiarch.sh` script to build images for multiple architectures:

```bash
./build_multiarch.sh
```

For more information on ARM deployment, see [Deployment Guide](docs/deployment.md).

### Reverse Proxy Configuration

For production deployments, it's recommended to deploy behind a reverse proxy. The application is configured to support this setup with the frontend making API requests to `/api` instead of a hardcoded URL.

See the [Deployment Guide](docs/deployment.md) for detailed reverse proxy configuration examples.

### Running Locally (Development)

#### Backend

1. Install dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Set up the data pipeline:

   ```bash
   # On Linux/macOS
   ./run_pipeline.sh
   
   # On Windows
   run_pipeline.bat
   
   # Or using Python directly
   python run_pipeline.py
   ```

3. Start the API server:

   ```bash
   uvicorn backend.src.api.app:app --reload
   ```

#### Frontend

1. Install dependencies:

   ```bash
   cd frontend
   npm install
   ```

2. Start the development server:

   ```bash
   npm start
   ```

3. Access the web interface at `http://localhost:3000`

## Documentation

- [API Documentation](docs/api.md): API endpoints and usage
- [Deployment Guide](docs/deployment.md): Detailed deployment instructions
- [Dependencies Documentation](docs/dependencies.md): Information about dependencies and version requirements

## Dependencies

The system uses several key dependencies:

- **ChromaDB 0.6.3**: Vector database for embeddings storage
- **FastAPI**: API framework
- **React**: Frontend framework

For a complete list of dependencies and version requirements, see the [Dependencies Documentation](docs/dependencies.md).

## Usage

1. Open the web interface
2. Ask questions about Canadian Supreme Court criminal cases
3. Receive answers with relevant citations from actual cases

## License

[Apache License 2.0](https://github.com/arnozeng98/scc-criminal-rag/blob/main/LICENSE)

## Acknowledgments

- Supreme Court of Canada for making their case decisions publicly available
- OpenAI and Anthropic for their language models
- The open-source community for the tools and libraries used in this project
