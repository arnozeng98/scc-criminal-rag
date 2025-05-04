#!/bin/bash
# 
# Shell script version of the RAG system pipeline
# Executes the following steps:
# 1. Scrape SCC criminal cases
# 2. Process and extract structured data
# 3. Generate embeddings and build vector index
#

# Initialize default parameters
MAX_CASES=""
SKIP_SCRAPING=false
SKIP_PROCESSING=false
SKIP_EMBEDDINGS=false
API_KEY=""

# Display help information
show_help() {
  echo "SCC Criminal Cases RAG Pipeline"
  echo "Usage: ./run_pipeline.sh [options]"
  echo ""
  echo "Options:"
  echo "  -h, --help             Display this help message"
  echo "  -m, --max-cases N      Maximum number of cases to download per URL"
  echo "  -s, --skip-scraping    Skip the scraping step"
  echo "  -p, --skip-processing  Skip the processing step"
  echo "  -e, --skip-embeddings  Skip the embeddings step"
  echo "  -k, --api-key KEY      Specify OpenAI API key"
  echo ""
}

# Parse command line arguments
while [ "$1" != "" ]; do
  case $1 in
    -h | --help )           show_help
                            exit 0
                            ;;
    -m | --max-cases )      shift
                            MAX_CASES=$1
                            ;;
    -s | --skip-scraping )  SKIP_SCRAPING=true
                            ;;
    -p | --skip-processing ) SKIP_PROCESSING=true
                            ;;
    -e | --skip-embeddings ) SKIP_EMBEDDINGS=true
                            ;;
    -k | --api-key )        shift
                            API_KEY=$1
                            ;;
    * )                     echo "Unknown option: $1"
                            show_help
                            exit 1
  esac
  shift
done

# Run command and handle errors
run_command() {
  local cmd="$1"
  local description="$2"
  
  echo ""
  echo "================================================================================"
  echo "$description"
  echo "================================================================================"
  echo "Running: $cmd"
  echo ""
  
  eval $cmd
  local exit_code=$?
  
  if [ $exit_code -eq 0 ]; then
    echo "✅ $description completed successfully"
  else
    echo "❌ $description failed with exit code: $exit_code"
    exit $exit_code
  fi
}

# Record start time
START_TIME=$(date +%s)

# Export API key
if [ -n "$API_KEY" ]; then
  export OPENAI_API_KEY="$API_KEY"
fi

# Check for API key if embeddings step is not skipped
if [ "$SKIP_EMBEDDINGS" = false ] && [ -z "$OPENAI_API_KEY" ]; then
  echo "❌ ERROR: OpenAI API key not provided. Set it with --api-key option or OPENAI_API_KEY environment variable."
  exit 1
fi

# Step 1: Scrape cases
if [ "$SKIP_SCRAPING" = false ]; then
  SCRAPER_CMD="python -m backend.scripts.run_scraper"
  if [ -n "$MAX_CASES" ]; then
    SCRAPER_CMD="$SCRAPER_CMD --max-cases $MAX_CASES"
  fi
  run_command "$SCRAPER_CMD" "Step 1: Scraping SCC criminal cases"
else
  echo -e "\n⏭️  Skipping Step 1: Scraping SCC criminal cases"
fi

# Step 2: Process and extract data
if [ "$SKIP_PROCESSING" = false ]; then
  run_command "python -m backend.scripts.process_data" "Step 2: Processing and extracting structured data"
else
  echo -e "\n⏭️  Skipping Step 2: Processing and extracting structured data"
fi

# Step 3: Generate embeddings and build index
if [ "$SKIP_EMBEDDINGS" = false ]; then
  run_command "python -m backend.scripts.build_index" "Step 3: Generating embeddings and building vector index"
else
  echo -e "\n⏭️  Skipping Step 3: Generating embeddings and building vector index"
fi

# Calculate total elapsed time
END_TIME=$(date +%s)
ELAPSED_TIME=$((END_TIME - START_TIME))

echo -e "\n================================================================================"
echo "🎉 Pipeline completed successfully in $ELAPSED_TIME seconds"
echo "================================================================================"

# Print next steps
echo -e "\nNext steps:"
echo "1. Start the API server:"
echo "   uvicorn backend.src.api.app:app --reload"
echo "2. Start the frontend development server:"
echo "   cd frontend && npm start"
echo "3. Or run everything with Docker:"
echo "   docker-compose up -d" 