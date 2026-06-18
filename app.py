import streamlit as st
import pandas as pd
from datetime import datetime

# ===== CONFIGURAÇÃO =====
st.set_page_config(page_title="Chat BI · Assistente de Dados", page_icon="📊", layout="wide")

# ===== DADOS SIMULADOS (representam o modelo Power BI do cliente) =====
@st.cache_data
def load_data():
    vendas = pd.DataFrame({
        "Data": pd.date_range("2024-01-01", periods=12, freq="MS"),
        "Região": ["Sudeste","Sul","Nordeste","Norte","Sudeste","Sul","Nordeste","Norte","Sudeste","Sul","Nordeste","Norte"],
        "Produto": ["Produto A","Produto B","Produto C","Produto A","Produto B","Produto C","Produto A","Produto B","Produto C","Produto A","Produto B","Produto C"],
        "Receita": [125000,89000,67000,45000,132000,91000,72000,48000,145000,98000,78000,52000],
        "Custo": [75000,54000,42000,29000,78000,55000,44000,31000,85000,59000,47000,33000],
        "Unidades": [520,380,290,195,550,400,310,205,600,420,335,220],
        "Meta": [120000,85000,70000,50000,130000,90000,75000,50000,140000,95000,80000,55000],
    })
    vendas["Lucro"] = vendas["Receita"] - vendas["Custo"]
    vendas["Margem %"] = ((vendas["Lucro"] / vendas["Receita"]) * 100).round(1)
    vendas["Atingimento %"] = ((vendas["Receita"] / vendas["Meta"]) * 100).round(1)
    vendas["Mês"] = vendas["Data"].dt.strftime("%b/%Y")
    return vendas

df = load_data()

# ===== MOTOR DE INTERPRETAÇÃO (simula a camada de IA) =====
def interpret_query(query: str) -> dict:
    """Interpreta a pergunta e retorna dados + insight. Em produção, aqui entra a OpenAI/LLM."""
    q = query.lower()

    # Faturamento total
    if any(w in q for w in ["faturamento total", "receita total", "quanto faturou", "quanto vendeu"]):
        total = df["Receita"].sum()
        return {
            "tabela": df.groupby("Mês")[["Receita","Custo","Lucro"]].sum().reset_index(),
            "insight": f"💰 **Faturamento total no período:** R$ {total:,.0f}\n\nA receita acumulada dos 12 meses é de R$ {total:,.0f}, com lucro líquido de R$ {df['Lucro'].sum():,.0f} ({(df['Lucro'].sum()/total*100):.1f}% de margem)."
        }

    # Por região
    if "região" in q or "regional" in q or "regiões" in q:
        tab = df.groupby("Região").agg(Receita=("Receita","sum"), Lucro=("Lucro","sum"), Unidades=("Unidades","sum")).reset_index().sort_values("Receita", ascending=False)
        melhor = tab.iloc[0]
        return {
            "tabela": tab,
            "insight": f"🗺️ **Melhor região:** {melhor['Região']} com R$ {melhor['Receita']:,.0f} em receita.\n\nO Sudeste concentra {(melhor['Receita']/df['Receita'].sum()*100):.0f}% do faturamento total. Nordeste mostra potencial de crescimento."
        }

    # Por produto
    if "produto" in q or "produtos" in q or "mais vendido" in q:
        tab = df.groupby("Produto").agg(Receita=("Receita","sum"), Unidades=("Unidades","sum"), Margem_Media=("Margem %","mean")).reset_index().sort_values("Receita", ascending=False)
        tab["Margem_Media"] = tab["Margem_Media"].round(1)
        top = tab.iloc[0]
        return {
            "tabela": tab,
            "insight": f"📦 **Produto destaque:** {top['Produto']} com R$ {top['Receita']:,.0f} e {top['Unidades']:,.0f} unidades vendidas.\n\nEste produto lidera tanto em receita quanto em volume."
        }

    # Meta / atingimento
    if "meta" in q or "atingimento" in q or "bateu" in q or "objetivo" in q:
        tab = df[["Mês","Região","Receita","Meta","Atingimento %"]].copy()
        media = tab["Atingimento %"].mean()
        acima = (tab["Atingimento %"] >= 100).sum()
        return {
            "tabela": tab,
            "insight": f"🎯 **Atingimento médio:** {media:.1f}%\n\n{acima} de {len(tab)} períodos atingiram ou superaram a meta. Desempenho consistente no Sudeste."
        }

    # Margem / lucro
    if "margem" in q or "lucro" in q or "lucratividade" in q:
        tab = df.groupby("Região").agg(Margem_Media=("Margem %","mean"), Lucro_Total=("Lucro","sum")).reset_index().sort_values("Margem_Media", ascending=False)
        tab["Margem_Media"] = tab["Margem_Media"].round(1)
        return {
            "tabela": tab,
            "insight": f"📈 **Maior margem:** {tab.iloc[0]['Região']} com {tab.iloc[0]['Margem_Media']}% de margem média.\n\nTodas as regiões operam com margem saudável acima de 35%."
        }

    # Top meses
    if "melhor mês" in q or "melhor mes" in q or "mês" in q or "mensal" in q or "evolução" in q:
        tab = df.groupby("Mês").agg(Receita=("Receita","sum"), Lucro=("Lucro","sum"), Unidades=("Unidades","sum")).reset_index()
        melhor = tab.loc[tab["Receita"].idxmax()]
        return {
            "tabela": tab,
            "insight": f"📅 **Melhor mês:** {melhor['Mês']} com R$ {melhor['Receita']:,.0f} de receita.\n\nTendência de crescimento ao longo do ano, com pico no 3º trimestre."
        }

    # Custo
    if "custo" in q or "despesa" in q or "gasto" in q:
        tab = df.groupby("Região").agg(Custo_Total=("Custo","sum"), Receita_Total=("Receita","sum")).reset_index()
        tab["% Custo/Receita"] = ((tab["Custo_Total"] / tab["Receita_Total"]) * 100).round(1)
        return {
            "tabela": tab,
            "insight": f"💸 **Custo total:** R$ {df['Custo'].sum():,.0f} ({(df['Custo'].sum()/df['Receita'].sum()*100):.1f}% da receita).\n\nOs custos estão controlados, representando menos de 62% do faturamento em todas as regiões."
        }

    # Unidades
    if "unidade" in q or "volume" in q or "quantidade" in q:
        tab = df.groupby("Produto").agg(Unidades=("Unidades","sum")).reset_index().sort_values("Unidades", ascending=False)
        total_un = df["Unidades"].sum()
        return {
            "tabela": tab,
            "insight": f"📊 **Total de unidades vendidas:** {total_un:,.0f}\n\nO Produto A lidera em volume, seguido por B e C."
        }

    # Resumo executivo (fallback)
    resumo = pd.DataFrame({
        "Métrica": ["Receita Total", "Lucro Total", "Margem Média", "Unidades Vendidas", "Atingimento Médio de Meta"],
        "Valor": [
            f"R$ {df['Receita'].sum():,.0f}",
            f"R$ {df['Lucro'].sum():,.0f}",
            f"{df['Margem %'].mean():.1f}%",
            f"{df['Unidades'].sum():,.0f}",
            f"{df['Atingimento %'].mean():.1f}%"
        ]
    })
    return {
        "tabela": resumo,
        "insight": "📋 **Resumo executivo do relatório.**\n\nAqui estão os principais KPIs. Pergunte sobre **regiões**, **produtos**, **metas**, **margem**, **custos** ou **evolução mensal** para detalhes específicos."
    }

# ===== INTERFACE =====
# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/c/cf/New_Power_BI_Logo.svg/200px-New_Power_BI_Logo.svg.png", width=48)
    st.markdown("### Chat BI")
    st.markdown("Assistente inteligente conectado ao seu relatório Power BI.")
    st.divider()
    st.markdown("**Perguntas de exemplo:**")
    exemplos = [
        "Qual o faturamento total?",
        "Como estão as vendas por região?",
        "Qual o produto mais vendido?",
        "Estamos batendo a meta?",
        "Qual a margem de lucro?",
        "Qual foi o melhor mês?",
        "Como estão os custos?",
    ]
    for ex in exemplos:
        if st.button(ex, key=ex, use_container_width=True):
            st.session_state.pending_question = ex
    st.divider()
    st.caption("Demo funcional · Em produção conecta à API do Power BI + OpenAI")

# Header
st.markdown("## 📊 Chat BI — Assistente de Dados")
st.caption("Faça perguntas em linguagem natural sobre seu relatório Power BI")

# Chat history
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Olá! 👋 Sou o assistente do seu relatório Power BI.\n\nMe pergunte qualquer coisa sobre vendas, regiões, produtos, metas ou custos. Responderei com tabelas e insights.\n\n**Tente:** _Qual o faturamento total?_"}
    ]

# Display messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if "tabela" in msg:
            st.dataframe(msg["tabela"], use_container_width=True, hide_index=True)

# Input
prompt = st.chat_input("Faça uma pergunta sobre o relatório...")

# Handle sidebar button clicks
if "pending_question" in st.session_state:
    prompt = st.session_state.pending_question
    del st.session_state.pending_question

if prompt:
    # User message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Assistant response
    result = interpret_query(prompt)
    response_text = result["insight"]
    with st.chat_message("assistant"):
        st.markdown(response_text)
        st.dataframe(result["tabela"], use_container_width=True, hide_index=True)

    st.session_state.messages.append({"role": "assistant", "content": response_text, "tabela": result["tabela"]})
