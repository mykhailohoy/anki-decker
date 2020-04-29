# anki-decker

An app to generate Anki decks from wordlist for the German language.
 
To run the application, you will need to install selenium at your device.
Use the given wordlist (it's B2) or paste your own one (currently only 'Aspekte neu' format is supported) to the file wordlist.txt.
Now, open main.py and set variables `start_at` and `stop_at` (these are line 8 and 9) to desired values.

Run the file. You get deck.txt file, that can be imported into Anki app. Change encoding to utf-8 if necessary.