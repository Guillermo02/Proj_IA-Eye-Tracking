# Proj_IA-Eye-Tracking  
Sistema de rastreamento ocular com WebGazer.js, Streamlit e análise com IA.

## Autores
- Arthur Cezar da Silveira Lima RA 10409172
- Gabriel Morgado Nogueira RA 10409493
- Guillermo Kuznietz RA 10410134

---

## Visão Geral do Projeto

Este projeto implementa um experimento de **eye-tracking** baseado em webcam utilizando o **WebGazer.js** integrado ao **Streamlit**, permitindo analisar como usuários distribuem sua atenção entre diferentes estímulos coloridos exibidos na tela.

O experimento apresenta três círculos coloridos fixos nas posições de um triângulo. Cada ciclo funciona assim:

- **5 segundos** → os círculos aparecem com cores aleatórias  
- **2 segundos** → todos desaparecem para “resetar” a visão  
- O WebGazer registra continuamente a posição do olhar  

Cada amostra coletada é associada ao estímulo mais próximo e salva contendo:

- Coordenadas do olhar (x, y)  
- Cor do estímulo mais próximo  
- Posição do estímulo (topo / baixo-esquerda / baixo-direita)  
- Timestamp  
- ID do estímulo  

Esses dados podem ser baixados em JSON e analisados diretamente no Streamlit.

### Vídeo
O vídeo explicativo do projeto pode ser encontrado em <a href="https://youtu.be/nhFCPyoFcq8">vídeo</a>

---

## Funcionamento do Experimento

A interface do experimento combina:

- **WebGazer.js** — rastreamento ocular via webcam  
- **HTML, CSS e JavaScript** — exibidos dentro do Streamlit  
- **Python + Streamlit** — controle de interface e análise dos dados  

O fluxo do experimento é:

1. O usuário encara a tela; o WebGazer calibra com cliques do mouse na posição que estiver olhando na tela.  
2. Três círculos coloridos surgem formando um triângulo centralizado.  
3. Após 5 segundos, desaparecem por 2 segundos.  
4. A cada ciclo novas cores são sorteadas.  
5. A cada frame, o sistema captura a estimativa do olhar e associa ao círculo mais próximo.  

---


## Dependências Necessárias

 Versão recomendada de Python:
- Python 3.12

 Bibliotecas utilizadas (Python):
- streamlit  
- pandas  
- numpy  
- scikit-learn  

Instalação:

pip install streamlit pandas numpy scikit-learn

> Se quiser garantir que seja instalado usando a versão do python atual, use o comando:

``python -m pip install scikit-learn streamlit pandas matplotlib``



### Dependências Web (via CDN):

- WebGazer.js  
- clmtrackr  

Essas já estão incluídas no HTML dentro da aplicação.

---

## Como Executar o Projeto

### 1. Criar ambiente virtual (opcional porém recomendado)
  python -m venv venv
  
### 1.1 Ativar o ambiente virtual
  
Windows: venv\Scripts\activate


### 2. Instalar dependências

pip install streamlit pandas numpy scikit-learn

ou

python -m pip install scikit-learn streamlit pandas matplotlib


### 3. Rodar o Streamlit

streamlit run app.py


Seu navegador abrirá automaticamente em: http://localhost:8501


---

## Análises Disponíveis no Streamlit

O aplicativo é dividido em abas:

### Aba 1 — Experimento

- Exibe o HTML com WebGazer.js  
- Usuário realiza o teste visual
- Botão "Ver Análise Atual" mostra uma analise simples do teste até o momento
- Botão “Baixar JSON” salva os dados coletados  

### Aba 2 — Análise Dos Dados

Permite:
- Carregar o arquivo JSON gerado  
- Ver as primeiras amostras  
- Ver colunas detectadas  
- Ver atenção:
  - Por cor  
  - Por posição (topo / baixo-esquerda / baixo-direita)  
- Ver tempo estimado de fixação 

Inclui também:
- Estimativa do intervalo médio entre amostras (`dt`)  
- Cálculo do tempo total de atenção por categoria  

### Aba 3 — Análise com IA (scikit-learn)

Processo executado:
1. Agrega dados por **cor + posição**  
2. Estima o tempo total de atenção por combinação  
3. Define automaticamente o limiar de “alta atenção” (mediana)  
4. Constrói dataset rotulado  
5. Codifica as variáveis categóricas (`OneHotEncoder`)  
6. Treina um modelo:
   - **RandomForestClassifier**  
7. Exibe:
   - Tabela completa agregada  
   - Limiar usado  
   - Relatório de classificação (`classification_report`)  

Essa aba mostra como IA pode auxiliar na interpretação de comportamento visual.

---

## Detalhes Técnicos da Análise

### Cálculo do tempo de atenção

1. Ordena timestamps  
2. Calcula diferença média entre amostras (`dt`)  
3. Multiplica número de amostras por `dt` para obter tempo aproximado  

### Associação com estímulo mais próximo

Para cada gaze `(x, y)`:

- Calcula distância para cada círculo  
- Seleciona o mais próximo  
- Salva cor, posição e ID  

### Rótulo de atenção (IA)

`tempo_atencao >= mediana → alta atenção (1)`  
`tempo_atencao < mediana → baixa atenção (0)`

---

## Referências Bibliográficas

**BYLINSKII, Z.; ISOLA, P.; BAINBRIDGE, C.; TORRALBA, A.; OLIVA, A.**  
*Intrinsic and Extrinsic Effects on Image Memorability.* Vision Research, v. 116, p. 165–178, 2015.

**ȚICHINDELEAN, M.; ȚICHINDELEAN, M. T.; CETINĂ, I.; ORZAN, G.**  
*A Comparative Eye Tracking Study of Usability — Towards Sustainable Web Design.* Sustainability, v. 13, p. 10415, 2021.

**YU, C. H.**  
*An Eye-Tracking Study: Investigating the Impact of Website Theme Colors on Viewer Engagement.* Dean & Francis Press, 2023.

---

## Possíveis Extensões do Projeto

- Heatmap do olhar  
- Exportação automática dos resultados em PDF  
- Comparação entre múltiplos participantes  
- Pipeline completo para estudos de UX  
- Modelos de IA mais complexos (SVM, Gradient Boosting)  
- Dashboard avançado com Plotly  
