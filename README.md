## Project Introduction
An intelligent word guessing solver that combines Wordle game API with DeepSeek big language model. The system intelligently generates rule-based word guesses by analyzing game feedback, achieving automated Wordle game solutions.

## Project structure
wordle-solver/
├── wordle_solver.py          # Main solver
├── nim_client.py             # DeepSeek API Client: LLM Interaction
├── .env.example              # Storing API keys
└── README.md                 # Project Description Document

## Environmental Requirements
```
Python: 3.8 or higher version
Package dependencies:
Requests: version 2.32.3 or higher
Python dongenv: Latest version
```

** Before running the file, it is necessary to create an. env file in the directory** which contains the following content**:
```
DEEPSEEK_API_KEY=YOUR PRIVATE KEY
```

## Configuration parameters
Game parameters (adjustable)
```
MAX_TTTEMPTS=20 # Maximum attempts
WORD_SIZE=5 # Word Length (Standard Wordle)
BASE_URL = " https://wordle.votee.dev:8000 # Wordle API Address
```

API parameters (adjustable)
```
MIN-REQUEST∝VAL=5.0 # Minimum interval for API calls (seconds)
TEMPERTURE=0.1 # LLM generation temperature (the lower the value, the more stable it is)
MODEL="deepseek chat" # DeepSeek model used
```