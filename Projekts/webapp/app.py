import os
import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
from lightnovel_scraper import LightNovelScraper
app = Flask(__name__)
app.secret_key = "secret"

NOVEL_DIR = os.path.join(os.path.dirname(__file__), "novels")
PROGRESS_FILE = os.path.join(os.path.dirname(__file__), "progress.json")



class SentenceNode:
    def __init__(self, sentence):
        self.sentence = sentence
        self.next = None
        self.prev = None

class SentenceList:
    def __init__(self, filepath):
        self.head = None
        self.tail = None
        self.current = None
        self.index = 1
        self.total = 0
        self.load(filepath)

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        sentences = [s.strip() + '.' for s in text.replace('\n', ' ').split('.') if s.strip()]
        self.total = len(sentences)
        prev_node = None
        for sentence in sentences:
            node = SentenceNode(sentence)
            if not self.head:
                self.head = node
            else:
                prev_node.next = node
                node.prev = prev_node
            prev_node = node
        self.tail = prev_node
        self.current = self.head
        self.index = 1

    def get(self):
        return self.current.sentence if self.current else "The End."

    def next(self):
        if self.current and self.current.next:
            self.current = self.current.next
            self.index += 1

    def prev(self):
        if self.current and self.current.prev:
            self.current = self.current.prev
            self.index -= 1

    def is_last(self):
        return self.current == self.tail

    def set_index(self, index):
        if index < 1 or index > self.total:
            return
        self.current = self.head
        self.index = 1
        while self.index < index:
            self.next()


sentence_list = None



def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_progress(data):
    with open(PROGRESS_FILE, "w") as f:
        json.dump(data, f)


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

    sorted_chapters = sorted(chapters, key=extract_number)
    print(f"[DEBUG] Sorted chapters for '{novel_name}'")
    return sorted_chapters


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
                novel_data.append({
                    "name": novel,
                    "link": link,
                    "button_text": button_text
                })
    return render_template("select.html", novel_data=novel_data)

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

@app.route('/reader')
def reader():
    if not sentence_list:
        return redirect(url_for("home"))
    novel = session.get('novel')
    chapter = session.get('chapter')
    chapters = get_sorted_chapters(novel)
    return render_template("reader.html",
                           sentence=sentence_list.get(),
                           novel=novel,
                           chapter=chapter,
                           chapters=chapters)

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
        return jsonify({
            "sentence": sentence,
            "index": index,
            "total": total
        })
    return jsonify({"error": "No sentence list loaded"}), 400

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
        return jsonify({
            "sentence": sentence,
            "index": index,
            "total": total
        })
    return jsonify({"error": "No sentence list loaded"}), 400

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
        return jsonify({
            "sentence": sentence,
            "index": index,
            "total": total
        })
    return jsonify({"error": "No sentence list"}), 400

@app.route('/api/next_chapter')
def api_next_chapter():
    global sentence_list
    novel = session.get('novel')
    print(novel)
    chapter = session.get('chapter')
    print(chapter)
    if not (novel and chapter):
        return "Session missing", 400

    chapter_list = get_sorted_chapters(novel)

    def extract_number(name):
        match = re.search(r'\d+', name)
        return int(match.group()) if match else -1

    current_num = extract_number(chapter)
    print(current_num)
    # Find the index based on the chapter number, not the string
    idx = next(
        (i for i, ch in enumerate(chapter_list) if extract_number(ch) == current_num),
        None
    )
    print(idx)
    if idx is not None and idx + 1 < len(chapter_list):
        next_chapter = chapter_list[idx + 1]
        path = os.path.join(NOVEL_DIR, novel, next_chapter)
        sentence_list = SentenceList(path)
        session['chapter'] = next_chapter
        print(next_chapter)
        return redirect(url_for('reader'))

    return "No next chapter", 404


@app.route('/add_novel', methods=['POST'])
def add_novel():
    link = request.form['link']
    try:
        scraper = LightNovelScraper()
        scraper.scrape_from(link)
        return redirect(url_for('select'))
    except Exception as e:
        return f"Error adding novel: {str(e)}", 500


if __name__ == '__main__':
    app.run(debug=True)