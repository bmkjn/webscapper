from bs4 import BeautifulSoup
import pandas as pd
import requests
import os
import time
import json
import csv
import os
import string
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize,sent_tokenize



def save_product2(book_name, paras, urlid,url,response):
    file_name = './solution/' + urlid
    with open(file_name, 'w', encoding='utf-8') as file:
        if response == 200:
            file.write(book_name.text + '\n\n')
            if paras:
                for para in paras:
                    file.write(paras.text + '\n\n')
            else:
                response2 = requests.get(url)
                soup = BeautifulSoup(response2.content, 'html.parser')
                paras2 = soup.find('div', class_='td_block_wrap tdb_single_content tdi_130 td-pb-border-top td_block_template_1 td-post-content tagdiv-type') 
                file.write(paras2.text + '\n\n')
        else:
            file.write(book_name + '\n\n')
            for para in paras:
                file.write(paras + '\n\n')

def scrape(url,urlid):
    response = requests.get(url)
    print(response)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        book_name = soup.find('h1')
        print(book_name)
        paras = soup.find('div', class_='td-post-content tagdiv-type')  
        save_product2(book_name, paras, urlid,url,response.status_code)
    elif response.status_code == 404:
        save_product2("Ooops... Error 404", "Sorry, but the page you are looking for doesn't exist.", urlid,url,response.status_code)
    else:
        print("Unexpected error occurred:", response.status_code)




def clean_tokens(text,stopp_words):
    dirty_tokens = word_tokenize(text)
    tokens = [word for word in dirty_tokens if word not in string.punctuation]
    cleaned_tokens = [word for word in tokens if word not in stopp_words]
    return cleaned_tokens




def calculate_positive_score(cleaned_tokens, positive_words):
    positive_score = 0
    for token in cleaned_tokens:
        if token in positive_words:
            positive_score += 1
    return positive_score



def calculate_negative_score(cleaned_tokens, negative_words):
    negative_score = 0
    for token in cleaned_tokens:
        if token in negative_words:
            negative_score += 1
    return negative_score



def polarity_score(cleaned_tokens,positive_words,negative_words):
    pscore = calculate_positive_score(cleaned_tokens, positive_words)
    nscore = calculate_negative_score(cleaned_tokens, negative_words)
    ps = (pscore-nscore)/((pscore+nscore)+0.000001)
    return ps



def subjectivity_score(cleaned_tokens,positive_words,negative_words):
    pscore = calculate_positive_score(cleaned_tokens, positive_words)
    nscore = calculate_negative_score(cleaned_tokens, negative_words)
    ss = (pscore+nscore)/((len(cleaned_tokens))+0.000001)
    return ss



def average_sentence_length(text,cleaned_tokens):
    total_sentences = len(sent_tokenize(text))
    total_words = len(cleaned_tokens)
    return  total_words/total_sentences


def percentage_complex(text,cleaned_tokens):
    complexw = count_complex_words(cleaned_tokens)
    total_words = len(cleaned_tokens)
    return complexw/total_words


def fog_index(text,cleaned_tokens):
    perc = percentage_complex(text,cleaned_tokens)
    sent_len = average_sentence_length(text,cleaned_tokens)
    fi = 0.4*(sent_len+perc)
    return fi


def average_wordspersent(text):
    total_sentences = len(sent_tokenize(text))
    total_words = len(word_tokenize(text))
    return  total_words/total_sentences



def count_complex_words(cleaned_tokens):
    complex_words = 0
    for token in cleaned_tokens:
        if syllable_count(token)>2:
             complex_words+=1
    return complex_words



def word_count(cleaned_tokens):
    return len(cleaned_tokens)




def syllable_count(word):
    vowels = "aeiou"
    count = 0

    if word.endswith("es") or word.endswith("ed"):
        word = word[:-2]

    for char in word:
        if char.lower() in vowels:
            count += 1

    return count



def total_syllable(cleaned_tokens):
    syll_count =0;
    for token in cleaned_tokens:
        ct = syllable_count(token)
        syll_count = syll_count+ct
    return syll_count




def pers_pronouns(personal_pronouns,text):
    tokens = word_tokenize(text)
    total_personal_pronouns = sum(1 for token in tokens if token in personal_pronouns)
    return total_personal_pronouns


def avg_wordlen(cleaned_tokens):
    total_char_sum = 0
    for token in cleaned_tokens:
        char_sum = sum(1 for char in token)
        total_char_sum = total_char_sum + char_sum
    return total_char_sum/len(cleaned_tokens)


def main():

    print('hello')
    df = pd.read_excel('./Input.xlsx')

    path_name = './Input.csv'
    with open(path_name,'r') as file:
        csv_reader = csv.DictReader(file)
        for csv_row in csv_reader:
            print("url-> "+csv_row['URL'])
            print("urlid-> "+csv_row['URL_ID'])
            urlid = csv_row['URL_ID']
            scrape(csv_row['URL'],urlid)


    
    document_dir = './solution'
    documents = []
    for file_name in os.listdir(document_dir):
        if file_name.startswith("blackassign"):
            with open(os.path.join(document_dir, file_name), 'r') as file:
                org_text = file.read()
                documents.append({'file_name': file_name, 'text': org_text.lower()})

    stop_words = set()
    stop_words_directory = './stopwordslists'
    for filename in os.listdir(stop_words_directory):
        if filename.endswith(".txt"):
            with open(os.path.join(stop_words_directory, filename), 'r', encoding='latin-1') as file:
                for word in file.read().splitlines():
                    stop_words.add(word.lower())

    positive_words = set()
    file1_path = './positive-words.txt' 
    with open(file1_path, 'r') as file1:
        for word in file1.read().splitlines():
            positive_words.add(word.lower())

    negative_words = set()
    file2_path = './negative-words.txt' 
    with open(file2_path, 'r', encoding='latin-1') as file2:
        for word in file2.read().splitlines():
            negative_words.add(word.lower())

    personal_pronouns =['i', 'we', 'my', 'ours','us']

    for doc in documents:
        text = doc['text']
        cleaned_tokens = clean_tokens(text, stop_words)    
        doc['POSITIVE SCORE'] = calculate_positive_score(cleaned_tokens, positive_words)
        doc['NEGATIVE SCORE'] = calculate_negative_score(cleaned_tokens, negative_words)
        doc['POLARITY SCORE'] = polarity_score(cleaned_tokens, positive_words, negative_words)
        doc['SUBJECTIVITY SCORE'] = subjectivity_score(cleaned_tokens, positive_words, negative_words)
        doc['AVG SENTENCE LENGTH'] = average_sentence_length(text, cleaned_tokens)
        doc['PERCENTAGE OF COMPLEX WORDS'] = percentage_complex(text, cleaned_tokens)
        doc['FOG INDEX'] = fog_index(text, cleaned_tokens)
        doc['AVG NUMBER OF WORDS PER SENTENCE'] = average_wordspersent(text)
        doc['COMPLEX WORD COUNT'] = count_complex_words(cleaned_tokens)
        doc['WORD COUNT'] = word_count(cleaned_tokens)
        doc['SYLLABLE PER WORD'] = total_syllable(cleaned_tokens)
        doc['PERSONAL PRONOUNS'] = pers_pronouns(personal_pronouns, text)
        doc['AVG WORD LENGTH'] = avg_wordlen(cleaned_tokens)

    df = pd.DataFrame(documents)
    df = df.rename(columns={'file_name':'URL_ID'})
    df.drop('text', axis=1, inplace=True)
    df2 =  pd.read_excel('./Input.xlsx')
    final_df = pd.merge(df2,df)
    final_df.to_csv('./Bhumika_results.csv', index=False)
    print('saving final dataframe')
    
main()



