import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
import re
app = Flask(__name__)
app.secret_key = "secret"

NOVEL_DIR = os.path.join(os.path.dirname(__file__), "novels")


# ---------- Linked List for Sentence Navigation ----------

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


# --------- Global Sentence Manager (per session would be better for multi-user) ---------
sentence_list = None


# ---------- Routes ----------

@app.route('/')
def home():
    novels = sorted(os.listdir(NOVEL_DIR))
    return render_template("select.html", novels=novels)

@app.route('/chapters')
def select_chapter():
    novel = request.args.get('novel')
    novel_path = os.path.join(NOVEL_DIR, novel)
    if not os.path.isdir(novel_path):
        return "Novel not found", 404

    def extract_chapter_number(name):
        match = re.search(r'(\d+)', name)
        return int(match.group(1)) if match else float('inf')

    chapters = sorted(
        [f for f in os.listdir(novel_path) if f.endswith(".txt")],
        key=extract_chapter_number
    )
    return render_template("select.html", novels=sorted(os.listdir(NOVEL_DIR)), chapters=chapters, selected_novel=novel)


@app.route('/read')
def read():
    global sentence_list
    novel = request.args.get("novel")
    chapter = request.args.get("chapter")

    path = os.path.join(NOVEL_DIR, novel, chapter)
    if not os.path.exists(path):
        return "Chapter not found", 404

    sentence_list = SentenceList(path)
    session['novel'] = novel
    session['chapter'] = chapter
    return redirect(url_for("reader"))

@app.route('/reader')
def reader():
    if not sentence_list:
        return redirect(url_for("home"))

    novel = session.get('novel')
    chapter = session.get('chapter')

    chapter_list = sorted([f for f in os.listdir(os.path.join(NOVEL_DIR, novel)) if f.endswith('.txt')])

    return render_template("reader.html",
                           sentence=sentence_list.get(),
                           novel=novel,
                           chapter=chapter,
                           chapters=chapter_list)


@app.route('/api/next')
def api_next():
    if sentence_list:
        sentence_list.next()
        sentence = sentence_list.get()
        return jsonify({
            "sentence": sentence,
            "index": sentence_list.index,
            "total": sentence_list.total
        })
    return jsonify({"error": "No sentence list loaded"}), 400

@app.route('/api/prev')
def api_prev():
    if sentence_list:
        sentence_list.prev()
        sentence = sentence_list.get()
        return jsonify({
            "sentence": sentence,
            "index": sentence_list.index,
            "total": sentence_list.total
        })
    return jsonify({"error": "No sentence list loaded"}), 400

@app.route('/api/init')
def api_init():
    if sentence_list:
        return jsonify({
            "sentence": sentence_list.get(),
            "index": sentence_list.index,
            "total": sentence_list.total
        })
    return jsonify({"error": "No sentence list"}), 400

@app.route('/api/next_chapter')
def api_next_chapter():
    global sentence_list
    novel = session.get('novel')
    chapter = session.get('chapter')
    if not (novel and chapter):
        return "Session missing", 400

    chapter_list = sorted([f for f in os.listdir(os.path.join(NOVEL_DIR, novel)) if f.endswith('.txt')])
    try:
        idx = chapter_list.index(chapter)
        if idx + 1 < len(chapter_list):
            next_chapter = chapter_list[idx + 1]
            path = os.path.join(NOVEL_DIR, novel, next_chapter)
            sentence_list = SentenceList(path)
            session['chapter'] = next_chapter
            return redirect(url_for('reader'))
    except ValueError:
        pass

    return "No next chapter", 404
if __name__ == '__main__':
    app.run(debug=True)
