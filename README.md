# AI RPG Game with Mental Health Themes

An interactive text-based RPG powered by Ollama and Gradio that explores themes of mental health through the character of Elara Moonweaver, a High Elf wizard struggling with anxiety and depression while trying to save her world.

## Features

- Text-based adventure gameplay using AI-generated responses
- Character-driven narrative focusing on mental health themes
- Interactive web interface built with Gradio
- Persistent game state and conversation history
- Customisable character attributes via JSON configuration

## Setup Instructions

### 1. Download Model from Ollama
```bash
ollama pull mattw/llama2-13b-tiefighter
```

### 2. Set Up Virtual Environment
```bash
conda create --prefix=venv python=3.11 -y
```

### 3. Activate the Virtual Environment
```bash
conda activate ./venv
```

### 4. Install Packages
```bash
python -m pip install -r requirements.txt
```

### 5. Run the Gradio Application
```bash
python main.py
```