# Board Game System with Generative AI

This project is a board game system implemented using generative AI technologies. It aims to provide an engaging and interactive gaming experience by integrating AI into traditional board games.

## Current Game Available

- **Who Is the Undercover**: A social deduction game where players must identify the undercover agent among them.

## Getting Started

### Prerequisites

- Python 3.10.2 and related libraries installed on your system.

### Installation

1. Clone the repository to your local machine and then run:
   ```bash
    pip install -r requirements.txt
   ```

2. Create and edit .env file to store API keys
   ```bash
    touch .env
    vim .env
   ```
   Put your API key as following:
   ```bash
    export ELEVEN_API_KEY="REPLACE_THIS_LINE_WITH_YOUR_API_KEY"
    export OPENAI_API_KEY="REPLACE_THIS_LINE_WITH_YOUR_API_KEY"
   ```
   If you don't want to use API key, you can navigate to app.py,
   commented the first line, and uncommented the second line. This will use mock logics instead of calling API:
   ```python
   # from utils.ai_api import initialize_ai_agent, generate_ai_descriptions, generate_ai_votes
   from utils.ai_mock import initialize_ai_agent, generate_ai_descriptions, generate_ai_votes
   ```
3. Run：

   ```bash
   python app.py
   ```
   After running the command, open your web browser and navigate to the provided URL (e.g., http://localhost:5000) to access the game interface.

## Notice

#### This project uses [fullPage.js](https://github.com/alvarotrigo/fullPage.js). If necessary, please apply for or purchase the license.

#### This project contains a significant amount of generative AI content, and most of the code is provided by generative AI.