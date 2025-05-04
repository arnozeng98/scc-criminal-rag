@echo off
setlocal enabledelayedexpansion

:: 
:: Windows batch version of the RAG system pipeline
:: Executes the following steps:
:: 1. Scrape SCC criminal cases
:: 2. Process and extract structured data
:: 3. Generate embeddings and build vector index
::

:: Initialize default parameters
set MAX_CASES=
set SKIP_SCRAPING=false
set SKIP_PROCESSING=false
set SKIP_EMBEDDINGS=false
set API_KEY=

:: Parse command line arguments
:parse_args
if "%~1"=="" goto :args_done
if /i "%~1"=="--help" (
    call :show_help
    exit /b 0
) else if /i "%~1"=="-h" (
    call :show_help
    exit /b 0
) else if /i "%~1"=="--max-cases" (
    set MAX_CASES=%~2
    shift
) else if /i "%~1"=="-m" (
    set MAX_CASES=%~2
    shift
) else if /i "%~1"=="--skip-scraping" (
    set SKIP_SCRAPING=true
) else if /i "%~1"=="-s" (
    set SKIP_SCRAPING=true
) else if /i "%~1"=="--skip-processing" (
    set SKIP_PROCESSING=true
) else if /i "%~1"=="-p" (
    set SKIP_PROCESSING=true
) else if /i "%~1"=="--skip-embeddings" (
    set SKIP_EMBEDDINGS=true
) else if /i "%~1"=="-e" (
    set SKIP_EMBEDDINGS=true
) else if /i "%~1"=="--api-key" (
    set API_KEY=%~2
    shift
) else if /i "%~1"=="-k" (
    set API_KEY=%~2
    shift
) else (
    echo Unknown option: %~1
    call :show_help
    exit /b 1
)
shift
goto :parse_args
:args_done

:: Display help information
:show_help
echo SCC Criminal Cases RAG Pipeline
echo Usage: run_pipeline.bat [options]
echo.
echo Options:
echo   -h, --help             Display this help message
echo   -m, --max-cases N      Maximum number of cases to download per URL
echo   -s, --skip-scraping    Skip the scraping step
echo   -p, --skip-processing  Skip the processing step
echo   -e, --skip-embeddings  Skip the embeddings step
echo   -k, --api-key KEY      Specify OpenAI API key
echo.
exit /b 0

:: Run command and handle errors
:run_command
set cmd=%~1
set description=%~2

echo.
echo ================================================================================
echo %description%
echo ================================================================================
echo Running: %cmd%
echo.

%cmd%
set exit_code=%errorlevel%

if %exit_code% equ 0 (
    echo ✅ %description% completed successfully
) else (
    echo ❌ %description% failed with exit code: %exit_code%
    exit /b %exit_code%
)
exit /b 0

:: Record start time
set START_TIME=%time%

:: Export API key
if not "%API_KEY%"=="" (
    set OPENAI_API_KEY=%API_KEY%
)

:: Check for API key if embeddings step is not skipped
if "%SKIP_EMBEDDINGS%"=="false" (
    if "%OPENAI_API_KEY%"=="" (
        echo ❌ ERROR: OpenAI API key not provided. Set it with --api-key option or OPENAI_API_KEY environment variable.
        exit /b 1
    )
)

:: Step 1: Scrape cases
if "%SKIP_SCRAPING%"=="false" (
    set SCRAPER_CMD=python -m backend.scripts.run_scraper
    if not "%MAX_CASES%"=="" (
        set SCRAPER_CMD=!SCRAPER_CMD! --max-cases %MAX_CASES%
    )
    call :run_command "!SCRAPER_CMD!" "Step 1: Scraping SCC criminal cases"
    if errorlevel 1 exit /b !errorlevel!
) else (
    echo.
    echo ⏭️  Skipping Step 1: Scraping SCC criminal cases
)

:: Step 2: Process and extract data
if "%SKIP_PROCESSING%"=="false" (
    call :run_command "python -m backend.scripts.process_data" "Step 2: Processing and extracting structured data"
    if errorlevel 1 exit /b !errorlevel!
) else (
    echo.
    echo ⏭️  Skipping Step 2: Processing and extracting structured data
)

:: Step 3: Generate embeddings and build index
if "%SKIP_EMBEDDINGS%"=="false" (
    call :run_command "python -m backend.scripts.build_index" "Step 3: Generating embeddings and building vector index"
    if errorlevel 1 exit /b !errorlevel!
) else (
    echo.
    echo ⏭️  Skipping Step 3: Generating embeddings and building vector index
)

:: Calculate total elapsed time (Windows batch calculation of time is complex, simplified here)
set END_TIME=%time%
echo.
echo ================================================================================
echo 🎉 Pipeline completed successfully
echo ================================================================================

:: Print next steps
echo.
echo Next steps:
echo 1. Start the API server:
echo    uvicorn backend.src.api.app:app --reload
echo 2. Start the frontend development server:
echo    cd frontend ^&^& npm start
echo 3. Or run everything with Docker:
echo    docker-compose up -d

endlocal 