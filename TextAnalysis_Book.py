from pdfminer.pdfparser import PDFParser
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfpage import PDFTextExtractionNotAllowed
from pdfminer.pdfinterp import PDFResourceManager
from pdfminer.pdfinterp import PDFPageInterpreter
from pdfminer.pdfdevice import PDFDevice
from pdfminer.layout import LAParams, LTTextBox, LTTextLine
from pdfminer.converter import PDFPageAggregator
from pdfminer.converter import TextConverter

# import pandas as pd 
import pandas as pd

import io
from io import StringIO

# Import spaCy and load the language library
import spacy
nlp = spacy.load('en_core_web_lg')

spacy_stopwords = spacy.lang.en.stop_words.STOP_WORDS
print (len(spacy_stopwords))

#TODO book names to be added in stop word
customize_stop_words = ['a', 'b', 'c', 'd', 'e','f', 'g', 'h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','’s','A', 'B', 'C', 'D', 'E','F', 'G', 'H','I','J','K','L','M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z', '3/27/2017', 'Book-3.indd','PM','FA','SA','etc','n’t','English','Channel']
for w in customize_stop_words:
    nlp.vocab[w].is_stop = True

def ReadPDFBook (pdf_document):
    # Open and read the pdf file in binary mode
    fp = open(pdf_document, "rb")

    # Create parser object to parse the pdf content
    parser = PDFParser(fp)

    # Store the parsed content in PDFDocument object
    document = PDFDocument(parser)

    # Create PDFResourceManager object that stores shared resources such as fonts or images
    rsrcmgr = PDFResourceManager()

    # set parameters for analysis
    laparams = LAParams()

    # Create a PDFDevice object which translates interpreted information into desired format
    # Device needs to be connected to resource manager to store shared resources
    # device = PDFDevice(rsrcmgr)
    # Extract the decive to page aggregator to get LT object elements
    device = PDFPageAggregator(rsrcmgr, laparams=laparams)

    # Create interpreter object to process page content from PDFDocument
    # Interpreter needs to be connected to resource manager for shared resources and device 
    interpreter = PDFPageInterpreter(rsrcmgr, device)

    extracted_text = ''

    # Ok now that we have everything to process a pdf document, lets process it page by page
    for page in PDFPage.create_pages(document):
        # As the interpreter processes the page stored in PDFDocument object
        interpreter.process_page(page)
        # The device renders the layout from interpreter
        layout = device.get_result()
        # Out of the many LT objects within layout, we are interested in LTTextBox and LTTextLine
        for lt_obj in layout:
            if isinstance(lt_obj, LTTextBox) or isinstance(lt_obj, LTTextLine):
                extracted_text += lt_obj.get_text()

    #close the pdf file
    fp.close()
    
    return extracted_text
   
   book1 = 'NCERT/Books/Class3/English/Marigold/Marigold_NCERT_Class3.pdf'
book2 = 'NCERT/Books/Class4/English/Marigold/Marigold_NCERT_Class4.pdf'
book3 = 'NCERT/Books/Class4/EVS/lookingaround/LokingAround_Class4.pdf'

extracted_text_book1 = ReadPDFBook(book1)
extracted_text_book2 = ReadPDFBook(book2)
extracted_text_book3 = ReadPDFBook(book3)

print (len(extracted_text_book1))
print (len(extracted_text_book2))
print (len(extracted_text_book3))

# Create a Doc object and explore tokens
doc1 = nlp(extracted_text_book1)
doc2 = nlp(extracted_text_book2)
doc3 = nlp(extracted_text_book3)

print (len(doc1))
print (len(doc2))
print (len(doc3))

print(len(list(doc1.sents)))
print(len(list(doc2.sents)))
print(len(list(doc3.sents)))

from __future__ import unicode_literals
from collections import Counter

def ReleventToken(doc):
    final_tokens = [token for token in doc if not token.is_space | token.is_bracket | token.is_stop | token.is_digit  | token.is_quote | token.is_left_punct | token.is_punct | token.is_right_punct | token.is_quote | token.like_url | token.like_num]
    #print (final_tokens)
    print (len(final_tokens))
    c = Counter([token.pos_ for token in final_tokens])
    #sbase = sum(c.values())
    #array = [[int(j) for j in el] for i in c.items()]
    row = 0
    multi_list = [[0] * 2 for i in c.items()]
    for el, cnt in c.items():
        multi_list[row] [0]= el
        multi_list[row] [1]= cnt
        row = row + 1
    return final_tokens, multi_list
    
   final_tokens_book1, multi_list1 = ReleventToken(doc1)
final_tokens_book2, multi_list2 = ReleventToken(doc2)
final_tokens_book3, multi_list3 = ReleventToken(doc3)

final_tokens_book1_df = pd.DataFrame(multi_list1, columns=['parts_of_speech', 'count'])
final_tokens_book2_df = pd.DataFrame(multi_list2, columns=['parts_of_speech', 'count'])
final_tokens_book3_df = pd.DataFrame(multi_list3, columns=['parts_of_speech', 'count'])

final_tokens_book = pd.merge(final_tokens_book1_df, final_tokens_book2_df, how ='outer', on = 'parts_of_speech') 
final_tokens_book = pd.merge(final_tokens_book, final_tokens_book3_df, how ='outer', on = 'parts_of_speech') 
final_tokens_book.head(15)

def MostCommonWords(final_tokens):
    words = [token.text for token in final_tokens]
    word_freq = Counter(words)
    common_words = word_freq.most_common(100)
    #print (common_words)
    return common_words 
    
 common_words_book1 = MostCommonWords(final_tokens_book1)
common_words_book2 = MostCommonWords(final_tokens_book2)
common_words_book3 = MostCommonWords(final_tokens_book3)

common_words_book1_df = pd.DataFrame(common_words_book1, columns=['words', 'count'])
common_words_book2_df = pd.DataFrame(common_words_book2, columns=['words', 'count'])
common_words_book3_df = pd.DataFrame(common_words_book3, columns=['words', 'count'])

final_common_words_book_df = pd.merge(common_words_book1_df, common_words_book2_df, how ='outer', on = 'words') 
final_common_words_book_df = pd.merge(final_common_words_book_df, common_words_book3_df, how ='outer', on = 'words')
final_common_words_book_df.head(50)

final_common_words_book_df.tail(50)

