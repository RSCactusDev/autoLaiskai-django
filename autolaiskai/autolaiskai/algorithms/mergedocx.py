# Code source: https://stackoverflow.com/questions/24872527/combine-word-document-using-python-docx
from docxcompose.composer import Composer
from docx import Document as Document_compose

def mergedocx(letter_first, letter_second, output_file):
    master = Document_compose(letter_first)
    composer = Composer(master)
    doc2 = Document_compose(letter_second)
    # append the doc2 into the master using composer.append function
    composer.append(doc2)
    output =  output_file    
    #Save the combined docx with a name
    return  composer.save(output)
