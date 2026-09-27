# RELATÓRIO — Resultados e interpretação das análises

## Análise 1 — Pokémon por tipo primário e geração

| Tipo primário | Geração | Quantidade |
| ------------- | ------: | ---------: |
| bug           |       1 |         14 |
| dragon        |       1 |          3 |
| electric      |       1 |          9 |
| fairy         |       1 |          2 |
| fighting      |       1 |          7 |
| fire          |       1 |         14 |
| ghost         |       1 |          4 |
| grass         |       1 |         13 |
| ground        |       1 |          8 |
| ice           |       1 |          2 |
| normal        |       1 |         24 |
| poison        |       1 |         14 |
| psychic       |       1 |         11 |
| rock          |       1 |         10 |
| water         |       1 |         31 |
| bug           |       2 |         12 |
| dark          |       2 |          6 |
| electric      |       2 |          7 |
| fairy         |       2 |          5 |
| fighting      |       2 |          2 |
| fire          |       2 |          8 |
| ghost         |       2 |          1 |
| grass         |       2 |          9 |
| ground        |       2 |          3 |
| ice           |       2 |          4 |
| normal        |       2 |         15 |
| poison        |       2 |          1 |
| psychic       |       2 |          7 |
| rock          |       2 |          5 |
| steel         |       2 |          3 |
| water         |       2 |         18 |
| bug           |       3 |         12 |
| dark          |       3 |          6 |
| dragon        |       3 |         12 |
| electric      |       3 |          5 |
| fighting      |       3 |          5 |
| fire          |       3 |          8 |
| ghost         |       3 |          5 |
| grass         |       3 |         13 |
| ground        |       3 |          7 |
| ice           |       3 |          7 |
| normal        |       3 |         18 |
| poison        |       3 |          3 |
| psychic       |       3 |         12 |
| rock          |       3 |          8 |
| steel         |       3 |         12 |
| water         |       3 |         27 |
| bug           |       4 |         10 |
| dark          |       4 |          3 |
| dragon        |       4 |          4 |
| electric      |       4 |         12 |
| fairy         |       4 |          1 |
| fighting      |       4 |          3 |
| fire          |       4 |          5 |
| ghost         |       4 |          7 |
| grass         |       4 |         15 |
| ground        |       4 |          4 |
| ice           |       4 |          3 |
| normal        |       4 |         18 |
| poison        |       4 |          6 |
| psychic       |       4 |          8 |
| rock          |       4 |          6 |
| steel         |       4 |          3 |
| water         |       4 |         13 |
| bug           |       5 |         18 |
| dark          |       5 |         13 |
| dragon        |       5 |          9 |
| electric      |       5 |          8 |
| fighting      |       5 |          7 |
| fire          |       5 |          9 |
| flying        |       5 |          2 |
| ghost         |       5 |          5 |
| grass         |       5 |         15 |
| ground        |       5 |         10 |
| ice           |       5 |          6 |
| normal        |       5 |         19 |
| poison        |       5 |          2 |
| psychic       |       5 |         14 |
| rock          |       5 |          6 |
| steel         |       5 |          4 |
| water         |       5 |         18 |
| bug           |       6 |          3 |
| dark          |       6 |          3 |
| dragon        |       6 |          4 |
| electric      |       6 |          3 |
| fairy         |       6 |          9 |
| fighting      |       6 |          3 |
| fire          |       6 |          8 |
| flying        |       6 |          2 |
| ghost         |       6 |         10 |
| grass         |       6 |          5 |
| ice           |       6 |          2 |
| normal        |       6 |          4 |
| poison        |       6 |          2 |
| psychic       |       6 |          5 |
| rock          |       6 |          9 |
| steel         |       6 |          5 |
| water         |       6 |          5 |

**Interpretação:** A distribuição dos Pokémon por tipo primário e geração não é uniforme. O tipo Water apresenta grande representação em várias gerações, especialmente na geração 1, com 31 Pokémon, e na geração 3, com 27. Normal, Grass e Bug também apresentam quantidades elevadas em diferentes gerações.

A dimensão `silver.dim_pokemon` possui 800 registros, correspondentes aos registros conciliados utilizados na modelagem. A distribuição apresentada nesta consulta não indica perda de registros por falha de conciliação, pois os Pokémon estão distribuídos entre suas respectivas gerações e tipos primários. A consulta resultou em 98 combinações distintas de tipo e geração.

## Análise 2 — Média de status por tipo primário

| Tipo primário | HP médio | Ataque médio | Defesa média | Ataque especial médio | Defesa especial média | Velocidade média |
| ------------- | -------: | -----------: | -----------: | --------------------: | --------------------: | ---------------: |
| flying        |     70,8 |         78,8 |         66,3 |                  94,3 |                  72,5 |            102,5 |
| electric      |     59,8 |         69,1 |         66,3 |                  90,0 |                  73,7 |             84,5 |
| dragon        |     83,3 |        112,1 |         86,4 |                  96,8 |                  88,8 |             83,0 |
| psychic       |     70,6 |         71,5 |         67,7 |                  98,4 |                  86,3 |             81,5 |
| dark          |     66,8 |         88,4 |         70,2 |                  74,6 |                  69,5 |             76,2 |
| fire          |     69,9 |         84,8 |         67,8 |                  89,0 |                  72,2 |             74,4 |
| normal        |     77,3 |         73,5 |         59,8 |                  55,8 |                  63,7 |             71,6 |
| fighting      |     69,9 |         96,8 |         65,9 |                  53,1 |                  64,7 |             66,1 |
| water         |     72,1 |         74,2 |         72,9 |                  74,8 |                  70,5 |             66,0 |
| ghost         |     64,4 |         73,8 |         81,2 |                  79,3 |                  76,5 |             64,3 |
| ground        |     73,8 |         95,8 |         84,8 |                  56,5 |                  62,8 |             63,9 |
| poison        |     67,3 |         74,7 |         68,8 |                  60,4 |                  64,4 |             63,6 |
| ice           |     72,0 |         72,8 |         71,4 |                  77,5 |                  76,3 |             63,5 |
| grass         |     67,3 |         73,2 |         70,8 |                  77,5 |                  70,4 |             61,9 |
| bug           |     56,9 |         71,0 |         70,7 |                  53,9 |                  64,8 |             61,7 |
| rock          |     65,4 |         92,9 |        100,8 |                  63,3 |                  75,5 |             55,9 |
| steel         |     65,2 |         92,7 |        126,4 |                  67,5 |                  80,6 |             55,3 |
| fairy         |     74,1 |         61,5 |         65,7 |                  78,5 |                  84,7 |             48,6 |

**Interpretação:** O tipo Flying apresenta a maior velocidade média, com 102,5. Em relação ao "bulk", considerando conjuntamente HP e Defesa, Dragon apresenta HP médio de 83,3 e Defesa de 86,4, enquanto Steel apresenta Defesa média de 126,4 e HP médio de 65,2. Assim, os tipos apresentam perfis diferentes de atributos defensivos.

Dragon apresenta o maior ataque médio, com 112,1, e também o maior HP médio, com 83,3. Steel possui a maior defesa média, com 126,4. Psychic apresenta o maior ataque especial médio, com 98,4, enquanto Dragon possui a maior defesa especial média, com 88,8.

Nenhum tipo apresenta simultaneamente os maiores valores em todos os atributos. Os resultados indicam diferentes especializações entre os tipos.

## Análise 3 — Taxa de vitórias por Pokémon (10 maiores / 10 menores, corte ≥ 20 combates)

| Nome                     | Tipo primário | Combates | Taxa de vitórias |
| ------------------------ | ------------- | -------: | ---------------: |
| Mega Aerodactyl          | rock          |      129 |           0,9845 |
| Weavile                  | dark          |      119 |           0,9748 |
| Tornadus Therian Forme   | flying        |      125 |           0,9680 |
| Mega Beedrill            | bug           |      119 |           0,9664 |
| Aerodactyl               | rock          |      141 |           0,9645 |
| Mega Lopunny             | normal        |      129 |           0,9612 |
| Greninja                 | water         |      127 |           0,9606 |
| Meloetta Pirouette Forme | normal        |      123 |           0,9593 |
| Mega Mewtwo Y            | psychic       |      125 |           0,9520 |
| Mega Sharpedo            | water         |      120 |           0,9500 |
| Shuckle                  | bug           |      135 |           0,0000 |
| Silcoon                  | bug           |      138 |           0,0217 |
| Togepi                   | fairy         |      122 |           0,0246 |
| Solosis                  | psychic       |      129 |           0,0310 |
| Slugma                   | fire          |      123 |           0,0325 |
| Munna                    | psychic       |      128 |           0,0391 |
| Igglybuff                | normal        |      115 |           0,0435 |
| Wynaut                   | psychic       |      130 |           0,0462 |
| Wooper                   | water         |      125 |           0,0480 |
| Cascoon                  | bug           |      133 |           0,0526 |

**Interpretação:** O corte de pelo menos 20 combates reduz a influência de amostras muito pequenas no ranking. Mesmo com esse critério, existe uma grande diferença entre os extremos: Mega Aerodactyl apresenta taxa de vitória de 98,45%, enquanto Shuckle apresenta 0%.

Os extremos também mostram que o tipo primário, isoladamente, não determina o resultado. Bug, por exemplo, aparece tanto entre os maiores resultados, com Mega Beedrill (96,64%), quanto entre os menores, com Shuckle (0%) e Cascoon (5,26%). Isso indica que os atributos individuais e as demais características utilizadas pelo simulador têm influência importante.

## Análise 4 — Taxa de vitórias por tipo primário

| Tipo     | Combates | Vitórias | Taxa de vitórias |
| -------- | -------: | -------: | ---------------: |
| flying   |      478 |      362 |           0,7573 |
| dark     |    3.845 |    2.447 |           0,6364 |
| dragon   |    3.932 |    2.490 |           0,6333 |
| electric |    5.346 |    3.370 |           0,6304 |
| fire     |    6.552 |    3.802 |           0,5803 |
| psychic  |    7.320 |    3.998 |           0,5462 |
| normal   |   12.098 |    6.518 |           0,5388 |
| ground   |    3.889 |    2.088 |           0,5369 |
| ghost    |    3.908 |    1.877 |           0,4803 |
| water    |   14.041 |    6.569 |           0,4678 |
| fighting |    3.306 |    1.543 |           0,4667 |
| ice      |    3.079 |    1.357 |           0,4407 |
| grass    |    8.426 |    3.707 |           0,4399 |
| bug      |    8.760 |    3.772 |           0,4306 |
| poison   |    3.654 |    1.571 |           0,4299 |
| steel    |    3.546 |    1.523 |           0,4295 |
| rock     |    5.669 |    2.299 |           0,4055 |
| fairy    |    2.151 |      707 |           0,3287 |

**Interpretação:** As taxas de vitória variam consideravelmente entre os tipos. Flying apresenta taxa de 75,73%, enquanto Fairy apresenta 32,87%.

Ao comparar com a Análise 2, observa-se que Flying também possui a maior velocidade média, de 102,5. Fairy, por outro lado, possui a menor velocidade média, de 48,6. Isso mostra uma associação entre velocidade média e taxa de vitória nesses dois casos.

Entretanto, a relação não é suficiente para explicar todos os resultados. Por exemplo, Steel apresenta velocidade média de 55,3 e taxa de vitória de 42,95%, enquanto Dragon apresenta velocidade média de 83,0 e taxa de 63,33%. Portanto, a velocidade pode contribuir para o desempenho, mas não explica sozinha as diferenças entre os tipos.

## Análise 5 — Diferença de velocidade x vitória

| Faixa                        | Combates | Taxa de vitórias |
| ---------------------------- | -------: | ---------------: |
| 1 - Muito mais lento (≤ -50) |   12.407 |           0,0940 |
| 2 - Mais lento (-49 a -10)   |   29.432 |           0,0553 |
| 3 - Similar (-9 a 9)         |   16.322 |           0,5000 |
| 4 - Mais rápido (10 a 49)    |   29.432 |           0,9447 |
| 5 - Muito mais rápido (≥ 50) |   12.407 |           0,9060 |

**Interpretação:** A diferença de velocidade apresenta uma relação muito forte com a taxa de vitória no conjunto analisado. Nos confrontos em que os Pokémon possuem velocidades semelhantes, a taxa de vitória é de 50%.

Quando o Pokémon está entre 10 e 49 pontos mais rápido, a taxa de vitória sobe para 94,47%. Já quando está entre 10 e 49 pontos mais lento, a taxa é de apenas 5,53%.

A relação não é estritamente monotônica nas categorias extremas, pois "Muito mais lento" apresenta 9,40%, enquanto "Mais lento" apresenta 5,53%; da mesma forma, "Mais rápido" apresenta 94,47%, enquanto "Muito mais rápido" apresenta 90,60%. Mesmo assim, existe uma diferença muito clara entre estar em vantagem ou desvantagem de velocidade.

Os resultados sugerem que a velocidade possui forte influência no resultado dos combates do simulador, possivelmente relacionada à ordem de atuação ou a algum critério de desempate.

## Análise 6 — Vantagem de tipo (multiplicador) x vitória

| Multiplicador | Combates | Taxa de vitórias |
| ------------: | -------: | ---------------: |
|          0,00 |    1.831 |           0,3162 |
|          0,50 |   19.028 |           0,4755 |
|          1,00 |   64.764 |           0,5004 |
|          2,00 |   14.377 |           0,5542 |

**Interpretação:** Existe uma tendência positiva entre o multiplicador de efetividade e a taxa de vitória observada. Os confrontos com multiplicador 0 apresentam taxa de 31,62%, enquanto os confrontos com multiplicador 2 apresentam taxa de 55,42%.

Apesar disso, a diferença não é suficiente para indicar que a efetividade de tipo determina o vencedor. Mesmo com multiplicador 2, a taxa de vitória é de 55,42%, próxima de uma distribuição equilibrada.

Além disso, a maior parte dos confrontos está concentrada no multiplicador 1, com 64.764 ocorrências e taxa de 50,04%. Isso indica que outros fatores do simulador também possuem influência relevante sobre o resultado.

## Análise 7 — Matriz de confronto 18x18 e posições divergentes

A matriz possui **18 × 18 = 324 combinações** de tipos.

As posições identificadas como divergentes foram:

| Tipo atacante | Tipo defensor | Combates | Taxa de vitórias do atacante | Multiplicador |
| ------------- | ------------- | -------: | ---------------------------: | ------------: |
| water         | water         |    1.942 |                       0,5000 |          0,50 |
| grass         | water         |    1.208 |                       0,4983 |          2,00 |
| water         | grass         |    1.208 |                       0,5017 |          0,50 |
| water         | fire          |      931 |                       0,4157 |          2,00 |
| fire          | water         |      931 |                       0,5843 |          0,50 |
| grass         | grass         |      708 |                       0,5000 |          0,50 |
| normal        | rock          |      682 |                       0,6056 |          0,50 |
| bug           | psychic       |      646 |                       0,4241 |          2,00 |
| water         | ground        |      571 |                       0,4694 |          2,00 |
| psychic       | psychic       |      518 |                       0,5000 |          0,50 |
| ghost         | normal        |      484 |                       0,5062 |          0,00 |
| electric      | grass         |      459 |                       0,6667 |          0,50 |
| fighting      | normal        |      443 |                       0,4402 |          2,00 |
| fire          | fire          |      430 |                       0,5000 |          0,50 |
| normal        | steel         |      422 |                       0,5782 |          0,50 |
| fire          | rock          |      358 |                       0,6034 |          0,50 |
| rock          | fire          |      358 |                       0,3966 |          2,00 |
| ground        | bug           |      335 |                       0,5224 |          0,50 |
| ground        | grass         |      318 |                       0,5094 |          0,50 |
| grass         | ground        |      318 |                       0,4906 |          2,00 |
| bug           | dark          |      309 |                       0,3625 |          2,00 |
| ghost         | psychic       |      289 |                       0,4498 |          2,00 |
| psychic       | steel         |      279 |                       0,5520 |          0,50 |
| grass         | steel         |      274 |                       0,5036 |          0,50 |
| fighting      | bug           |      271 |                       0,5720 |          0,50 |
| electric      | electric      |      268 |                       0,5000 |          0,50 |
| ground        | fire          |      266 |                       0,4812 |          2,00 |
| poison        | rock          |      194 |                       0,6082 |          0,50 |
| bug           | fairy         |      190 |                       0,6105 |          0,50 |
| ghost         | ghost         |      166 |                       0,5000 |          2,00 |
| dragon        | dragon        |      150 |                       0,5000 |          2,00 |
| poison        | poison        |      148 |                       0,5000 |          0,50 |
| dark          | dark          |      148 |                       0,5000 |          0,50 |
| steel         | steel         |      146 |                       0,5000 |          0,50 |
| dragon        | steel         |      141 |                       0,7943 |          0,50 |
| fighting      | poison        |      133 |                       0,5639 |          0,50 |
| ice           | dragon        |      116 |                       0,3103 |          2,00 |
| dark          | fighting      |      103 |                       0,5049 |          0,50 |
| fighting      | dark          |      103 |                       0,4951 |          2,00 |
| ice           | ice           |       94 |                       0,5000 |          0,50 |
| dark          | fairy         |       83 |                       0,7952 |          0,50 |
| fairy         | dark          |       83 |                       0,2048 |          2,00 |
| fighting      | fairy         |       62 |                       0,6613 |          0,50 |
| fairy         | fighting      |       62 |                       0,3387 |          2,00 |
| rock          | flying        |       24 |                       0,3333 |          2,00 |
| flying        | rock          |       24 |                       0,6667 |          0,50 |
| flying        | steel         |       21 |                       0,8571 |          0,50 |
| ice           | flying        |       20 |                       0,2000 |          2,00 |
| flying        | electric      |       16 |                       0,6875 |          0,50 |
| electric      | flying        |       16 |                       0,3125 |          2,00 |

**Interpretação:** Foram identificadas 50 posições divergentes na comparação realizada pela consulta. As divergências mostram que o multiplicador de efetividade não determina isoladamente a taxa de vitória observada.

Em alguns casos, a relação é bastante evidente. Por exemplo, Electric contra Ground possui multiplicador 0 e taxa de vitória de apenas 9,63%. Dragon contra Fairy também possui multiplicador 0 e taxa de vitória de 10,71%.

Em outros casos, porém, o resultado observado não acompanha diretamente o multiplicador. Grass contra Water possui multiplicador 2, mas taxa de vitória de aproximadamente 49,83%, praticamente equilibrada. Da mesma forma, Water contra Fire possui multiplicador 2, mas taxa de vitória de 41,57%.

Uma hipótese para as divergências é o tamanho da amostra em alguns pares de tipos, principalmente nas combinações com poucos combates. Entretanto, várias divergências também aparecem em pares com centenas ou milhares de confrontos, como Grass × Water e Water × Fire. Isso sugere que o simulador considera outros fatores além da efetividade de tipo, como os atributos individuais dos Pokémon e a velocidade.

## Análise 8 (proposta) — Taxa de vitórias por geração

**Pergunta de negócio:** a geração de origem do Pokémon influencia sua taxa de vitórias em combate?

| Geração | Combates | Taxa de vitórias |
| ------- | -------: | ---------------: |
| 1       |   20.311 |           0,5176 |
| 2       |   13.310 |           0,4482 |
| 3       |   20.388 |           0,4762 |
| 4       |   15.137 |           0,5391 |
| 5       |   20.607 |           0,5174 |
| 6       |   10.247 |           0,4871 |

**Interpretação:** As taxas de vitória variam entre as gerações, mas não apresentam uma tendência crescente ou decrescente conforme a geração avança.

A geração 4 apresenta a maior taxa, com 53,91%, enquanto a geração 2 apresenta a menor, com 44,82%. A diferença entre esses valores é de aproximadamente 9,09 pontos percentuais.

A geração 6, apesar de ser a mais recente considerada na análise, apresenta taxa de 48,71%, inferior às gerações 1, 4 e 5. Portanto, os resultados não indicam uma relação linear entre geração e taxa de vitória.

Dentro dos dados analisados, a geração de origem parece ter uma associação menor com o resultado dos combates do que fatores como a diferença de velocidade e as características individuais dos Pokémon.
