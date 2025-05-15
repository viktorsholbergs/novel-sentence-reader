from flask import Flask, render_template, request, redirect, url_for, session
import os

app = Flask(__name__)
app.secret_key = "secret"

# ----------- Linked List Data Structure -----------

class SentenceNode:
    def __init__(self, sentence):
        self.sentence = sentence
        self.next = None
        self.prev = None

class SentenceList:
    def __init__(self, text_path):
        self.head = None
        self.tail = None
        self.current = None
        self.load_sentences(text_path)

    def load_sentences(self, path):
        with open(path, "r", encoding="utf-8") as file:
            text = file.read()

        sentences = [s.strip() for s in text.replace('\n', ' ').split('.') if s.strip()]
        prev_node = None
        for sentence in sentences:
            node = SentenceNode(sentence + '.')
            if not self.head:
                self.head = node
            else:
                prev_node.next = node
                node.prev = prev_node
            prev_node = node
        self.tail = prev_node
        self.current = self.head

    def get_current(self):
        return self.current.sentence if self.current else "The End."

    def move_next(self):
        if self.current and self.current.next:
            self.current = self.current.next

    def move_prev(self):
        if self.current and self.current.prev:
            self.current = self.current.prev


# Store sentence lists in memory (can later extend to per-user sessions)
sentence_list = SentenceList("chapters/chapter_1.txt")

# ----------- Flask Routes -----------

@app.route('/')
def index():
    return redirect(url_for('reader'))

@app.route('/read')
def reader():
    sentence = sentence_list.get_current()
    return render_template('reader.html', sentence=sentence)

@app.route('/next')
def next_sentence():
    sentence_list.move_next()
    return redirect(url_for('reader'))

@app.route('/prev')
def prev_sentence():
    sentence_list.move_prev()
    return redirect(url_for('reader'))

if __name__ == '__main__':
    app.run(debug=True)
