# Proj_IA-Eye-Tracking

## Autores
- Arthur Cezar da Silveira Lima RA 10409172
- Gabriel Morgado Nogueira      RA 10409493
- Guillermo Kuznietz            RA 10410134

## 1. Introdução

O rastreamento ocular (eye-tracking) é uma ferramenta fundamental para compreender como usuários distribuem sua atenção visual diante de diferentes estímulos. Elementos como cor, contraste, posição e organização espacial influenciam significativamente o que tende a atrair o olhar humano. Bylinskii et al. (2015) demonstram que características intrínsecas e extrínsecas das imagens afetam diretamente sua memorabilidade, enquanto Țichindelean et al. (2021) evidenciam que técnicas de eye-tracking auxiliam na avaliação da usabilidade em interfaces digitais.

Neste contexto, este projeto investiga qual cor e qual posição espacial tendem a receber mais atenção quando apresentadas simultaneamente ao usuário. Para isso, utiliza-se um experimento simples baseado em estímulos circulares coloridos, registrados pelo sistema WebGazer.

## 2. Referencial Teórico

Diversas pesquisas ao longo dos últimos anos têm explorado a relação entre atenção visual e características dos estímulos apresentados:

Memorabilidade e atenção visual: Segundo Bylinskii et al. (2015), elementos com maior contraste visual, organização clara e cores marcantes apresentam maior probabilidade de atrair e manter a atenção, contribuindo para sua memorabilidade.

Influência das cores no engajamento: Yu (2023) demonstra que diferentes esquemas de cores alteram significativamente o engajamento do usuário com interfaces digitais, reforçando o papel psicológico e perceptivo das cores.

Usabilidade e eye-tracking: Țichindelean et al. (2021) analisam como padrões de fixação e movimentos oculares podem indicar problemas ou pontos fortes de usabilidade em layouts visuais.

Com base nesses estudos, este projeto usa cores simples e posições espaciais bem definidas (triângulo equilátero fixo) para isolar variáveis e observar padrões básicos de atenção.

## 3. Metodologia

A metodologia consiste em três etapas principais:

### 3.1. Ambiente do Experimento

O experimento foi implementado utilizando Streamlit e WebGazer.js, que permite rastrear a posição do olhar via webcam sem necessidade de hardware especializado.

Três círculos coloridos são exibidos simultaneamente em posições fixas que formam um triângulo em torno do centro da tela.

### 3.2. Ciclo do Estímulo

Cada ciclo é composto por:

Exibição dos círculos (5 segundos)

Três círculos aparecem em posições fixas:

Topo; Baixo-esquerda; Baixo-direita

Cada círculo recebe uma cor aleatória e distinta dentre um conjunto pré-definido.

Período em branco (2 segundos)

Os círculos desaparecem temporariamente para permitir “reset” perceptivo.

Novo ciclo

O processo se repete com novas cores, gerando novas oportunidades de coleta.

### 3.3. Coleta dos Dados

A cada amostra coletada, WebGazer registra:

- Coordenadas do olhar (x, y)
- Timestamp
- Círculo mais próximo no instante (nearestStimulusId)
- Cor associada (nearestStimulusColor)

Os dados ficam acessíveis via botão “Baixar dados em JSON”.

### 3.4. Análise dos Dados

Um script em Python processa o arquivo JSON e calcula:

- Tempo estimado de atenção por cor
- Tempo de fixação por posição do triângulo
- Contagem de amostras por cor e posição
- Tabela cruzada COR × POSIÇÃO
- Estimativa do intervalo médio entre amostras

Opcionalmente, gráficos podem ser gerados com matplotlib.

## 4. Resultados Esperados

Com base no referencial teórico e na configuração do experimento, espera-se:

- Identificar quais cores atraem mais a atenção do usuário.
- Verificar se existe preferência por certas regiões espaciais (ex.: topo > esquerda > direita).
- Observar padrões de retorno do olhar durante o período de exibição.
- Possibilidade de agrupar comportamentos similares entre usuários.

Embora simples, esse experimento pode fornecer insights valiosos sobre percepção visual, ergonomia, design de interfaces e psicologia das cores.

## 5. Conclusão

O projeto demonstra como é possível conduzir um experimento de eye-tracking funcional apenas com tecnologias acessíveis (WebGazer + Streamlit), sem a necessidade de equipamentos especializados. Através da análise dos dados coletados, é possível compreender padrões fundamentais de atenção visual, contribuindo tanto para estudos acadêmicos quanto para aplicações práticas em design, usabilidade, marketing e acessibilidade.

## 6. Referências Bibliográficas

BYLINSKII, Zoya; ISOLA, Phillip; BAINBRIDGE, Constance; TORRALBA, Antonio; OLIVA, Aude. Intrinsic and Extrinsic Effects on Image Memorability. Vision Research, v. 116, p. 165-178, 2015.

YU, Chao Hsuan. An Eye-tracking Study: Investigating the Impact of Website Theme Colors on Viewer Engagement. Dean & Francis Press, 2023. Disponível em: https://doi.org/10.61173/4fhyq880

ȚICHINDELEAN, M.; ȚICHINDELEAN, M. T.; CETINĂ, I.; ORZAN, G. A Comparative Eye Tracking Study of Usability—Towards Sustainable Web Design. Sustainability, v. 13, n. 10, p. 10415, 2021. DOI: https://doi.org/10.3390/su131810415
