import streamlit as st
import streamlit.components.v1 as components
import json
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import OneHotEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report

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
      gap: 8px;
    }

    #buttonsBox {
      display: flex;
      gap: 6px;
    }

    .topBtn {
      padding: 5px 10px;
      background: #28a745;
      border: none;
      border-radius: 4px;
      color: #fff;
      cursor: pointer;
      font-size: 13px;
    }

    .topBtn:hover {
      background: #218838;
    }

    #info {
      font-size: 12px;
      opacity: 0.8;
      flex: 1;
    }

    #resultsPanel {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      max-height: 35%;
      background: rgba(0,0,0,0.85);
      padding: 10px;
      font-size: 13px;
      overflow-y: auto;
      z-index: 9000;
      border-top: 1px solid #333;
    }

    #resultsPanel h3, #resultsPanel h4 {
      margin: 4px 0;
    }

    #resultsPanel ul {
      margin: 2px 0 6px 16px;
      padding: 0;
    }
  </style>
</head>
<body>

  <div id="topBar">
    <div id="info">
      Olhe para os três círculos coloridos. Eles ficam 5 segundos visíveis em posições fixas (triângulo) e depois somem por 2 segundos antes do próximo teste.
      Clique em pontos da tela (olhando para eles) para ajudar na calibração.
    </div>
    <div id="buttonsBox">
      <button class="topBtn" id="analyzeBtn">Ver análise atual</button>
      <button class="topBtn" id="downloadBtn">Baixar JSON</button>
    </div>
  </div>

  <div id="ponto"></div>

  <!-- Três círculos de estímulo -->
  <div class="stimulusCircle" id="circle0"></div>
  <div class="stimulusCircle" id="circle1"></div>
  <div class="stimulusCircle" id="circle2"></div>

  <!-- Painel para exibir análise parcial -->
  <div id="resultsPanel"></div>

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
      { dx: 0,    dy: -150, label: "topo" },
      { dx: -130, dy:  75,  label: "baixo-esquerda" },
      { dx: 130,  dy:  75,  label: "baixo-direita" }
    ];

    // ==========================
    // VARIÁVEIS DE ESTADO
    // ==========================

    let currentStimuli = [];   // [{id, color, x, y, position}, ...]
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
    const analyzeBtn = document.getElementById('analyzeBtn');
    const resultsPanel = document.getElementById('resultsPanel');

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
          position: offset.label,
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
            nearestStimulusColor: nearest ? nearest.color : null,
            nearestPosition: nearest ? nearest.position : null
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
    // ANÁLISE PARCIAL NO BOTÃO
    // ==========================

    analyzeBtn.addEventListener('click', function() {
      if (!gazeData || gazeData.length === 0) {
        resultsPanel.innerHTML = "<p>Nenhuma amostra registrada ainda. Aguarde alguns segundos de experimento.</p>";
        return;
      }

      // Considerar apenas amostras com alvo definido
      const valid = gazeData.filter(s => s.nearestStimulusColor !== null && s.nearestPosition !== null);

      if (valid.length === 0) {
        resultsPanel.innerHTML = "<p>Ainda não há amostras com estímulos visíveis associados.</p>";
        return;
      }

      const total = valid.length;

      const byColor = {};
      const byPos = {};

      for (const s of valid) {
        const c = s.nearestStimulusColor;
        const p = s.nearestPosition;

        if (!byColor[c]) byColor[c] = 0;
        byColor[c]++;

        if (!byPos[p]) byPos[p] = 0;
        byPos[p]++;
      }

      let html = "<h3>Resumo parcial do experimento</h3>";
      html += `<p>Total de amostras com alvo associado: <strong>${total}</strong></p>`;

      html += "<h4>Atenção por cor</h4><ul>";
      for (const c in byColor) {
        const n = byColor[c];
        const perc = (n / total * 100).toFixed(1);
        html += `<li><strong>${c}</strong>: ${n} amostras (${perc}%)</li>`;
      }
      html += "</ul>";

      html += "<h4>Atenção por posição do triângulo</h4><ul>";
      for (const p in byPos) {
        const n = byPos[p];
        const perc = (n / total * 100).toFixed(1);
        html += `<li><strong>${p}</strong>: ${n} amostras (${perc}%)</li>`;
      }
      html += "</ul>";

      resultsPanel.innerHTML = html;
    });

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

# -------------------------------------------------------------------
# TABS
# -------------------------------------------------------------------
tab_exp, tab_analise, tab_ia = st.tabs(["🧪 Experimento", "📊 Análise dos dados", "🤖 Análise com IA"])

# ==========================
# TAB 1 – EXPERIMENTO
# ==========================
with tab_exp:
    st.subheader("Execução do experimento (WebGazer)")
    st.write("""
    - Ajuste a posição do rosto para que o rastreamento funcione bem.  
    - Observe os três círculos coloridos a cada ciclo.  
    - Use o botão **Baixar JSON** na barra superior da tela do experimento
      para salvar os dados em um arquivo.
    """)
    components.html(html_code, height=800)

# ==========================
# TAB 2 – ANÁLISE DOS DADOS
# ==========================
with tab_analise:
    st.subheader("Upload e análise básica dos dados")
    st.write("Após rodar o experimento e baixar o arquivo `gaze_data_experimento.json`, envie-o abaixo.")

    uploaded_file = st.file_uploader("Envie o arquivo JSON gerado pelo experimento", type=["json"], key="file_analise")

    if uploaded_file is not None:
        try:
            data = json.load(uploaded_file)
        except Exception as e:
            st.error(f"Erro ao ler o JSON: {e}")
            st.stop()

        if not data:
            st.error("O arquivo JSON está vazio. Rode o experimento novamente e baixe um novo arquivo.")
            st.stop()

        df = pd.DataFrame(data)
        
        st.write("Pré-visualização das primeiras amostras:")
        st.dataframe(df.head())
        st.write("Colunas encontradas:", list(df.columns))

        # ----- LIMPEZA BÁSICA -----
        for col in ["x", "y", "timestamp"]:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors="coerce")

        # Reconstruir nearestPosition se não existir (a partir do padrão do triângulo)
        if "nearestPosition" not in df.columns and "nearestStimulusId" in df.columns:
            st.info("Coluna 'nearestPosition' não encontrada. Reconstruindo a partir de 'nearestStimulusId' (mod 3).")

            def map_pos_from_id(id_):
                try:
                    r = int(id_) % 3
                except (TypeError, ValueError):
                    return None
                if r == 0:
                    return "topo"
                elif r == 1:
                    return "baixo-esquerda"
                else:
                    return "baixo-direita"

            df["nearestPosition"] = df["nearestStimulusId"].apply(map_pos_from_id)

        required_cols = ["nearestStimulusColor", "timestamp"]
        if "nearestPosition" in df.columns:
            required_cols.append("nearestPosition")

        missing = [c for c in required_cols if c not in df.columns]
        if missing:
            st.error(
                f"As seguintes colunas necessárias não estão no JSON: {missing}. "
                "Verifique se o experimento rodou na versão mais recente do HTML."
            )
            st.stop()

        df_valid = df.dropna(subset=required_cols).copy()
        st.write(f"Total de amostras válidas (com estímulo associado): **{len(df_valid)}**")

        if len(df_valid) == 0:
            st.error("Nenhuma amostra válida encontrada com estímulo associado.")
            st.stop()

        # ----- ATENÇÃO POR COR -----
        st.markdown("### Atenção por cor")

        samples_by_color = df_valid.groupby("nearestStimulusColor")["timestamp"].count()
        st.write("Número de amostras por cor:")
        st.write(samples_by_color)

        # Estimativa de dt médio
        df_sorted = df_valid.sort_values("timestamp")
        dt = df_sorted["timestamp"].diff().dropna()
        dt_medio_ms = dt.mean() if not dt.empty else 30.0
        dt_medio_s = dt_medio_ms / 1000.0
        st.write(f"Intervalo médio estimado entre amostras: **{dt_medio_ms:.2f} ms**")

        attention_time_color_s = samples_by_color * dt_medio_s
        st.write("Tempo estimado de atenção por cor (segundos):")
        st.write(attention_time_color_s)

        # ----- ATENÇÃO POR POSIÇÃO -----
        if "nearestPosition" in df_valid.columns:
            st.markdown("### Atenção por posição do triângulo")

            samples_by_pos = df_valid.groupby("nearestPosition")["timestamp"].count()
            attention_time_pos_s = samples_by_pos * dt_medio_s

            st.write("Número de amostras por posição:")
            st.write(samples_by_pos)

            st.write("Tempo estimado de atenção por posição (segundos):")
            st.write(attention_time_pos_s)

# ==========================
# TAB 3 – ANÁLISE COM IA
# ==========================
with tab_ia:
    st.subheader("Classificação de alta/baixa atenção (IA)")

    st.write("""
    Esta aba utiliza **scikit-learn** para:
    - agregar os dados por **cor + posição**;  
    - estimar o **tempo de atenção** em cada combinação;  
    - rotular automaticamente como **alta atenção** ou **baixa atenção**, usando a mediana como limiar;  
    - treinar um modelo **RandomForestClassifier** para prever essa classificação.
    """)

    uploaded_file_ia = st.file_uploader(
        "Envie novamente o JSON (ou o mesmo usado na aba anterior) para análise com IA:",
        type=["json"],
        key="file_ia",
    )

    if uploaded_file_ia is not None:
        try:
            data_ia = json.load(uploaded_file_ia)
        except Exception as e:
            st.error(f"Erro ao ler o JSON: {e}")
            st.stop()

        if not data_ia:
            st.error("O arquivo JSON está vazio.")
            st.stop()

        df_ia = pd.DataFrame(data_ia)

        # Conversão numérica
        for col in ["x", "y", "timestamp"]:
            if col in df_ia.columns:
                df_ia[col] = pd.to_numeric(df_ia[col], errors="coerce")

        # Reconstruir nearestPosition, se faltar
        if "nearestPosition" not in df_ia.columns and "nearestStimulusId" in df_ia.columns:
            def map_pos_from_id_ia(id_):
                try:
                    r = int(id_) % 3
                except (TypeError, ValueError):
                    return None
                if r == 0:
                    return "topo"
                elif r == 1:
                    return "baixo-esquerda"
                else:
                    return "baixo-direita"

            df_ia["nearestPosition"] = df_ia["nearestStimulusId"].apply(map_pos_from_id_ia)

        required_cols_ia = ["nearestStimulusColor", "nearestPosition", "timestamp"]
        missing_ia = [c for c in required_cols_ia if c not in df_ia.columns]
        if missing_ia:
            st.error(
                f"As seguintes colunas necessárias não estão no JSON: {missing_ia}. "
                "Verifique se o experimento rodou na versão correta."
            )
            st.stop()

        df_ia_valid = df_ia.dropna(subset=required_cols_ia).copy()
        if len(df_ia_valid) == 0:
            st.error("Nenhuma amostra válida encontrada para IA.")
            st.stop()

        # Estima dt médio
        df_ia_sorted = df_ia_valid.sort_values("timestamp")
        dt_ia = df_ia_sorted["timestamp"].diff().dropna()
        dt_medio_ms_ia = dt_ia.mean() if not dt_ia.empty else 30.0
        dt_medio_s_ia = dt_medio_ms_ia / 1000.0

        st.write(f"Intervalo médio estimado entre amostras: **{dt_medio_ms_ia:.2f} ms**")

        # Agregar por cor + posição
        group_cols = ["nearestStimulusColor", "nearestPosition"]
        agg = (
            df_ia_valid.groupby(group_cols)["timestamp"]
            .count()
            .reset_index(name="num_samples")
        )

        agg["tempo_atencao_s"] = agg["num_samples"] * dt_medio_s_ia

        st.markdown("### Tabela agregada por cor + posição")
        st.dataframe(agg)

        if len(agg) < 2:
            st.warning("Poucos pontos agregados para treinar um modelo de IA de forma significativa.")
            st.stop()

        # Definir rótulo de alta atenção (>= mediana)
        limiar = agg["tempo_atencao_s"].median()
        agg["alta_atencao"] = (agg["tempo_atencao_s"] >= limiar).astype(int)

        st.write(f"Limiar de alta atenção (mediana do tempo): **{limiar:.2f} s**")
        st.write("Tabela com rótulo de alta atenção (1) / baixa atenção (0):")
        st.dataframe(agg[["nearestStimulusColor", "nearestPosition", "tempo_atencao_s", "alta_atencao"]])

        # Preparar features e rótulos
        X_cat = agg[["nearestStimulusColor", "nearestPosition"]]
        y = agg["alta_atencao"]

        # One-hot encoding
        enc = OneHotEncoder(sparse_output=False)
        X_encoded = enc.fit_transform(X_cat)

        # Garantir tamanho mínimo pro train_test_split
        if len(agg) < 4:
            st.warning("Poucos exemplos agregados para uma divisão treino/teste robusta. O modelo será treinado e avaliado sobre os mesmos dados (apenas demonstração).")

            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_encoded, y)
            y_pred = clf.predict(X_encoded)

            report = classification_report(y, y_pred)
            st.markdown("### Relatório de classificação (treino = teste)")
            st.text(report)

        else:
            X_train, X_test, y_train, y_test = train_test_split(
                X_encoded, y, test_size=0.3, random_state=42
            )

            clf = RandomForestClassifier(n_estimators=100, random_state=42)
            clf.fit(X_train, y_train)
            y_pred = clf.predict(X_test)

            report = classification_report(y_test, y_pred)
            st.markdown("### Relatório de classificação (IA)")
            st.text(report)

        st.success("Análise com IA concluída.")
