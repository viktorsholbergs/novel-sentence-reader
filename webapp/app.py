import os  # Provides functions to interact with the operating system
import json  # Used for reading and writing JSON files
from flask import Flask, render_template, request, redirect, url_for, session, jsonify  # Flask modules for web app functionality
from selenium import webdriver  # Used to control a browser programmatically
from selenium.webdriver.chrome.service import Service  # Helps configure ChromeDriver as a service
from selenium.webdriver.common.by import By  # Enum-like class for selecting elements in the DOM
import re  # Regular expressions for string pattern matching
from lightnovel_scraper import LightNovelScraper  # Custom class to scrape novel chapters

app = Flask(__name__)  # Create a Flask application instance
app.secret_key = "secret"  # Secret key for session encryption

# Define paths for novels directory and progress-tracking file
NOVEL_DIR = os.path.join(os.path.dirname(__file__), "novels")
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.json")

# Node in a doubly linked list storing one sentence
class SentenceNode:
    def __init__(self, sentence):
        self.sentence = sentence  # The sentence text
        self.next = None  # Pointer to the next node
        self.prev = None  # Pointer to the previous node

# A doubly linked list of sentences
class SentenceList:
    def __init__(self, filepath):
        self.head = None  # First node
        self.tail = None  # Last node
        self.current = None  # Currently focused node
        self.index = 1  # Index of the current sentence
        self.total = 0  # Total number of sentences
        self.load(filepath)  # Load the sentences from a file

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()  # Read the full chapter text
        # Split the text into sentences using '.' as a delimiter
        sentences = [s.strip() + '.' for s in text.replace('\n', ' ').split('.') if s.strip()]
        self.total = len(sentences)  # Store sentence count
        prev_node = None
        for sentence in sentences:
            node = SentenceNode(sentence)  # Create a new node
            if not self.head:
                self.head = node  # Set head if first node
            else:
                prev_node.next = node  # Link previous node to this
                node.prev = prev_node  # Link back to previous
            prev_node = node
        self.tail = prev_node  # Store the tail
        self.current = self.head  # Start at the beginning
        self.index = 1  # Reset index

    def get(self):
        return self.current.sentence if self.current else "The End."  # Return the current sentence

    def next(self):
        if self.current and self.current.next:
            self.current = self.current.next  # Move forward
            self.index += 1

    def prev(self):
        if self.current and self.current.prev:
            self.current = self.current.prev  # Move backward
            self.index -= 1

    def is_last(self):
        return self.current == self.tail  # Check if at the last sentence

    def set_index(self, index):
        if index < 1 or index > self.total:
            return  # Invalid index
        self.current = self.head
        self.index = 1
        while self.index < index:
            self.next()  # Move to desired index

sentence_list = None  # Global variable for current SentenceList

# Load progress from progress.json
def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

# Save reading progress to file
def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)

# Get a list of sorted chapters for a given novel
def get_sorted_chapters(novel_name):
    novel_path = os.path.join(NOVEL_DIR, novel_name)
    if not os.path.exists(novel_path):
        print(f"[ERROR] Novel path does not exist: {novel_path}")
        return []
    files = os.listdir(novel_path)
    chapters = [f for f in files if f.lower().startswith("chapter_") and f.endswith(".txt")]

    def extract_number(ch):
        try:
            return int(ch.lower().replace("chapter_", "").replace(".txt", ""))
        except ValueError:
            return float('inf')

    sorted_chapters = sorted(chapters, key=extract_number)  # Sort by chapter number
    print(f"[DEBUG] Sorted chapters for '{novel_name}'")
    return sorted_chapters

# Homepage showing available novels and reading progress
@app.route('/')
def home():
    novels = sorted(os.listdir(NOVEL_DIR))
    progress = load_progress()
    novel_data = []
    for novel in novels:
        novel_path = os.path.join(NOVEL_DIR, novel)
        if os.path.isdir(novel_path):
            chapters = get_sorted_chapters(novel)
            if chapters:
                first_chapter = chapters[0]
                if novel in progress and "last_chapter" in progress[novel]:
                    last_chapter = progress[novel]["last_chapter"]
                    link = url_for('read', novel=novel, chapter=last_chapter)
                    button_text = "Continue reading"
                else:
                    link = url_for('read', novel=novel, chapter=first_chapter)
                    button_text = "Start reading"
                novel_data.append({"name": novel, "link": link, "button_text": button_text})
    return render_template("select.html", novel_data=novel_data)

# Begin reading a specific chapter
@app.route('/read')
def read():
    global sentence_list
    novel = request.args.get("novel")
    chapter = request.args.get("chapter")
    path = os.path.join(NOVEL_DIR, novel, chapter)
    if not os.path.exists(path):
        return "Chapter not found", 404
    sentence_list = SentenceList(path)
    progress = load_progress()
    if novel in progress and "chapters" in progress[novel] and chapter in progress[novel]["chapters"]:
        sentence_index = progress[novel]["chapters"][chapter]
        sentence_list.set_index(sentence_index)
    else:
        sentence_list.set_index(1)
    session['novel'] = novel
    session['chapter'] = chapter
    return redirect(url_for("reader"))

# Display the reader interface
@app.route('/reader')
def reader():
    if not sentence_list:
        return redirect(url_for("home"))
    novel = session.get('novel')
    chapter = session.get('chapter')
    chapters = get_sorted_chapters(novel)
    return render_template("reader.html", sentence=sentence_list.get(), novel=novel, chapter=chapter, chapters=chapters)

# API endpoint to get the next sentence
@app.route('/api/next')
def api_next():
    if sentence_list:
        sentence_list.next()
        sentence = sentence_list.get()
        index = sentence_list.index
        total = sentence_list.total
        novel = session.get('novel')
        chapter = session.get('chapter')
        if novel and chapter:
            progress = load_progress()
            if novel not in progress:
                progress[novel] = {"chapters": {}, "last_chapter": chapter}
            if "chapters" not in progress[novel]:
                progress[novel]["chapters"] = {}
            progress[novel]["chapters"][chapter] = index
            progress[novel]["last_chapter"] = chapter
            save_progress(progress)
        return jsonify({"sentence": sentence, "index": index, "total": total})
    return jsonify({"error": "No sentence list loaded"}), 400

# API endpoint to get the previous sentence
@app.route('/api/prev')
def api_prev():
    if sentence_list:
        sentence_list.prev()
        sentence = sentence_list.get()
        index = sentence_list.index
        total = sentence_list.total
        novel = session.get('novel')
        chapter = session.get('chapter')
        if novel and chapter:
            progress = load_progress()
            if novel not in progress:
                progress[novel] = {"chapters": {}, "last_chapter": chapter}
            if "chapters" not in progress[novel]:
                progress[novel]["chapters"] = {}
            progress[novel]["chapters"][chapter] = index
            progress[novel]["last_chapter"] = chapter
            save_progress(progress)
        return jsonify({"sentence": sentence, "index": index, "total": total})
    return jsonify({"error": "No sentence list loaded"}), 400

# API endpoint to initialize sentence data
@app.route('/api/init')
def api_init():
    if sentence_list:
        sentence = sentence_list.get()
        index = sentence_list.index
        total = sentence_list.total
        novel = session.get('novel')
        chapter = session.get('chapter')
        if novel and chapter:
            progress = load_progress()
            if novel not in progress:
                progress[novel] = {"chapters": {}, "last_chapter": chapter}
            if "chapters" not in progress[novel]:
                progress[novel]["chapters"] = {}
            progress[novel]["chapters"][chapter] = index
            progress[novel]["last_chapter"] = chapter
            save_progress(progress)
        return jsonify({"sentence": sentence, "index": index, "total": total})
    return jsonify({"error": "No sentence list"}), 400

# Load the next chapter in the sequence
@app.route('/api/next_chapter')
def api_next_chapter():
    global sentence_list
    novel = session.get('novel')
    chapter = session.get('chapter')
    if not (novel and chapter):
        return "Session missing", 400

    chapter_list = get_sorted_chapters(novel)

    def extract_number(name):
        match = re.search(r'\d+', name)
        return int(match.group()) if match else -1

    current_num = extract_number(chapter)
    idx = next((i for i, ch in enumerate(chapter_list) if extract_number(ch) == current_num), None)
    if idx is not None and idx + 1 < len(chapter_list):
        next_chapter = chapter_list[idx + 1]
        path = os.path.join(NOVEL_DIR, novel, next_chapter)
        sentence_list = SentenceList(path)
        session['chapter'] = next_chapter
        return redirect(url_for('reader'))

    return "No next chapter", 404

# Add a new novel by scraping it from a link
@app.route('/add_novel', methods=['POST'])
def add_novel():
    link = request.form['link']
    try:
        scraper = LightNovelScraper()
        scraper.scrape_from(link)
        return redirect(url_for('select'))
    except Exception as e:
        return f"Error adding novel: {str(e)}", 500

# Start the Flask server
if __name__ == '__main__':
    app.run(debug=True)