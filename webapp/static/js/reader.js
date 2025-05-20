// === Grab UI Elements ===
const textBox = document.getElementById('text-box');
const sentenceText = document.getElementById('sentence-text');
const page = document.getElementById('page');

const bgColor = document.getElementById('bgColor');
const textColor = document.getElementById('textColor');
const fontSize = document.getElementById('fontSize');
const fontFamily = document.getElementById('fontFamily');
const themeSwitch = document.getElementById('themeSwitch');
const progressBar = document.getElementById('progress-bar');
const progressLabel = document.getElementById('progress-label');

const prevBtn = document.getElementById('prevBtn');
const nextBtn = document.getElementById('nextBtn');

// === Initialize Progress Tracking from Local Storage ===
let currentIndex = parseInt(localStorage.getItem("sentenceIndex")) || 1;
let totalSentences = parseInt(localStorage.getItem("totalSentences")) || 1;

// === Applies User UI Settings (Theme, Font, Color, etc.) ===
function applySettings(save = true) {
    const bg = bgColor.value;
    const fg = textColor.value;
    const fs = fontSize.value + "px";
    const ff = fontFamily.value;

    // Remove any Bootstrap theme classes before applying custom styles
    textBox.classList.remove("bg-dark", "text-light", "bg-light", "text-dark");

    // Apply custom colors and font to the text box
    textBox.style.setProperty("background-color", bg, "important");
    sentenceText.style.setProperty("color", fg, "important");
    sentenceText.style.setProperty("font-size", fs, "important");
    sentenceText.style.setProperty("font-family", ff, "important");

    // Toggle between dark and light themes
    if (themeSwitch.checked) {
        page.classList.remove("theme-light");
        page.classList.add("theme-dark");
    } else {
        page.classList.remove("theme-dark");
        page.classList.add("theme-light");
    }

    // Optionally save settings to localStorage
    if (save) {
        localStorage.setItem("settings", JSON.stringify({
            bg,
            color: fg,
            size: fontSize.value,
            font: ff,
            dark: themeSwitch.checked
        }));
    }
}

// === Load Settings on Page Load from Local Storage ===
function loadSettings() {
    const settings = JSON.parse(localStorage.getItem("settings"));
    if (settings) {
        bgColor.value = settings.bg;
        textColor.value = settings.color;
        fontSize.value = settings.size;
        fontFamily.value = settings.font;
        themeSwitch.checked = settings.dark;
        applySettings(false);
    } else {
        // Defaults if no saved settings
        bgColor.value = "#212529";
        textColor.value = "#e0e0e0";
        fontSize.value = 20;
    }
    applySettings(false);
}

// === Update Sentence & Chapter Progress Bars ===
function updateProgress() {
    if (totalSentences > 1) {
        const percent = Math.min(100, (currentIndex / totalSentences) * 100);
        document.getElementById("sentence-progress-bar").style.width = percent + "%";
        progressLabel.innerText = `Sentence ${currentIndex} of ${totalSentences}`;
    } else {
        document.getElementById("sentence-progress-bar").style.width = "100%";
        progressLabel.innerText = "Sentence 1 of 1";
    }

    // Update chapter progress
    const chapterList = Array.from(document.getElementById("chapterSelect").options).map(opt => opt.value);
    const currentChapter = document.getElementById("chapterSelect").value;
    const chapterIndex = chapterList.indexOf(currentChapter) + 1;
    const totalChapters = chapterList.length;

    const chapterPercent = (chapterIndex / totalChapters) * 100;
    document.getElementById("chapter-progress-bar").style.width = chapterPercent + "%";
    document.getElementById("chapter-progress-label").innerText = `Chapter ${chapterIndex} of ${totalChapters}`;
}

// === Sync Sentence Progress to Local Storage ===
function syncProgress() {
    localStorage.setItem("sentenceIndex", currentIndex);
    localStorage.setItem("totalSentences", totalSentences);
    updateProgress();
}

// === Change Chapter by Redirecting Page ===
const chapterSelect = document.getElementById("chapterSelect");

if (chapterSelect) {
    chapterSelect.addEventListener("change", () => {
        const selectedChapter = chapterSelect.value;
        const currentNovel = new URLSearchParams(window.location.search).get("novel");
        // Redirect to the new chapter page
        window.location.href = `/read?novel=${encodeURIComponent(currentNovel)}&chapter=${encodeURIComponent(selectedChapter)}`;
    });
}

// === Keyboard Navigation Support ===
document.addEventListener("keydown", function (e) {
    if (e.key === "ArrowRight") nextBtn.click();
    if (e.key === "ArrowLeft") prevBtn.click();
});

// === UI Settings Change Listeners ===
bgColor.addEventListener('input', () => applySettings());
textColor.addEventListener('input', () => applySettings());
fontSize.addEventListener('input', () => applySettings());
fontFamily.addEventListener('change', () => applySettings());
themeSwitch.addEventListener('change', () => applySettings());

/**
 * Asynchronous function to navigate to next/previous sentence.
 * This is like "background threading" in Python — it fetches data from server without blocking the UI.
 */
async function navigateSentence(direction) {
    const url = direction === 'next' ? '/api/next' : '/api/prev';

    // Disable navigation buttons while fetching
    setNavButtonsState(true);

    try {
        const res = await fetch(url);
        const data = await res.json();

        if (data.sentence) {
            sentenceText.textContent = data.sentence;
            currentIndex = data.index;
            totalSentences = data.total;
            syncProgress();

            // Disable prev if first sentence; disable next if last sentence
            prevBtn.disabled = currentIndex <= 1;
            nextBtn.disabled = currentIndex >= totalSentences;

            // Automatically go to next chapter if it's the last sentence
            if (direction === 'next' && currentIndex === totalSentences) {
                setTimeout(() => {
                    goToNextChapter();
                }, 800);
            }
        }
    } catch (err) {
        console.error("Failed to load sentence:", err);
    } finally {
        // Only re-enable buttons if not at ends
        if (currentIndex > 1) prevBtn.disabled = false;
        if (currentIndex < totalSentences) nextBtn.disabled = false;
    }
}


// === Automatically Moves to the Next Chapter or Shows Modal if None Left ===
function goToNextChapter() {
    fetch('/api/next_chapter')
        .then(res => {
            if (res.redirected) {
                // Redirect to new chapter if available
                window.location.href = res.url;
            } else {
                // Otherwise, show end-of-novel modal
                const endModal = new bootstrap.Modal(document.getElementById('endModal'));
                endModal.show();
            }
        });
}

// === Button Event Listeners for Sentence Navigation ===
nextBtn.addEventListener("click", e => {
    e.preventDefault();
    navigateSentence('next');
});

prevBtn.addEventListener("click", e => {
    e.preventDefault();
    navigateSentence('prev');
});
// === disable buttons for Sentence Navigation ===
function setNavButtonsState(disabled) {
    nextBtn.disabled = disabled;
    prevBtn.disabled = disabled;
}

/**
 * Initialize sentence on page load
 * Similar to a background thread fetching initial content from backend
 */
async function initSentence() {
    try {
        const res = await fetch('/api/init');  // Initial data load from server
        const data = await res.json();
        if (data.sentence) {
            sentenceText.textContent = data.sentence;
            currentIndex = data.index;
            totalSentences = data.total;
            syncProgress();
        }
    } catch (err) {
        console.error("Init failed:", err);
    }
}

// === On Page Load: Apply Settings and Load Sentence ===
loadSettings();
initSentence();
updateProgress();
