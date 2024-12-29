# Book Generator

This repository contains a Python script that automatically writes a book using a local [Ollama](https://github.com/jmorganca/ollama) API. It includes:

- **`input.txt`**: A file containing a **single, overall book summary** or setting.  
- **`outline.txt`**: A **CSV** file of chapters, each line containing:  

```chapter_number,chapter_title,chapter_summary```

- **A Python script** that:
1. Reads the **book summary** from `input.txt`.  
2. Parses **chapters** from `outline.txt`.  
3. Calls Ollama’s API to write each chapter, appending results to `book.txt`.  
4. Displays a **progress bar** using [tqdm](https://github.com/tqdm/tqdm).  
5. Archives the old `book.txt` if found, appending a timestamp to preserve previous runs.  
6. Outputs a **final summary** of the entire book.

---

## Requirements

1. **Python 3.8+**  
2. **[Ollama](https://github.com/jmorganca/ollama)** running locally on `http://localhost:11434/api/generate`.  
3. Any additional Python libraries specified in `requirements.txt`, such as:  
 - `requests`  
 - `tqdm`  

---

## Installation

1. **Clone** or **download** this repository.  
2. **Create and activate a virtual environment** (recommended):
 ```bash
 python3 -m venv .venv
 source .venv/bin/activate
 ```

### Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Check that Ollama is running locally and that the model you want to use ("llama3.3") is installed or configured.
	•	By default, the script expects to reach Ollama at http://localhost:11434/api/generate.
	•	Adjust the URL or model name in the script if your setup differs.

# Project Structure

├── input.txt            # Overall book summary
├── outline.txt          # Chapter outlines in CSV (chapter_number,chapter_title,chapter_summary)
├── book.txt             # Generated book content (created/updated by the script)
├── requirements.txt