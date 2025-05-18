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

let currentIndex = parseInt(localStorage.getItem("sentenceIndex")) || 1;
let totalSentences = parseInt(localStorage.getItem("totalSentences")) || 1;

function applySettings(save = true) {
  const bg = bgColor.value;
  const fg = textColor.value;
  const fs = fontSize.value + "px";
  const ff = fontFamily.value;

  // Remove conflicting Bootstrap classes
  textBox.classList.remove("bg-dark", "text-light", "bg-light", "text-dark");

  // Apply styles with !important override
  textBox.style.setProperty("background-color", bg, "important");
  sentenceText.style.setProperty("color", fg, "important");
  sentenceText.style.setProperty("font-size", fs, "important");
  sentenceText.style.setProperty("font-family", ff, "important");

  // Theme toggle
  if (themeSwitch.checked) {
    page.classList.remove("theme-light");
    page.classList.add("theme-dark");
  } else {
    page.classList.remove("theme-dark");
    page.classList.add("theme-light");
  }

  if (save) {
    localStorage.setItem("settings", JSON.stringify({
      bg,
      color: fg,
      size: fontSize.value,
      font: ff,
      dark: themeSwitch.checked
    }));
  }

  // Debug logs
  console.log(`[Settings Updated]`);
  console.log(`Background: ${bg}`);
  console.log(`Text Color: ${fg}`);
  console.log(`Font Size: ${fs}`);
  console.log(`Font: ${ff}`);
  console.log(`Theme: ${themeSwitch.checked ? "Dark" : "Light"}`);
}

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
    // Defaults
    bgColor.value = "#212529";
    textColor.value = "#e0e0e0";
    fontSize.value = 20;
  }
  applySettings(false);
}

function updateProgress() {
  // Sentence progress (within chapter)
  if (totalSentences > 1) {
    const percent = Math.min(100, (currentIndex / totalSentences) * 100);
    document.getElementById("sentence-progress-bar").style.width = percent + "%";
    progressLabel.innerText = `Sentence ${currentIndex} of ${totalSentences}`;
  } else {
    document.getElementById("sentence-progress-bar").style.width = "100%";
    progressLabel.innerText = "Sentence 1 of 1";
  }

  // Chapter progress (within novel)
  const chapterList = Array.from(document.getElementById("chapterSelect").options).map(opt => opt.value);
  const currentChapter = document.getElementById("chapterSelect").value;
  const chapterIndex = chapterList.indexOf(currentChapter) + 1; // 1-based
  const totalChapters = chapterList.length;

  const chapterPercent = (chapterIndex / totalChapters) * 100;
  document.getElementById("chapter-progress-bar").style.width = chapterPercent + "%";
  document.getElementById("chapter-progress-label").innerText = `Chapter ${chapterIndex} of ${totalChapters}`;
}


function syncProgress() {
  localStorage.setItem("sentenceIndex", currentIndex);
  localStorage.setItem("totalSentences", totalSentences);
  updateProgress();
}

const chapterSelect = document.getElementById("chapterSelect");

if (chapterSelect) {
  chapterSelect.addEventListener("change", () => {
    const selectedChapter = chapterSelect.value;
    const currentNovel = new URLSearchParams(window.location.search).get("novel");
    window.location.href = `/read?novel=${encodeURIComponent(currentNovel)}&chapter=${encodeURIComponent(selectedChapter)}`;
  });
}





document.addEventListener("keydown", function (e) {
  if (e.key === "ArrowRight") nextBtn.click();
  if (e.key === "ArrowLeft") prevBtn.click();
});

bgColor.addEventListener('input', () => applySettings());
textColor.addEventListener('input', () => applySettings());
fontSize.addEventListener('input', () => applySettings());
fontFamily.addEventListener('change', () => applySettings());
themeSwitch.addEventListener('change', () => applySettings());

async function navigateSentence(direction) {
  const url = direction === 'next' ? '/api/next' : '/api/prev';
  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.sentence) {
      sentenceText.textContent = data.sentence;
      currentIndex = data.index;
      totalSentences = data.total;
      syncProgress();

      if (direction === 'next' && currentIndex === totalSentences) {
        // Reached the last sentence
        setTimeout(() => {
          goToNextChapter();
        }, 800);  // slight delay to let user read last sentence
      }
    }
  } catch (err) {
    console.error("Failed to load sentence:", err);
  }
}

function goToNextChapter() {
  fetch('/api/next_chapter')
    .then(res => {
      if (res.redirected) {
        window.location.href = res.url;
      } else {
        // No more chapters → show modal
        const endModal = new bootstrap.Modal(document.getElementById('endModal'));
        endModal.show();
      }
    });
}


// Replace click handlers
nextBtn.addEventListener("click", e => {
  e.preventDefault();
  navigateSentence('next');
});

prevBtn.addEventListener("click", e => {
  e.preventDefault();
  navigateSentence('prev');
});

async function initSentence() {
  try {
    const res = await fetch('/api/init');
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

loadSettings();
initSentence();
updateProgress();
