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
│   ├── scripts/             # Utility scripts
│   └── tests/               # Unit and integration tests
├── frontend/                # React frontend
│   ├── src/                 # Source code
│   │   ├── components/      # React components
│   │   ├── services/        # API services
│   │   └── contexts/        # React contexts
├── data/                    # Data storage
│   ├── raw/                 # Raw HTML files
│   ├── processed/           # Processed data
│   └── vectors/             # Vector embeddings
├── docs/                    # Documentation
├── docker/                  # Docker configuration
└── docker-compose.yml       # Docker Compose configuration
```

## Features

- **Web Scraping**: Automatically scrape and download Supreme Court of Canada criminal case decisions
- **Data Processing**: Clean and extract relevant information from case documents
- **Vector Search**: Create embeddings and search for semantically relevant case information
- **RAG System**: Combine retrieval with large language models to generate accurate answers
- **Web Interface**: User-friendly chat interface for asking questions

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

2. Access the web interface at `http://localhost`

### Running Locally (Development)

#### Backend

1. Install dependencies:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

2. Set up the data pipeline:

   ```bash
   # Scrape case data
   python scripts/run_scraper.py

   # Process the data
   python scripts/process_data.py

   # Build the vector index
   python scripts/build_index.py
   ```

3. Start the API server:

   ```bash
   uvicorn src.api.app:app --reload
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

## Usage

1. Open the web interface
2. Ask questions about Canadian Supreme Court criminal cases
3. Receive answers with relevant citations from actual cases

## License

[MIT License](LICENSE)

## Acknowledgments

- Supreme Court of Canada for making their case decisions publicly available
- OpenAI and Anthropic for their language models
- The open-source community for the tools and libraries used in this project
