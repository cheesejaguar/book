import requests
import sys
import time
import json
import os
import datetime
import argparse
import csv

from tqdm import tqdm

# Updated URL and model name
OLLAMA_URL = "http://localhost:11434/api/generate"
# OLLAMA_URL = "http://192.168.1.79:11434/api/generate"
MODEL_NAME = "llama3.3"

def parse_arguments():
    """Parses command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Automatically write a book using a local Ollama API."
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable verbose debug prints"
    )
    return parser.parse_args()

def debug_print(message: str, verbose: bool):
    """Helper function to conditionally print debug messages."""
    if verbose:
        print(message)

def call_ollama_api(prompt: str, verbose: bool) -> str:
    """
    Calls the local Ollama API with the specified prompt
    and returns the generated text.
    """
    payload = {
        "prompt": prompt,
        "model": MODEL_NAME
    }

    debug_print("\n--- DEBUG: Sending payload to Ollama ---", verbose)
    debug_print(json.dumps(payload, indent=2), verbose)
    
    try:
        response = requests.post(OLLAMA_URL, json=payload, stream=True)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error connecting to Ollama API: {e}")
        sys.exit(1)
    
    generated_text = ""
    for line in response.iter_lines(decode_unicode=True):
        # Debug print each raw line from the stream
        debug_print(f"DEBUG: Raw line from Ollama: {line}", verbose)
        if line:
            try:
                data = json.loads(line)
                # Ollama response is in data["response"]
                if "response" in data:
                    generated_text += data["response"]
                if data.get("done", False) is True:
                    break
            except json.JSONDecodeError as e:
                debug_print(f"DEBUG: JSONDecodeError occurred: {e}", verbose)
                continue

    debug_print("\n--- DEBUG: Generated text received ---", verbose)
    debug_print(generated_text, verbose)
    return generated_text.strip()


def write_chapter_to_book(
    chapter_number: str,
    chapter_title: str,
    chapter_outline: str,
    current_book_text: str,
    book_summary: str,
    verbose: bool
):
    """
    Prompts Ollama to write a new chapter using:
    - The overall 'book_summary'
    - The 'chapter_outline' (summary for this specific chapter)
    - The current book content (context)
    Appends the generated text to book.txt.
    """
    prompt = (
        f"Overall Book Summary:\n{book_summary}\n\n"
        f"Story so far:\n{current_book_text}\n\n"
        f"This chapter is described as:\n{chapter_outline}\n\n"
        f"Please write Chapter {chapter_number} titled '{chapter_title}' "
        f"so that it follows naturally from the story so far.\n\n"
        "Begin the chapter now:"
    )
    chapter_text = call_ollama_api(prompt, verbose=verbose)
    
    with open("book.txt", "a", encoding="utf-8") as f:
        f.write(f"\n\n### Chapter {chapter_number}: {chapter_title}\n\n")
        f.write(chapter_text + "\n")


def count_words_with_ollama(text: str, verbose: bool) -> int:
    """
    Uses Ollama to count the number of words in the given text.
    The prompt instructs the model to output just the number.
    """
    prompt = (
        "You are given the following text. Please return only the number "
        "of words in the text (as an integer) without any additional commentary.\n\n"
        f"Text:\n{text}\n\nNumber of words:"
    )
    
    generated_response = call_ollama_api(prompt, verbose=verbose)
    
    # Attempt to parse integer from response
    try:
        word_count = int("".join(filter(str.isdigit, generated_response)))
    except ValueError:
        word_count = 0
    
    return word_count


def summarize_progress(chapters_written: int, total_chapters: int, word_count: int) -> str:
    """
    Summarizes progress in a short statement.
    """
    return (
        f"Chapters: {chapters_written}/{total_chapters} | "
        f"Words so far: {word_count}"
    )


def summarize_book(book_text: str, verbose: bool) -> str:
    """
    Uses Ollama to produce a summary of the entire book.
    """
    prompt = (
        "Please provide a concise summary of the following story:\n\n"
        f"{book_text}\n\nSummary:"
    )
    return call_ollama_api(prompt, verbose=verbose)


def main():
    args = parse_arguments()
    verbose = args.verbose

    # If book.txt exists, archive it instead of deleting.
    if os.path.exists("book.txt"):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        archive_name = f"book_{timestamp}.txt"
        os.rename("book.txt", archive_name)
        debug_print(f"Existing 'book.txt' archived as '{archive_name}'.", verbose)

    # 1) Load the overall book summary from "input.txt"
    try:
        with open("input.txt", "r", encoding="utf-8") as f:
            book_summary = f.read().strip()
    except FileNotFoundError:
        print("Could not find 'input.txt'. Please ensure it is in the same directory.")
        sys.exit(1)

    if not book_summary:
        print("The 'input.txt' file is empty or not properly formatted.")
        sys.exit(0)

    # 2) Load the outline from "outline.txt" (CSV)
    chapters = []
    try:
        with open("outline.txt", "r", encoding="utf-8") as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                # Each row: [chapter_number, chapter_title, chapter_summary]
                # Make sure it has at least 3 columns
                if len(row) < 3:
                    continue
                chapter_number = row[0].strip()
                chapter_title = row[1].strip()
                chapter_summary = row[2].strip()
                chapters.append((chapter_number, chapter_title, chapter_summary))
    except FileNotFoundError:
        print("Could not find 'outline.txt'. Please ensure it is in the same directory.")
        sys.exit(1)

    if not chapters:
        print("The 'outline.txt' file is empty or not properly formatted.")
        sys.exit(0)

    total_chapters = len(chapters)
    chapters_written = 0

    # Use tqdm to create a progress bar for the total number of chapters
    with tqdm(total=total_chapters, desc="Writing Chapters", unit="chapter") as pbar:
        for (chapter_number, chapter_title, chapter_summary) in chapters:
            debug_print(f"\n--- Writing Chapter {chapter_number}: {chapter_title} ---", verbose)

            # Read current book content so far
            if os.path.exists("book.txt"):
                with open("book.txt", "r", encoding="utf-8") as bf:
                    book_so_far = bf.read()
            else:
                book_so_far = ""

            # Write the new chapter
            write_chapter_to_book(
                chapter_number, 
                chapter_title, 
                chapter_summary, 
                book_so_far, 
                book_summary,
                verbose=verbose
            )
            chapters_written += 1

            # Read current book content again after writing
            with open("book.txt", "r", encoding="utf-8") as bf:
                book_text_after_new_chapter = bf.read()

            # Count words
            word_count = count_words_with_ollama(book_text_after_new_chapter, verbose=verbose)

            # Update the progress bar
            progress_summary = summarize_progress(chapters_written, total_chapters, word_count)
            pbar.update(1)  # move one chapter forward
            pbar.set_postfix_str(progress_summary)

            # (Optional) Let the model analyze the book so far if there are remaining chapters
            if chapters_written < total_chapters:
                prompt = (
                    "Here is the progress so far:\n\n"
                    f"{book_text_after_new_chapter}\n\n"
                    "Please read and acknowledge the story so far. "
                    "When you're done, just say 'Understood.'"
                )
                acknowledgement = call_ollama_api(prompt, verbose=verbose)
                debug_print(f"Ollama Acknowledgement: {acknowledgement}\n", verbose)
                time.sleep(1)

    # Once the loop finishes, we have a complete book
    print("\n--- Book writing complete! ---\n")

    # Summarize the entire book
    with open("book.txt", "r", encoding="utf-8") as bf:
        final_book_text = bf.read()

    final_summary = summarize_book(final_book_text, verbose=verbose)
    print("Summary of the Book:")
    print(final_summary)


if __name__ == "__main__":
    main()