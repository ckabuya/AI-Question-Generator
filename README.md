# AI-Question-Generator

## Overview

The AI-Question-Generator project aims to develop an AI-driven tool to assist teachers in generating various types of questions for educational purposes. The tool will support multiple question formats compatible with Moodle, including Multiple Choice, True/False, Short Answer, and Matching questions.

## Features

- **Question Generation**: Automatically generate questions from provided content.
- **Moodle-Compatible Formats**: Export questions in formats such as GIFT, XML, and Aiken.
- **Customizable Difficulty**: Adjust question difficulty levels based on Bloom’s Taxonomy or NQF levels.
- **User-Friendly Interface**: Upload documents, specify parameters, and download generated questions with ease.

## Getting Started

### Prerequisites

- Python 3.x
- Virtual Environment

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/ckabuya/AI-Question-Generator.git
   ```

2. Navigate to the project directory:
   ```bash
   cd AI-Question-Generator
   ```

3. Set up a virtual environment:
   ```bash
   python -m venv env
   ```

4. Activate the virtual environment:
   - On Windows:
     ```bash
     .\env\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source env/bin/activate
     ```

5. Install the required libraries:
   ```bash
   pip install transformers spacy pdfminer.six python-docx
   ```

## Usage

1. Upload your content files (PDF, DOCX, TXT) to the designated folder.
2. Run the AI agent to generate questions.
3. Download the generated questions in your desired Moodle-compatible format.

## Contributing

We welcome contributions from the community. Please fork the repository and submit pull requests for any improvements or new features.

## License

This project is licensed under the MIT License.

## Acknowledgments

- Hugging Face Transformers
- SpaCy
- PDFMiner
- python-docx
