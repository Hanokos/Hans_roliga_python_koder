import os
import nltk
import pandas as pd
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, wordnet as wn
from collections import Counter

# Download necessary NLTK data
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')

def find_theme_by_similarity(keywords):
    """
    A more flexible similarity-based function. Instead of relying only on
    predefined keywords, we also take context into account for finding similarities.
    """
    themes = {
        "Engineering and Technology": ["technology", "engineering", "nuclear", "power", "energy", "electronics", "computing", "robotics", "nanotech"],
        "Medical and Health Sciences": ["medicine", "health", "doctor", "biotech", "pharma", "disease", "biomolecule", "protein", "cure"],
        "Natural Sciences": ["physics", "chemistry", "biology", "quantum", "material", "atoms", "molecules", "evolution", "astronomy"]
    }
    
    best_theme = None
    best_score = 0
    
    # Compute similarity between keyword sets and theme-specific words.
    for theme, rep_words in themes.items():
        total_similarity = 0
        count = 0
        for kw in keywords:
            kw_synsets = wn.synsets(kw)
            if not kw_synsets:
                continue
            for rep in rep_words:
                rep_synsets = wn.synsets(rep)
                if not rep_synsets:
                    continue
                for kw_syn in kw_synsets:
                    for rep_syn in rep_synsets:
                        sim = kw_syn.path_similarity(rep_syn)
                        if sim is not None:
                            total_similarity += sim
                            count += 1
        if count > 0:
            avg_similarity = total_similarity / count
            if avg_similarity > best_score:
                best_score = avg_similarity
                best_theme = theme
                
    return best_theme if best_theme is not None else "Uncategorized"

def get_theme(keywords):
    """
    Refined theme classification considering keyword matching and the broader context.
    """
    keywords_lower = [k.lower() for k in keywords]
    
    # Define keywords that represent each theme, expanding beyond basic scientific terms.
    theme_rep = {
        "Engineering and Technology": [
            "terahertz", "electronics", "robotics", "computing", "nanotechnology", "engineering", "power", "energy", "nuclear"
        ],
        "Medical and Health Sciences": [
            "biomolecule", "protein", "enzyme", "cure", "health", "medicine", "biotech", "disease", "biomolecular"
        ],
        "Natural Sciences": [
            "quantum", "material", "molecule", "atoms", "collisions", "earth", "astronomy", "chemistry", "physics", "biology"
        ]
    }
    
    # Score the themes based on their keyword matches.
    scores = {theme: 0 for theme in theme_rep}
    
    # Adjust weights for more dynamic matching based on context.
    for theme, rep_words in theme_rep.items():
        for rep in rep_words:
            for kw in keywords_lower:
                if rep in kw:
                    scores[theme] += 1

    # If no dominant theme found, fall back to similarity-based matching.
    best_theme = max(scores, key=scores.get)
    
    if scores[best_theme] == 0:
        return find_theme_by_similarity(keywords)

    return best_theme

def process_text(text, title):
    """
    Process the text: tokenize, remove stopwords, count word frequencies,
    extract the top 5 keywords, determine the theme, and build DCAT-like metadata.
    """
    tokens = word_tokenize(text)
    stop_words = set(stopwords.words('english'))
    filtered_tokens = [token for token in tokens if token.lower() not in stop_words and token.isalpha()]
    
    # Count word frequencies and pick top 5 keywords.
    freq = Counter(filtered_tokens)
    common_keywords = [word for word, count in freq.most_common(5)]
    
    # Get the theme based on the refined keyword matching and contextual analysis.
    theme = get_theme(common_keywords)
    
    # Build a description from the keywords.
    description = f"This project involves {', '.join(common_keywords)}."
    
    # Build a DCAT-like metadata dictionary.
    metadata = {
        "Dataset": ":Dataset",
        "Title": title,
        "Description": description,
        "Theme": theme,
        "Keyword": ", ".join(common_keywords)
    }
    
    return metadata

def main():
    # Ask the user for the number of text files to process.
    num_files = int(input("Enter the number of text files to process: "))
    metadata_list = []
    
    # For each file, ask for its name.
    for i in range(1, num_files + 1):
        filename = input(f"Enter the name of text file {i}: ").strip()
        if not os.path.exists(filename):
            print(f"File {filename} not found. Skipping this file.")
            continue
        
        with open(filename, "r", encoding="utf-8") as f:
            text = f.read()
        
        metadata = process_text(text, filename)
        metadata_list.append(metadata)
    
    if not metadata_list:
        print("No files processed. Exiting.")
        return
    
    # Create a DataFrame from the metadata list.
    df = pd.DataFrame(metadata_list, columns=["Dataset", "Title", "Description", "Theme", "Keyword"])
    
    # Determine an output filename: if exceltest.xlsx exists, increment a counter. eaxmpel: exceltest2.xlsx
    base_filename = "exceltest"
    extension = ".xlsx"
    output_excel = base_filename + extension
    counter = 1
    while os.path.exists(output_excel):
        output_excel = f"{base_filename}{counter}{extension}"
        counter += 1

    # Save the metadata to the Excel file.
    df.to_excel(output_excel, index=False)
    
    print(f"Metadata for {len(metadata_list)} project(s) saved to {output_excel}")

if __name__ == "__main__":
    main()



# in the terminal it will ask how many txt file you wanna read in. type a number.
# then it will ask each txt file you wanna read in.
# exampel test2.txt, then press enter then it will ask for next txt file to type in.