import spacy

# Load the SpaCy model
nlp = spacy.load("en_core_web_sm")

def process_text(text):
    # Process the text using SpaCy
    doc = nlp(text)
    
    # Extract sentences
    sentences = [sent.text for sent in doc.sents]
    
    # Extract key concepts (nouns and proper nouns)
    key_concepts = [chunk.text for chunk in doc.noun_chunks]
    
    return sentences, key_concepts

# Example usage
if __name__ == "__main__":
    sample_text = """
    The ArrayList class is a resizable array, which can be found in the java.util package.
    The difference between a built-in array and an ArrayList in Java, is that the size of an array cannot be modified (if you want to add or remove elements to/from an array, you have to create a new one). 
    While elements can be added and removed from an ArrayList whenever you want.
    """
    sentences, key_concepts = process_text(sample_text)
    print("Sentences:", sentences)
    print("Key Concepts:", key_concepts)
