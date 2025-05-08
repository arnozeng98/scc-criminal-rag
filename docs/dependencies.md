# Dependencies Documentation

This document provides information about the project's dependencies, version requirements, and compatibility considerations.

## Backend Dependencies

The backend relies on several Python packages for different functionalities:

### Core Dependencies

| Package       | Version | Description                             |
| ------------- | ------- | --------------------------------------- |
| fastapi       | 0.104.0 | Fast API framework based on Starlette   |
| uvicorn       | 0.23.2  | ASGI server for FastAPI                 |
| pydantic      | >=2.5.2 | Data validation and settings management |
| python-dotenv | 1.0.0   | Environment variable management         |

### Vector Database

| Package          | Version | Description                                |
| ---------------- | ------- | ------------------------------------------ |
| chromadb         | 0.6.3   | Vector database for embeddings storage     |
| chroma-hnswlib   | 0.7.6   | HNSW algorithm for nearest neighbor search |
| langchain-chroma | 0.2.3   | LangChain integration for ChromaDB         |

### Data Processing

| Package      | Version  | Description                     |
| ------------ | -------- | ------------------------------- |
| numpy        | >=1.26.0 | Numerical computing library     |
| pandas       | >=2.1.0  | Data manipulation and analysis  |
| scikit-learn | 1.3.0    | Machine learning utilities      |
| requests     | 2.31.0   | HTTP client library             |
| httpx        | >=0.27.0 | Async HTTP client               |
| backoff      | 2.2.1    | Exponential backoff for retries |

### Web Scraping

| Package           | Version | Description                        |
| ----------------- | ------- | ---------------------------------- |
| selenium          | 4.11.2  | Browser automation for scraping    |
| webdriver-manager | 4.0.0   | Web driver management for Selenium |
| beautifulsoup4    | 4.12.2  | HTML parsing library               |

## Frontend Dependencies

The frontend is built with React and several supporting libraries.

## Version Update Notes

### ChromaDB Update (0.4.22 → 0.6.3)

The update to ChromaDB 0.6.3 includes several important changes:

1. **Database Schema Changes**: The newer version uses a different schema, making databases created with older versions incompatible
2. **New Dependencies**: Requires additional packages (chroma-hnswlib, langchain-chroma)
3. **API Changes**: Some API methods and parameters have been updated

### Dependency Compatibility Matrix

The following dependency updates were made to resolve compatibility issues:

1. **pydantic ≥2.5.2**: Required for compatibility with langchain-core
2. **numpy ≥1.26.0**: Required for compatibility with newer versions of pandas and langchain-chroma
3. **pandas ≥2.1.0**: Updated to work with numpy ≥1.26.0
4. **httpx ≥0.27.0**: Required for compatibility with ChromaDB 0.6.3

## Platform-Specific Dependencies

### ARM64 Architecture

The application now supports ARM64 architecture. When deploying on ARM-based systems:

1. No special dependencies are required as Docker images are built for multi-architecture
2. Native performance will vary based on the specific ARM implementation
3. Memory usage patterns may differ slightly from x86/AMD64 deployments

## Upgrading Dependencies

When upgrading project dependencies:

1. **Database Migration**: If upgrading ChromaDB, you may need to rebuild your vector database
2. **Testing**: Always test thoroughly after dependency updates, especially major version changes
3. **Version Pinning**: Critical dependencies should be pinned to specific versions to avoid unexpected breaking changes

## Development Dependencies

For development environments, these additional dependencies are recommended:

```bash
# Testing
pytest==7.4.0
pytest-cov==4.1.0

# Linting and formatting
black==23.7.0
flake8==6.1.0
isort==5.12.0

# Type checking
mypy==1.5.1
```
