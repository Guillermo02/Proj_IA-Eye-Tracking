import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

st.set_page_config(page_title="Eye Tracking com WebGazer", layout="wide")

st.title("Experimento de Eye-Tracking com Estímulos Coloridos")

st.write("""
Este experimento apresenta **círculos coloridos** em posições aleatórias na tela,
trocando de cor e posição a cada intervalo de tempo.  
O WebGazer registra continuamente as coordenadas do olhar e associa cada amostra
ao estímulo que está na tela naquele momento.

No final, você pode **baixar um arquivo JSON** com todos os dados coletados
para análise em Python/IA.
""")

html_code = """
<!DOCTYPE html>
<html>
<head>
  <meta charset="UTF-8">
  <script src="https://webgazer.cs.brown.edu/webgazer.js"></script>
  <style>
    html, body {
      margin: 0;
      padding: 0;
      overflow: hidden;
      width: 100%;
      height: 100%;
      background-color: #111;
      color: #fff;
      font-family: Arial, sans-serif;
    }

    #ponto {
      width: 16px;
      height: 16px;
      background-color: #ff0000;
      border-radius: 50%;
      position: absolute;
      pointer-events: none;
      transform: translate(-50%, -50%);
      z-index: 9999;
    }

    .stimulusCircle {
      width: 80px;
      height: 80px;
      border-radius: 50%;
      position: absolute;
      transform: translate(-50%, -50%);
      z-index: 5000;
    }

    #topBar {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      height: 40px;
      background: rgba(0,0,0,0.7);
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 0 10px;
      z-index: 10000;
      font-size: 14px;
    }

    #downloadBtn {
      padding: 5px 10px;
      background: #28a745;
      border: none;
      border-radius: 4px;
      color: #fff;
      cursor: pointer;
      font-size: 13px;
    }

    #downloadBtn:hover {
      background: #218838;
    }

    #info {
      font-size: 12px;
      opacity: 0.8;
    }
  </style>
</head>
<body>

  <div id="topBar">
    <div id="info">
      Olhe para os três círculos coloridos. Eles ficam 5 segundos visíveis em posições fixas (triângulo) e depois somem por 2 segundos antes do próximo teste.
      Clique em pontos da tela (olhando para eles) para ajudar na calibração.
    </div>
    <button id="downloadBtn">Baixar dados em JSON</button>
  </div>

  <div id="ponto"></div>

  <!-- Três círculos de estímulo -->
  <div class="stimulusCircle" id="circle0"></div>
  <div class="stimulusCircle" id="circle1"></div>
  <div class="stimulusCircle" id="circle2"></div>

  <script>
    // ==========================
    // CONFIGURAÇÃO DO EXPERIMENTO
    // ==========================

    const COLORS = ["red", "green", "blue", "yellow", "cyan", "magenta", "orange", "purple"];

    const NUM_CIRCLES = 3;

    // 5 segundos visíveis, 2 segundos apagados
    const STIMULUS_VISIBLE_MS = 5000;
    const STIMULUS_BLANK_MS   = 2000;

    const STIMULUS_DIAMETER = 80;

    // offsets fixos em forma de triângulo em torno do centro (dx, dy)
    const TRIANGLE_OFFSETS = [
      { dx: 0,    dy: -150 },  // topo
      { dx: -130, dy:  75 },   // baixo-esquerda
      { dx: 130,  dy:  75 }    // baixo-direita
    ];

    // ==========================
    // VARIÁVEIS DE ESTADO
    // ==========================

    let currentStimuli = [];   // [{id, color, x, y}, ...]
    let stimulusIdCounter = 0;
    let gazeData = [];
    let stimuliVisible = false;

    const ponto = document.getElementById('ponto');
    const circles = [
      document.getElementById('circle0'),
      document.getElementById('circle1'),
      document.getElementById('circle2'),
    ];
    const downloadBtn = document.getElementById('downloadBtn');

    // ==========================
    // FUNÇÕES AUXILIARES
    // ==========================

    function pickDistinctColors(n) {
      const shuffled = COLORS.slice().sort(() => Math.random() - 0.5);
      return shuffled.slice(0, n);
    }

    // posiciona os 3 círculos em triângulo fixo, apenas trocando as cores
    function showStimuli() {
      const w = window.innerWidth;
      const h = window.innerHeight;

      const centerX = w / 2;
      const centerY = h / 2;

      const colors = pickDistinctColors(NUM_CIRCLES);

      currentStimuli = [];

      for (let i = 0; i < NUM_CIRCLES; i++) {
        const circle = circles[i];
        const offset = TRIANGLE_OFFSETS[i];

        const x = centerX + offset.dx;
        const y = centerY + offset.dy;
        const color = colors[i];

        circle.style.left = x + "px";
        circle.style.top  = y + "px";
        circle.style.backgroundColor = color;
        circle.style.display = "block";

        currentStimuli.push({
          id: stimulusIdCounter++,
          color: color,
          x: x,
          y: y,
          startTime: Date.now()
        });
      }

      stimuliVisible = true;
    }

    function hideStimuli() {
      for (const circle of circles) {
        circle.style.display = "none";
      }
      stimuliVisible = false;
    }

    function findNearestStimulus(gazeX, gazeY) {
      if (!stimuliVisible || !currentStimuli || currentStimuli.length === 0) return null;

      let nearest = null;
      let minDistSq = Infinity;

      for (const s of currentStimuli) {
        const dx = gazeX - s.x;
        const dy = gazeY - s.y;
        const distSq = dx * dx + dy * dy;
        if (distSq < minDistSq) {
          minDistSq = distSq;
          nearest = s;
        }
      }

      return nearest;
    }

    // ciclo: 5s ON (triângulo visível) -> 2s OFF (sem círculos) -> repete
    function startStimulusCycle() {
      showStimuli();  // aparece triângulo com novas cores

      setTimeout(() => {
        hideStimuli();  // some
        setTimeout(() => {
          startStimulusCycle(); // próximo teste
        }, STIMULUS_BLANK_MS);
      }, STIMULUS_VISIBLE_MS);
    }

    // ==========================
    // INICIALIZAÇÃO DO WEBGAZER
    // ==========================

    function startExperiment() {
      window.saveDataAcrossSessions = true;

      webgazer
        .setRegression('ridge')
        .setTracker('clmtrackr')
        .setGazeListener(function(data, timestamp) {
          if (!data) return;

          const gazeX = data.x;
          const gazeY = data.y;

          // Atualiza o ponto vermelho
          ponto.style.left = gazeX + "px";
          ponto.style.top  = gazeY + "px";

          // Só associa a um círculo se eles estiverem visíveis
          const nearest = findNearestStimulus(gazeX, gazeY);

          gazeData.push({
            x: gazeX,
            y: gazeY,
            timestamp: timestamp || Date.now(),
            nearestStimulusId: nearest ? nearest.id : null,
            nearestStimulusColor: nearest ? nearest.color : null
          });
        })
        .begin()
        .then(() => {
          console.log("WebGazer iniciado");
          webgazer.addMouseEventListeners();   // ajuda na calibração
          webgazer.showPredictionPoints(false);

          // inicia o ciclo dos estímulos
          startStimulusCycle();
        })
        .catch(err => {
          console.error("Erro ao iniciar WebGazer:", err);
        });
    }

    // iniciar assim que possível
    startExperiment();

    // ==========================
    // DOWNLOAD DOS DADOS EM JSON
    // ==========================

    downloadBtn.addEventListener('click', function() {
      const blob = new Blob([JSON.stringify(gazeData, null, 2)], {type: "application/json"});
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "gaze_data_experimento.json";
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      URL.revokeObjectURL(url);
    });
  </script>
</body>
</html>
"""

components.html(html_code, height=800)

st.markdown("---")
st.header("Análise dos dados (opcional)")

st.write("Depois de rodar o experimento e baixar o arquivo `gaze_data_experimento.json`, envie-o abaixo para analisar os resultados.")

uploaded_file = st.file_uploader("Envie o arquivo JSON gerado pelo experimento", type=["json"])

# ===========================================================
# 1. CARREGAR O JSON
# ===========================================================

ARQUIVO_JSON = "gaze_data_experimento.json"

with open(ARQUIVO_JSON, "r", encoding="utf-8") as f:
    data = json.load(f)

if not data:
    raise ValueError("O arquivo JSON está vazio. Rode o experimento e baixe um novo arquivo.")

df = pd.DataFrame(data)
print("Primeiras linhas do DataFrame:")
print(df.head())
print("\nColunas:", df.columns.tolist())

# ===========================================================
# 2. LIMPEZA BÁSICA E FILTRO
# ===========================================================

# Garante tipos numéricos
for col in ["x", "y", "timestamp"]:
    if col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

# Mantém apenas linhas com associação a algum estímulo
df_valid = df.dropna(subset=["nearestStimulusId", "nearestStimulusColor", "timestamp"]).copy()
df_valid["nearestStimulusId"] = df_valid["nearestStimulusId"].astype(int)

print(f"\nTotal de amostras válidas (com estímulo associado): {len(df_valid)}")

if len(df_valid) == 0:
    raise ValueError("Nenhuma amostra válida encontrada (nearestStimulusId/Color está sempre nulo). Verifique se o experimento rodou corretamente.")

# ===========================================================
# 3. ESTIMAR INTERVALO MÉDIO ENTRE AMOSTRAS
# ===========================================================

# Ordena por tempo e calcula diferença entre timestamps
df_sorted = df_valid.sort_values("timestamp")
dt = df_sorted["timestamp"].diff()
dt_medio_ms = dt.dropna().mean()

if pd.isna(dt_medio_ms) or dt_medio_ms <= 0:
    dt_medio_ms = 30.0  # fallback padrão
    print("\nNão foi possível estimar dt médio. Usando 30 ms como valor aproximado.")
else:
    print(f"\nIntervalo médio estimado entre amostras: {dt_medio_ms:.2f} ms")

# ===========================================================
# 4. ATENÇÃO POR COR
# ===========================================================

samples_by_color = df_valid.groupby("nearestStimulusColor")["timestamp"].count()
attention_time_color_s = samples_by_color * dt_medio_ms / 1000.0

print("\nNúmero de amostras por cor (nearestStimulusColor):")
print(samples_by_color)

print("\nTempo estimado de atenção por cor (segundos):")
print(attention_time_color_s)

# ===========================================================
# 5. ATENÇÃO POR POSIÇÃO (TOPO / BAIXO-ESQ / BAIXO-DIR)
# ===========================================================

# Mapeia o padrão dos IDs para posição no triângulo
# Como você cria 3 estímulos por "rodada", o padrão dos ids é:
# 0,1,2  -> rodada 1
# 3,4,5  -> rodada 2
# ...
# Então: id % 3 -> 0 = topo, 1 = baixo-esq, 2 = baixo-dir

def map_pos(id_):
    r = id_ % 3
    if r == 0:
        return "topo"
    elif r == 1:
        return "baixo-esquerda"
    else:
        return "baixo-direita"

df_valid["posicaoTriangulo"] = df_valid["nearestStimulusId"].apply(map_pos)

samples_by_pos = df_valid.groupby("posicaoTriangulo")["timestamp"].count()
attention_time_pos_s = samples_by_pos * dt_medio_ms / 1000.0

print("\nNúmero de amostras por posição do triângulo:")
print(samples_by_pos)

print("\nTempo estimado de atenção por posição do triângulo (segundos):")
print(attention_time_pos_s)

# ===========================================================
# 6. TABELA RESUMO (COR x POSIÇÃO)
# ===========================================================

tabela_cor_pos = (
    df_valid
    .groupby(["nearestStimulusColor", "posicaoTriangulo"])["timestamp"]
    .count()
    .unstack(fill_value=0)
)

print("\nTabela (nº de amostras) por COR x POSIÇÃO:")
print(tabela_cor_pos)

# ===========================================================
# 7. GRÁFICOS COM MATPLOTLIB
# ===========================================================

# Se quiser ver gráficos, mude para True
FAZER_GRAFICOS = False

if FAZER_GRAFICOS:
    import matplotlib.pyplot as plt

    # Gráfico de barras - tempo de atenção por cor
    plt.figure()
    attention_time_color_s.sort_values(ascending=False).plot(kind="bar")
    plt.title("Tempo estimado de atenção por cor")
    plt.xlabel("Cor")
    plt.ylabel("Tempo (s)")
    plt.tight_layout()

    # Gráfico de barras - tempo de atenção por posição
    plt.figure()
    attention_time_pos_s.sort_values(ascending=False).plot(kind("bar"))
    plt.title("Tempo estimado de atenção por posição do triângulo")
    plt.xlabel("Posição")
    plt.ylabel("Tempo (s)")
    plt.tight_layout()

    plt.show()
