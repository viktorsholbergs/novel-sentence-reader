import os
from flask import Flask, render_template, request, redirect, url_for, session
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

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
        self.load(filepath)

    def load(self, filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
        sentences = [s.strip() + '.' for s in text.replace('\n', ' ').split('.') if s.strip()]
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

    def get(self):
        return self.current.sentence if self.current else "The End."

    def next(self):
        if self.current and self.current.next:
            self.current = self.current.next

    def prev(self):
        if self.current and self.current.prev:
            self.current = self.current.prev


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

    chapters = sorted([f for f in os.listdir(novel_path) if f.endswith(".txt")])
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
    return render_template("reader.html", sentence=sentence_list.get(), novel=session.get('novel'), chapter=session.get('chapter'))

@app.route('/next')
def next_sentence():
    if sentence_list:
        sentence_list.next()
    return redirect(url_for("reader"))

@app.route('/prev')
def prev_sentence():
    if sentence_list:
        sentence_list.prev()
    return redirect(url_for("reader"))

if __name__ == '__main__':
    app.run(debug=True)
