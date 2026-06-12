const STORAGE_KEY = "classic-exam-study-v1";
const state = {
  year: "all",
  exam: "2025-1-final",
  filter: "all",
  currentId: null,
  sidebarOpen: false,
  study: loadStudy(),
};

function loadStudy() {
  try { return JSON.parse(localStorage.getItem(STORAGE_KEY)) || { answers: {}, starred: {} }; }
  catch { return { answers: {}, starred: {} }; }
}

function saveStudy() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.study));
}

function allQuestions() {
  return [...(window.QUESTION_BANK || [])]
    .sort((a, b) => b.year - a.year || a.term.localeCompare(b.term) || a.number - b.number);
}

function filteredQuestions() {
  return allQuestions().filter(q => {
    const yearOk = state.year === "all" || String(q.year) === state.year;
    const examOk = state.exam === "all" || q.examId === state.exam;
    const result = state.study.answers[q.id];
    const filterOk =
      state.filter === "all" ||
      (state.filter === "wrong" && result !== undefined && result !== q.answer) ||
      (state.filter === "starred" && state.study.starred[q.id]);
    return yearOk && examOk && filterOk;
  });
}

function currentQuestion() {
  const list = filteredQuestions();
  if (!list.some(q => q.id === state.currentId)) state.currentId = list[0]?.id || null;
  return list.find(q => q.id === state.currentId);
}

function resultClass(q) {
  const answer = state.study.answers[q.id];
  if (answer === undefined) return "";
  return answer === q.answer ? "correct" : "wrong";
}

function setAnswer(q, index) {
  state.study.answers[q.id] = index;
  saveStudy();
  render();
}

function resetAnswer(q) {
  delete state.study.answers[q.id];
  saveStudy();
  render();
}

function toggleStar(q) {
  state.study.starred[q.id] = !state.study.starred[q.id];
  saveStudy();
  render();
}

function move(step) {
  const list = filteredQuestions();
  const index = list.findIndex(q => q.id === state.currentId);
  const next = list[index + step];
  if (next) {
    state.currentId = next.id;
    render();
    window.scrollTo({ top: 0, behavior: "smooth" });
  }
}

function render() {
  const questions = filteredQuestions();
  const q = currentQuestion();
  const years = [...new Set(allQuestions().map(q => q.year))].sort((a, b) => b - a);
  const exams = (window.EXAM_CATALOG || []).filter(exam => state.year === "all" || String(exam.year) === state.year);
  const answered = questions.filter(q => state.study.answers[q.id] !== undefined).length;
  const progress = questions.length ? Math.round(answered / questions.length * 100) : 0;
  const currentIndex = q ? questions.findIndex(item => item.id === q.id) : -1;

  document.querySelector("#app").innerHTML = `
    <div class="app-shell">
      <div class="overlay ${state.sidebarOpen ? "open" : ""}" data-action="close-sidebar"></div>
      <aside class="sidebar ${state.sidebarOpen ? "open" : ""}">
        <div class="brand">
          <div><h1>경전 기출</h1><small>FLASHCARD STUDY</small></div>
          <button class="mobile-close" data-action="close-sidebar">×</button>
        </div>
        <div class="filters">
          <select class="year-select" data-action="year">
            <option value="all">전체 연도</option>
            ${years.map(y => `<option value="${y}" ${state.year === String(y) ? "selected" : ""}>${y}년</option>`).join("")}
          </select>
          <select class="year-select" data-action="exam">
            <option value="all">전체 시험</option>
            ${exams.map(exam => `<option value="${exam.id}" ${state.exam === exam.id ? "selected" : ""}>${escapeHtml(exam.label)} · ${escapeHtml(exam.status)}</option>`).join("")}
          </select>
          <div class="filter-tabs">
            ${[["all","전체"],["wrong","오답"],["starred","별표"]].map(([key,label]) =>
              `<button class="${state.filter === key ? "active" : ""}" data-filter="${key}">${label}</button>`
            ).join("")}
          </div>
        </div>
        <div class="progress-block">
          <div class="progress-copy"><span>${answered} / ${questions.length} 풀이</span><span>${progress}%</span></div>
          <div class="progress-track"><div class="progress-value" style="width:${progress}%"></div></div>
        </div>
        <div class="question-list">
          ${questions.map(item => `<button class="q-jump ${item.id === state.currentId ? "active" : ""} ${resultClass(item)} ${state.study.starred[item.id] ? "starred" : ""}" data-id="${item.id}">${String(item.number).padStart(2,"0")}</button>`).join("")}
        </div>
      </aside>
      <main class="main">
        <div class="topbar">
          <button class="mobile-menu" data-action="open-sidebar">☰</button>
          <div class="top-meta">${q ? `<span class="pill">${escapeHtml(q.exam)}</span><span class="pill">${q.year}년 · ${q.term}</span>` : ""}</div>
          ${q && state.study.answers[q.id] !== undefined ? `<button class="reset-button" data-action="reset">정답 취소 · 다시 풀기</button>` : `<span></span>`}
        </div>
        ${q ? cardMarkup(q) : `<div class="card empty"><strong>명확하게 복원된 문제가 아직 없습니다.</strong><br><br>원본 OCR 품질이 낮아 불완전한 문항은 제외했습니다.</div>`}
        <div class="bottom-nav">
          <button class="nav-button" data-action="prev" ${currentIndex <= 0 ? "disabled" : ""}>← 이전</button>
          <span class="keyboard-hint">← → 이동 · 1–4 답 선택 · R 다시 풀기 · S 별표</span>
          <button class="nav-button" data-action="next" ${currentIndex >= questions.length - 1 ? "disabled" : ""}>다음 →</button>
        </div>
      </main>
    </div>`;
}

function cardMarkup(q) {
  const selected = state.study.answers[q.id];
  const revealed = selected !== undefined;
  return `<article class="card">
    <div class="card-head">
      <div>
        <div class="question-number">Question ${String(q.number).padStart(2,"0")}</div>
        <h2 class="question-text">${escapeHtml(q.question)}</h2>
      </div>
      <button class="star-button ${state.study.starred[q.id] ? "active" : ""}" data-action="star" aria-label="별표">${state.study.starred[q.id] ? "★" : "☆"}</button>
    </div>
    <div class="choices">
      ${q.choices.map((choice, index) => {
        let cls = "";
        if (revealed && index === q.answer) cls = "correct";
        else if (revealed && index === selected) cls = "wrong";
        else if (revealed) cls = "dimmed";
        return `<button class="choice ${cls}" data-choice="${index}">
          <span class="choice-index">${index + 1}</span><span>${escapeHtml(choice)}</span>
        </button>`;
      }).join("")}
    </div>
    ${revealed ? `<div class="explanation"><strong>${selected === q.answer ? "정답입니다." : `정답은 ${q.answer + 1}번입니다.`}</strong>${escapeHtml(q.explanation || "해설이 아직 등록되지 않았습니다.")}</div>` : ""}
  </article>`;
}

function escapeHtml(value) {
  return String(value).replace(/[&<>"']/g, c => ({ "&":"&amp;", "<":"&lt;", ">":"&gt;", '"':"&quot;", "'":"&#039;" }[c]));
}

document.addEventListener("click", event => {
  const el = event.target.closest("[data-action], [data-filter], [data-id], [data-choice]");
  if (!el) return;
  const q = currentQuestion();
  if (el.dataset.filter) { state.filter = el.dataset.filter; state.currentId = null; }
  if (el.dataset.id) { state.currentId = el.dataset.id; state.sidebarOpen = false; }
  if (el.dataset.choice !== undefined && q && state.study.answers[q.id] === undefined) setAnswer(q, Number(el.dataset.choice));
  if (el.dataset.action === "year" || el.dataset.action === "exam") return;
  if (el.dataset.action === "prev") move(-1);
  if (el.dataset.action === "next") move(1);
  if (el.dataset.action === "reset" && q) resetAnswer(q);
  if (el.dataset.action === "star" && q) toggleStar(q);
  if (el.dataset.action === "open-sidebar") state.sidebarOpen = true;
  if (el.dataset.action === "close-sidebar") state.sidebarOpen = false;
  render();
});

document.addEventListener("change", event => {
  if (event.target.dataset.action === "year") {
    state.year = event.target.value;
    state.exam = "all";
    state.currentId = null;
    render();
  }
  if (event.target.dataset.action === "exam") {
    state.exam = event.target.value;
    state.currentId = null;
    render();
  }
});

document.addEventListener("keydown", event => {
  if (["INPUT", "SELECT", "TEXTAREA"].includes(document.activeElement?.tagName)) return;
  const q = currentQuestion();
  if (event.key === "ArrowLeft") move(-1);
  if (event.key === "ArrowRight") move(1);
  if (/^[1-4]$/.test(event.key) && q && state.study.answers[q.id] === undefined) setAnswer(q, Number(event.key) - 1);
  if (event.key.toLowerCase() === "r" && q) resetAnswer(q);
  if (event.key.toLowerCase() === "s" && q) toggleStar(q);
});

if ("serviceWorker" in navigator) navigator.serviceWorker.register("/sw.js").catch(() => {});
render();
