# -*- coding: utf-8 -*-

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import re

# how many words do you need?
start_at = 356
stop_at = 500

def main():
  with open("wordlist.txt", encoding="utf_8", mode="r") as f:
    for word_count, line in enumerate(f, 1):
      if word_count >= start_at and word_count <= stop_at:
        # line = 'ausgerechnet'
        print(line)
        src_full_word = re.sub("\n", "", line.split("(")[0])
        src_word = line.split()[0].split(",")[0].split("/")[0]
        src_native_example_sentence = None
        if find_native_example_sentence(line):
          src_native_example_sentence = find_native_example_sentence(line)
        else:
          src_native_example_sentence = None

        options = Options()
        options.add_argument("--headless")
        options.add_argument("--ignore-certificate-errors")
        driver = webdriver.Chrome(executable_path="chromedriver.exe", options=options)

        bonus_sentences = None
        # if there is content between parentheses, in our case custom example sentence
        if src_native_example_sentence:
          # getting text to pass to url at reverso
          encoded_sentence = re.sub("(etw\.)|(jmd\.)|(/)|(die)|(der)(das)", "", src_native_example_sentence).replace(" ", "+")
          driver.get(f"https://context.reverso.net/translation/german-english/{encoded_sentence}")
          # looking for sentences that actually include the source word
          src_sentences = [e for e in driver.find_elements_by_css_selector("div.example>div.src.ltr") if e.text.find(src_word) != -1]
          if len(src_sentences) > 0:
            src_sentence, trg_sentence, bonus_sentences = find_sentences(src_sentences, driver)
          else:
            # if such sentence is not found fallback
            src_sentence = src_native_example_sentence
            driver.get(f'https://translate.google.com/#view=home&op=translate&sl=de&tl=en&text={src_sentence.lower()}')
            trg_sentence = driver.find_element_by_css_selector("span.tlid-translation.translation")
            trg_sentence = trg_sentence.text

          # getting word translation from google
          driver.get("https://www.google.com") # driver doesn't refresh for some reason, working around the situation
          driver.get(f'https://translate.google.com/#view=home&op=translate&sl=de&tl=en&text={src_word.lower()}')
          trg_word = driver.find_element_by_css_selector("span.tlid-translation.translation")
          trg_word = trg_word.text
        else:
          print("==================", src_word)
          driver.get(f"https://context.reverso.net/translation/german-english/{src_word}")
          try:
            trg_word = driver.find_element_by_css_selector("a.translation.ltr.dict")
            trg_word = trg_word.text
          except Exception:
            try:
              trg_word = driver.find_element_by_css_selector("div.translation.ltr.dict")
              trg_word = trg_word.text
            except Exception:
              driver.get(f'https://translate.google.com/#view=home&op=translate&sl=de&tl=en&text={src_word.lower()}')
              trg_word = driver.find_element_by_css_selector("span.tlid-translation.translation")
              trg_word = trg_word.text
              driver.get(f"https://context.reverso.net/translation/german-english/{src_word}")

          src_sentences = driver.find_elements_by_css_selector("div.example > div.src.ltr")
          try:
            src_sentence, trg_sentence, bonus_sentences = find_sentences(src_sentences, driver)
          except:
            print("=============================================================================================================================================================================================================================================================================================================================================================================================================", word_count)
        write_to_file('deck.txt', src_full_word, trg_word, src_sentence, trg_sentence, word_count, bonus_sentences)
        print("============", src_word, ":", trg_word, ":", src_sentence, ":", trg_sentence)



def find_sentences(sentences_list, driver):
  print("====================", sentences_list)
  bonus_sentences = None
  for i in range(len(sentences_list)):
    local_src_sentence = sentences_list[i].text
    script = "return arguments[0].nextElementSibling"
    local_trg_sentence = driver.execute_script(script, sentences_list[i]).text
    # first sentence in the list will be default
    # next ones will be bonus sentence
    if i == 0:
      src_sentence = local_src_sentence
      trg_sentence = local_trg_sentence
    else:
      bonus_sentences = []
      bonus_sentences.append([local_src_sentence, local_trg_sentence])
  return src_sentence, trg_sentence, bonus_sentences
    

def find_native_example_sentence(line):
  native_example_sentences = [i for i in re.findall("\(([^()]*)\)", line) if sentence_valid(i)]
  if len(native_example_sentences) != 0:
    return native_example_sentences[0]
  else:
    return None

def write_to_file(filename, src_word, trg_word, src_sentence, trg_sentence, word_count, bonus_sentences_list=None):
  with open(filename, "a") as f:
    f.write(f"{src_word}\t{trg_word}\t{src_sentence}\t{trg_sentence}\t{word_count}\t")
    if bonus_sentences_list:
      for i in bonus_sentences_list:
        f.write("<br>".join(i))
        f.write("<br><br>")
    f.write("\n")

def sentence_valid(str):
  forbidden = ("Sg.", "Pl.", "+", "ohne Artikel")
  for e in forbidden:
    if str.find(e) != -1:
      return False
  else:
    if str == "sich":
      return False
    else:
      return True
  

main()