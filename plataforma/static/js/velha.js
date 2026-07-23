const API = document.querySelector(".velha-wrap").dataset.api;

const NS = "http://www.w3.org/2000/svg";

const board   = document.getElementById("board");
const cells   = [...board.querySelectorAll(".cell")];
const winLine = board.querySelector(".win-line");
const winSeg  = winLine.querySelector("line");
const statusEl= document.getElementById("status");
const footEl  = document.getElementById("foot");
const els = { X: document.getElementById("sx"), O: document.getElementById("so"), draws: document.getElementById("sd") };

const scores = { X:0, O:0, draws:0 };
let state, current, over, busy, modo = "2p";

const delay = ms => new Promise(r => setTimeout(r, ms));

// Cria o SVG da marca (X ou O), desenhado com traço animado.
function markSVG(player){
  const svg = document.createElementNS(NS, "svg");
  svg.setAttribute("viewBox", "0 0 100 100");
  svg.classList.add("mark", player.toLowerCase());
  if (player === "X"){
    const p1 = document.createElementNS(NS, "path");
    p1.setAttribute("d", "M28 28 L72 72"); p1.setAttribute("pathLength", "1");
    const p2 = document.createElementNS(NS, "path");
    p2.setAttribute("d", "M72 28 L28 72"); p2.setAttribute("pathLength", "1"); p2.classList.add("s2");
    svg.append(p1, p2);
  } else {
    const c = document.createElementNS(NS, "circle");
    c.setAttribute("cx","50"); c.setAttribute("cy","50"); c.setAttribute("r","24");
    c.setAttribute("pathLength","1"); c.setAttribute("transform","rotate(-90 50 50)");
    svg.append(c);
  }
  return svg;
}

function renderMark(cell, sym, ghost=false){
  const m = markSVG(sym);
  if (ghost) m.classList.add("ghost");
  cell.appendChild(m);
}

const label = (i, val) => {
  const r = Math.floor(i/3)+1, c = i%3+1;
  return `Linha ${r}, coluna ${c}: ${val ? "marcado com "+val : "vazio"}`;
};
const plHTML = p => `<b class="${p==="X" ? "cx":"co"}">${p}</b>`;
const boardToList = () => state.map(v => v || "");

function updateTurn(){
  if (modo === "ia") statusEl.innerHTML = `Sua vez  ${plHTML("X")}`;
  else statusEl.innerHTML = `Vez do ${plHTML(current)}`;
}

function newGame(){
  state = Array(9).fill(null);
  current = "X"; over = false; busy = false;
  cells.forEach((c,i) => {
    c.innerHTML = ""; c.classList.remove("win"); c.disabled = false;
    c.setAttribute("aria-label", label(i, null));
  });
  winLine.classList.remove("show");
  updateTurn();
}

function drawWinLine(combo, p){
  const a = combo[0], c = combo[2];
  const ax = (a%3)*100+50, ay = Math.floor(a/3)*100+50;
  const cx = (c%3)*100+50, cy = Math.floor(c/3)*100+50;
  const dx = cx-ax, dy = cy-ay, len = Math.hypot(dx,dy) || 1;
  const ux = dx/len, uy = dy/len, ext = 40;
  winSeg.setAttribute("x1", ax-ux*ext); winSeg.setAttribute("y1", ay-uy*ext);
  winSeg.setAttribute("x2", cx+ux*ext); winSeg.setAttribute("y2", cy+uy*ext);
  winLine.style.setProperty("--wl", p==="X" ? "var(--x)" : "var(--o)");
  winLine.classList.remove("show"); void winLine.offsetWidth; winLine.classList.add("show");
}

function aplicarResultado(data, humano){
  if (data.status === "vitoria"){
    over = true;
    data.combo.forEach(k => cells[k].classList.add("win"));
    drawWinLine(data.combo, data.vencedor);
    scores[data.vencedor]++; els[data.vencedor].textContent = scores[data.vencedor];
    if (modo === "ia"){
      statusEl.innerHTML = (data.vencedor === humano) ? "Você venceu! 🎉" : "A IA venceu! 🤖";
    } else {
      statusEl.innerHTML = `${plHTML(data.vencedor)} venceu! 🎉`;
    }
    cells.forEach(c => c.disabled = true);
  } else if (data.status === "empate"){
    over = true;
    scores.draws++; els.draws.textContent = scores.draws;
    statusEl.textContent = "Deu velha! Empate.";
    cells.forEach(c => c.disabled = true);
  } else {
    current = data.proximo;
    updateTurn();
  }
}

async function play(i){
  if (over || state[i] || busy) return;
  busy = true;

  const humano = current;
  const antes = boardToList();          // tabuleiro ANTES da jogada (para o Python)

  // Marca do humano na hora (feedback imediato).
  cells[i].innerHTML = "";              // remove eventual "fantasma"
  renderMark(cells[i], humano);
  state[i] = humano;
  cells[i].disabled = true;
  cells[i].setAttribute("aria-label", label(i, humano));

  let data;
  try{
    const res = await fetch(API, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ tabuleiro: antes, posicao: i, jogador: humano, modo })
    });
    data = await res.json();
  } catch (e){
    // servidor fora do ar -> desfaz a jogada e avisa
    cells[i].innerHTML = ""; state[i] = null; cells[i].disabled = false;
    cells[i].setAttribute("aria-label", label(i, null));
    statusEl.textContent = "Não consegui falar com o servidor Python. Ele está rodando?";
    busy = false; return;
  }

  if (!data.ok){
    cells[i].innerHTML = ""; state[i] = null; cells[i].disabled = false;
    cells[i].setAttribute("aria-label", label(i, null));
    statusEl.textContent = data.erro;
    busy = false; return;
  }

  // Jogada da IA (quando houver), com uma pausa curta para dar ritmo.
  if (data.jogada_ia !== null && data.jogada_ia !== undefined){
    statusEl.textContent = "A IA está pensando…";
    await delay(300);
    const ia = humano === "X" ? "O" : "X";
    renderMark(cells[data.jogada_ia], ia);
    state[data.jogada_ia] = ia;
    cells[data.jogada_ia].disabled = true;
    cells[data.jogada_ia].setAttribute("aria-label", label(data.jogada_ia, ia));
  }

  aplicarResultado(data, humano);
  busy = false;
}

// Preview "fantasma" da marca ao passar o mouse numa casa vazia.
cells.forEach(cell => {
  const i = +cell.dataset.i;
  cell.addEventListener("click", () => play(i));
  cell.addEventListener("pointerenter", () => {
    if (over || state[i] || busy) return;
    renderMark(cell, current, true);
  });
  cell.addEventListener("pointerleave", () => {
    if (state[i]) return;
    const g = cell.querySelector(".ghost"); if (g) g.remove();
  });
});

// Alternância entre 2 jogadores e IA.
document.querySelectorAll(".mode").forEach(btn => {
  btn.addEventListener("click", () => {
    if (busy) return;
    modo = btn.dataset.modo;
    document.querySelectorAll(".mode").forEach(b => b.setAttribute("aria-selected", b === btn ? "true" : "false"));
    // Rótulos do placar mudam conforme o modo.
    if (modo === "ia"){
      document.getElementById("lx").textContent = "Você (X)";
      document.getElementById("lo").textContent = "IA (O)";
      footEl.textContent = "Modo contra a IA · você é o X e começa";
    } else {
      document.getElementById("lx").textContent = "Vitórias X";
      document.getElementById("lo").textContent = "Vitórias O";
      footEl.textContent = "Modo 2 jogadores · X e O se alternam";
    }
    newGame();
  });
});

document.getElementById("reset").addEventListener("click", () => { if (!busy) newGame(); });
document.getElementById("resetAll").addEventListener("click", () => {
  if (busy) return;
  scores.X = scores.O = scores.draws = 0;
  els.X.textContent = els.O.textContent = els.draws.textContent = "0";
  newGame();
});

newGame();
