# Chat BI — Assistente de Dados para Power BI

Chat em Streamlit que permite ao usuário interagir em linguagem natural com dados de relatório Power BI, recebendo respostas em tabelas e insights.

## Demo

Este é um modelo funcional com dados simulados. Em produção, conecta à API do Power BI + OpenAI para interpretar perguntas e consultar dados reais.

## Executar

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Arquitetura em Produção

```
Usuário → Streamlit (chat) → OpenAI (interpreta pergunta → gera DAX/query)
                                          ↓
                              Power BI REST API (executa query)
                                          ↓
                              Retorna dados → formata tabela + insight
```

## Perguntas suportadas no demo

- Faturamento total
- Vendas por região
- Produto mais vendido
- Atingimento de metas
- Margem de lucro
- Evolução mensal
- Análise de custos
