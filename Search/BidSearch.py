import os
import re
from PyPDF2 import PdfReader
import time


def search_words_in_pdf(file_path, search_words):
    results = []
    with open(file_path, "rb") as file:
        pdf_reader = PdfReader(file)
        for page_num, page in enumerate(pdf_reader.pages):
            text = page.extract_text()
            found_words = []
            for search_word in search_words:
                if re.search(r'\b{}\b'.format(re.escape(search_word)), text, flags=re.IGNORECASE):
                    found_words.append(search_word)
            if len(found_words) == len(search_words):
                results.append((file_path, page_num + 1))
    return results


def search_words_in_pdfs(directory, search_words, years_back):
    # Get the current time
    current_time = time.time()
    # Calculate the timestamp for the specified number of years back
    specified_time = current_time - (years_back * 365 * 24 * 60 * 60)
    # Create a list to store the results
    results = []
    # Iterate over all files in the directory
    for filename in os.listdir(directory):
        if filename.endswith(".pdf"):
            filepath = os.path.join(directory, filename)
            # Get the modification time of the file
            modification_time = os.path.getmtime(filepath)
            # Check if the file has been modified within the specified number of years back
            if modification_time > specified_time:
                # Search for the words in the PDF file
                page_results = search_words_in_pdf(filepath, search_words)
                if page_results:
                    results.extend(page_results)
    return results


if __name__ == "__main__":
    # Prompt the user for directory path
    directory_path = input("Enter the directory path: ")
    # Prompt the user for the first word to search for
    word1 = input("Enter the first word you want to search for: ")
    # Prompt the user for the second word to search for
    word2 = input("Enter the second word you want to search for: ")
    # Prompt the user for the number of years back
    years_back = int(input("Enter the number of years back: "))

    print("Searching...")

    # Perform the search
    search_words = [word1, word2]
    results = search_words_in_pdfs(directory_path, search_words, years_back)

    for result in results:
        print(f"Words '{word1}' and '{word2}' found in file: {result[0]}, page {result[1]}")
        input()
