import os
from PyPDF2 import PdfReader


# Function to extract the 6-char string after "Letting of:" from text
def extract_string(text):
    index = text.find("Letting of:")
    if index != -1:
        return text[index + len("Letting of:"):index + len("Letting of:") + 7]


# Function to rename the file with the extracted string
def rename_file(old_path, new_name):
    directory = os.path.dirname(old_path)
    new_file_path = os.path.join(directory, new_name + ".pdf")

    # Check if the new file name already exists
    counter = 1
    while os.path.exists(new_file_path):
        new_file_path = os.path.join(directory, f"{new_name}_{counter}.pdf")
        counter += 1

    # If a file with the new name exists, delete it
    if os.path.exists(new_file_path):
        os.remove(new_file_path)

    os.rename(old_path, new_file_path)
    print(f"File renamed to: {os.path.basename(new_file_path)}")


# Main function to read the file, extract the string, and rename the file
def main():
    folder_path = input("Enter the path of the folder: ")
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            with open(pdf_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                text = ""
                for page in pdf_reader.pages:
                    text += page.extract_text()
            extracted_string = extract_string(text)
            if extracted_string:
                rename_file(pdf_path, extracted_string)


if __name__ == "__main__":
    main()
