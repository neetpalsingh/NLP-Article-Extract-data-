import os
import pandas as pd
import numpy as np
import nltk
from nltk.tokenize import word_tokenize, sent_tokenize
from nltk.corpus import cmudict
import re

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('cmudict')

d = cmudict.dict()

def load_word(filename):
    with open(filename, 'r') as file:
        return set(file.read().splitlines())

positive_words = load_word('MasterDictionary/positive-words.txt')
negative_words = load_word('MasterDictionary/negative-words.txt')

def load_stopwords(folder_path):
    stopwords = set()
    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                stopwords.update(file.read().splitlines())
    return stopwords

stopwords_folder = 'StopWords' 
stop_words = load_stopwords(stopwords_folder)

# function to count syllables
def count_syllables(word):
    try:
        return [len(list(y for y in x if y[-1].isdigit())) for x in d[word.lower()]][0]
    except KeyError:
        return 1  

# function to determine if a word is complex
def is_complex(word):
    return count_syllables(word) >= 3

# function to perform text analysis
def analyze_text(text):
    words = word_tokenize(text)
    sentences = sent_tokenize(text)
    
    # remove punctuation and stopwords from words
    words = [word for word in words if word.isalpha() and word.lower() not in stop_words]
    
    word_count = len(words)
    sentence_count = len(sentences)
    avg_word_length = np.mean([len(word) for word in words])
    avg_sentence_length = word_count / sentence_count if sentence_count != 0 else 0
    
    # sentiment analysis
    positive_score = sum(1 for word in words if word.lower() in positive_words)
    negative_score = sum(1 for word in words if word.lower() in negative_words)
    polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
    subjectivity_score = (positive_score + negative_score) / (word_count + 0.000001)
    
    # complex word analysis
    complex_word_count = sum(1 for word in words if is_complex(word))
    percentage_complex_words = (complex_word_count / word_count) * 100 if word_count != 0 else 0
    fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)
    
    # syllable per word
    syllables_per_word = np.mean([count_syllables(word) for word in words])
    
    # count personal pronouns
    personal_pronouns = len([word for word in words if word in ['i', 'we', 'my', 'ours', 'us','I','We','My','Ours','Us']])
    # print(personal_pronouns)

    # pos_tags = nltk.pos_tag(words)
    # personal_pronouns = len([word for word, tag in pos_tags if tag == 'PRP' or tag == 'PRP$'])
    # print(personal_pronouns)
    
    # personal_nouns = []
    # personal_noun =['I', 'we','my', 'ours','and' 'us','My','We','Ours','Us','And'] 
    # for x in words:
    #  ans=0
    # for word in x:
    #   if word in personal_noun:
    #      ans+=1
    # personal_nouns.append(ans)
    # personal_pronouns=len(personal_nouns)
    # print(personal_pronouns)
    
    return {
        'POSITIVE SCORE': positive_score,
        'NEGATIVE SCORE': negative_score,
        'POLARITY SCORE': polarity_score,
        'SUBJECTIVITY SCORE': subjectivity_score,
        'AVG SENTENCE LENGTH': avg_sentence_length,
        'PERCENTAGE OF COMPLEX WORDS': percentage_complex_words,
        'FOG INDEX': fog_index,
        'AVG NUMBER OF WORDS PER SENTENCE': avg_sentence_length,
        'COMPLEX WORD COUNT': complex_word_count,
        'WORD COUNT': word_count,
        'SYLLABLE PER WORD': syllables_per_word,
        'PERSONAL PRONOUNS': personal_pronouns,
        'AVG WORD LENGTH': avg_word_length
    }

# Load the output structure
output_structure = pd.read_excel('Output Data Structure.xlsx')

# read the input URL
input_data = pd.read_excel('input.xlsx')

# folder where extracted articles are stored
input_dir = 'extracted_articles'

# iterate over each row in the input data
results = []
for _, row in input_data.iterrows():
    url_id = row['URL_ID']
    url = row['URL']
    file_path = os.path.join(input_dir, f'{url_id}.txt')
    
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            text = file.read()
            analysis_results = analyze_text(text)
            analysis_results['URL_ID'] = url_id
            analysis_results['URL'] = url
            results.append(analysis_results)

# convert results to dataset
results_df = pd.DataFrame(results)

# checking the dataset has the same columns and order as output structure
output_columns = output_structure.columns

for column in output_columns:
    if column not in results_df.columns:
        results_df[column] = None

results_df = results_df[output_columns]

# save the results to an excel file
output_file = 'analysis_results.xlsx'
results_df.to_excel(output_file, index=False)

print("Data analysis completed and saved to", output_file)