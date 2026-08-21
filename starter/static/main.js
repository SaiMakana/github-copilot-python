// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const SCORES_STORAGE_KEY = 'sudokuTop10Scores';
const THEME_STORAGE_KEY = 'sudokuTheme';
let puzzle = [];
let timerId = null;
let elapsedSeconds = 0;
let scoreRecorded = false;

function applyTheme(theme) {
  const selectedTheme = theme === 'dark' ? 'dark' : 'light';
  document.documentElement.dataset.theme = selectedTheme;
  const toggle = document.getElementById('theme-toggle');
  if (toggle) {
    const darkMode = selectedTheme === 'dark';
    toggle.setAttribute('aria-pressed', String(darkMode));
    toggle.textContent = darkMode ? 'Light mode' : 'Dark mode';
  }
}

function loadTheme() {
  try {
    return localStorage.getItem(THEME_STORAGE_KEY) || 'light';
  } catch (error) {
    return 'light';
  }
}

function toggleTheme() {
  const nextTheme = document.documentElement.dataset.theme === 'dark' ? 'light' : 'dark';
  applyTheme(nextTheme);
  try {
    localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  } catch (error) {
    // Continue with the selected theme when browser storage is unavailable.
  }
}

function validateScore(score) {
  return score !== null
    && typeof score === 'object'
    && typeof score.name === 'string'
    && score.name.trim() !== ''
    && Number.isInteger(score.time)
    && score.time >= 0
    && ['easy', 'medium', 'hard'].includes(score.difficulty)
    && Number.isFinite(score.createdAt);
}

function loadScores() {
  try {
    const storedScores = localStorage.getItem(SCORES_STORAGE_KEY);
    if (!storedScores) return [];

    const scores = JSON.parse(storedScores);
    return Array.isArray(scores) ? scores.filter(validateScore) : [];
  } catch (error) {
    return [];
  }
}

function saveScores(scores) {
  try {
    localStorage.setItem(SCORES_STORAGE_KEY, JSON.stringify(scores));
  } catch (error) {
    // Continue playing when browser storage is unavailable or full.
  }
}

function renderScores() {
  const scoreList = document.getElementById('score-list');
  if (!scoreList) return;

  scoreList.replaceChildren();
  loadScores().forEach((score) => {
    const item = document.createElement('li');
    const name = document.createElement('span');
    const time = document.createElement('span');
    const difficulty = document.createElement('span');

    name.className = 'score-name';
    time.className = 'score-time';
    difficulty.className = 'score-difficulty';
    name.textContent = score.name;
    time.textContent = formatElapsedTime(score.time);
    difficulty.textContent = score.difficulty;

    item.append(name, time, difficulty);
    scoreList.appendChild(item);
  });
}

function recordCompletedGame() {
  const enteredName = window.prompt('Enter your name for the Top 10:', 'Player');
  if (enteredName === null) return;

  const name = enteredName.trim().slice(0, 30) || 'Player';
  const scores = loadScores();
  scores.push({
    name,
    time: elapsedSeconds,
    difficulty: document.getElementById('difficulty').value,
    createdAt: Date.now(),
  });
  scores.sort((left, right) => left.time - right.time || left.createdAt - right.createdAt);
  const topScores = scores.slice(0, 10);
  saveScores(topScores);
  renderScores();
}

function formatElapsedTime(seconds) {
  const minutes = Math.floor(seconds / 60);
  const remainingSeconds = seconds % 60;
  return `${String(minutes).padStart(2, '0')}:${String(remainingSeconds).padStart(2, '0')}`;
}

function updateTimerDisplay() {
  document.getElementById('timer').innerText = formatElapsedTime(elapsedSeconds);
}

function stopTimer() {
  if (timerId !== null) {
    clearInterval(timerId);
    timerId = null;
  }
}

function startTimer() {
  stopTimer();
  timerId = setInterval(() => {
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function readBoard() {
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const value = inputs[i * SIZE + j].value;
      board[i][j] = value ? parseInt(value, 10) : 0;
    }
  }
  return board;
}

function hasConflict(board, row, col) {
  const value = board[row][col];
  if (value === 0) return false;

  for (let index = 0; index < SIZE; index++) {
    if (index !== col && board[row][index] === value) return true;
    if (index !== row && board[index][col] === value) return true;
  }

  const startRow = row - row % 3;
  const startCol = col - col % 3;
  for (let boxRow = startRow; boxRow < startRow + 3; boxRow++) {
    for (let boxCol = startCol; boxCol < startCol + 3; boxCol++) {
      if ((boxRow !== row || boxCol !== col) && board[boxRow][boxCol] === value) {
        return true;
      }
    }
  }
  return false;
}

function updateInvalidCells() {
  const board = readBoard();
  const inputs = document.getElementById('sudoku-board').getElementsByTagName('input');
  let hasInvalidCells = false;

  for (let row = 0; row < SIZE; row++) {
    for (let col = 0; col < SIZE; col++) {
      const input = inputs[row * SIZE + col];
      if (input.disabled) continue;
      input.classList.remove('incorrect');
      if (hasConflict(board, row, col)) {
        input.classList.add('incorrect');
        hasInvalidCells = true;
      }
    }
  }

  const msg = document.getElementById('message');
  if (hasInvalidCells) {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Invalid move';
  } else if (msg.innerText === 'Invalid move') {
    msg.innerText = '';
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.className = 'sudoku-cell';
      input.dataset.row = i;
      input.dataset.col = j;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        updateInvalidCells();
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function renderPuzzle(puz) {
  puzzle = puz;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className += ' prefilled';
      } else {
        inp.value = '';
        inp.disabled = false;
      }
    }
  }
}

async function newGame() {
  stopTimer();
  elapsedSeconds = 0;
  scoreRecorded = false;
  updateTimerDisplay();
  const difficulty = document.getElementById('difficulty').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(difficulty)}`);
  const data = await res.json();
  if (data.error) {
    document.getElementById('message').innerText = data.error;
    return;
  }
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  startTimer();
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = readBoard();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    inp.className = 'sudoku-cell';
    if (incorrect.has(idx)) {
      inp.className = 'sudoku-cell incorrect';
    }
  }
  if (incorrect.size === 0) {
    stopTimer();
    if (!scoreRecorded) {
      scoreRecorded = true;
      recordCompletedGame();
    }
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

async function requestHint() {
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board: readBoard()})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  if (data.hint === null) {
    msg.style.color = '#388e3c';
    msg.innerText = data.message;
    return;
  }

  const input = document.querySelector(
    `input[data-row="${data.row}"][data-col="${data.col}"]`
  );
  if (!input || input.disabled) return;
  input.value = data.value;
  input.disabled = true;
  input.classList.remove('incorrect');
  input.classList.add('hinted');
  updateInvalidCells();
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(loadTheme());
  renderScores();
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  // initialize
  newGame();
});