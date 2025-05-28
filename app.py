import streamlit as st
import pandas as pd
import requests
from graphviz import Digraph
import base64
import matplotlib.pyplot as plt


# Coleta de dados da API do Studio Ghibli
url = "https://ghibliapi.vercel.app/films"
response = requests.get(url)

if response.status_code == 200:
    dados_filmes = response.json()
else:
    st.error("Erro ao acessar a API do Studio Ghibli")
    dados_filmes = []


# Implementação da estrutura de lista simplesmente encadeada
class No:
    def __init__(self, dados):
        self.dados = dados
        self.proximo = None


class Lista:
    def __init__(self):
        self.cabeca = None

    def contem(self, filme):
        atual = self.cabeca
        while atual:
            if atual.dados['id'] == filme['id']:
                return True
            atual = atual.proximo
        return False

    def inserir_final(self, dados):
        if self.contem(dados):
            return False

        novo_no = No(dados)
        if self.cabeca is None:
            self.cabeca = novo_no
        else:
            atual = self.cabeca
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo_no
        return True

    def remover_ultimo(self):
        if self.cabeca is None:
            return None
        if self.cabeca.proximo is None:
            removido = self.cabeca
            self.cabeca = None
            return removido
        atual = self.cabeca
        while atual.proximo.proximo:
            atual = atual.proximo
        removido = atual.proximo
        atual.proximo = None
        return removido

    def exibir(self):
        dados_lista = []
        atual = self.cabeca
        while atual:
            dados_lista.append(atual.dados)
            atual = atual.proximo
        return dados_lista

    def gerar_grafico(self):
        grafico = Digraph(comment='Lista de Filmes Assistidos')
        atual = self.cabeca
        contador = 0

        while atual:
            label = f"{atual.dados['title']}\\n({atual.dados['release_date']})"
            grafico.node(str(contador), label=label)

            if atual.proximo:
                grafico.edge(str(contador), str(contador + 1))

            atual = atual.proximo
            contador += 1

        return grafico

    def limpar(self):
        self.cabeca = None


# Configuração de tema
st.set_page_config(page_title="Studio Ghibli - Lista Encadeada", page_icon="🎥", layout="wide")


# Função para converter imagem em base64
def get_base64(file):
    with open(file, "rb") as f:
        data = f.read()
    return base64.b64encode(data).decode()


# Adiciona background e logo como parte do CSS
def add_background(img_fundo, img_logo):
    img_fundo_base64 = get_base64(img_fundo)
    img_logo_base64 = get_base64(img_logo)
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: #1b2e2d;
            background-image: 
                url("data:image/png;base64,{img_fundo_base64}"),
                url("data:image/png;base64,{img_logo_base64}");
            background-position: bottom right, top 150px left 10px;
            background-repeat: no-repeat, no-repeat;
            background-size: 30vw, 120px;
            background-attachment: scroll, scroll;
        }}

        @media (max-width: 768px) {{
            .stApp {{
                background-size: 40vw, 80px;
                background-position: bottom right, top 150px left 10px;
            }}
        }}

        body {{
            color: white;
        }}

        .stButton>button {{
            background-color: #f28482;
            color: white;
            border-radius: 8px;
            height: 3em;
            font-size: 16px;
        }}

        .stButton>button:hover {{
            background-color: #f2a29e;
            color: black;
        }}

        hr {{
            border: 1px solid #f28482;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )


# Adiciona o background
add_background('assets/chihiro.png', 'assets/logo.png')


# Inicialização da lista e controle de sessão
if 'lista' not in st.session_state:
    st.session_state.lista = Lista()

if 'filmes_disponiveis' not in st.session_state:
    st.session_state.filmes_disponiveis = dados_filmes.copy()

lista = st.session_state.lista


# Função para atualizar a interface
def atualizar_interface():
    try:
        st.rerun()
    except AttributeError:
        try:
            st.experimental_rerun()
        except AttributeError:
            st.warning("Recarregamento automático não suportado na sua versão do Streamlit.")


# Layout utilizando colunas para deslocamento à esquerda
col_esq, col_centro, col_dir = st.columns([1.2, 2, 0.8])

with col_centro:
    st.markdown("<h1 style='text-align: left;'>Studio Ghibli - Lista Encadeada</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: left;'>Organize os filmes que você já assistiu</p>", unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.subheader("Selecione os Filmes Assistidos")

    opcoes = [
        f"{i + 1}. {filme['title']} ({filme['release_date']}) - Diretor: {filme['director']}"
        for i, filme in enumerate(st.session_state.filmes_disponiveis)
    ]

    selecionados = st.multiselect("Escolha os filmes:", options=opcoes, key="multiselect_filmes")

    col1, col2, col3 = st.columns([1, 1, 1])

    with col1:
        if st.button("Adicionar Filme(s)", use_container_width=True):
            if selecionados:
                indices_para_remover = []
                for item in selecionados:
                    indice = int(item.split('.')[0]) - 1
                    filme = st.session_state.filmes_disponiveis[indice]
                    sucesso = lista.inserir_final(filme)
                    if sucesso:
                        st.success(f"Adicionado: {filme['title']}")
                        indices_para_remover.append(indice)
                    else:
                        st.warning(f"O filme '{filme['title']}' já está na lista.")
                st.session_state.filmes_disponiveis = [
                    filme for i, filme in enumerate(st.session_state.filmes_disponiveis) if i not in indices_para_remover
                ]
                atualizar_interface()
            else:
                st.warning("Nenhum filme selecionado para adicionar.")

    with col2:
        if st.button("Remover Último", use_container_width=True):
            removido = lista.remover_ultimo()
            if removido:
                st.success(f"Removido: {removido.dados['title']}")
                st.session_state.filmes_disponiveis.append(removido.dados)
                atualizar_interface()
            else:
                st.warning("A lista está vazia.")

    with col3:
        if st.button("Limpar Lista", use_container_width=True):
            lista.limpar()
            st.session_state.filmes_disponiveis = dados_filmes.copy()
            st.success("Lista limpa com sucesso.")
            atualizar_interface()

    st.subheader("Lista Atual de Filmes Assistidos")

    dados_atual = lista.exibir()

    if dados_atual:
        df = pd.DataFrame(dados_atual)
        df = df[['title', 'director', 'release_date', 'rt_score']]
        df.columns = ['Título', 'Diretor', 'Ano', 'Score']
        st.dataframe(df)
    else:
        st.info("Nenhum filme na lista no momento. Adicione filmes para começar.")

    st.subheader("Visualizações")

    col_grafico_lista, col_grafico_scores = st.columns([1, 1])

    with col_grafico_lista:
        if st.button("🎬 Gerar Gráfico da Lista", use_container_width=True):
            if lista.cabeca is not None:
                grafico = lista.gerar_grafico()
                st.graphviz_chart(grafico.source)
            else:
                st.warning("A lista está vazia. Adicione filmes para gerar o gráfico.")

    with col_grafico_scores:
        if st.button("🍅 Gerar Gráfico de Scores", use_container_width=True):
            if dados_atual:
                df_scores = pd.DataFrame(dados_atual)
                df_scores['rt_score'] = pd.to_numeric(df_scores['rt_score'], errors='coerce')
                df_scores = df_scores.sort_values(by='rt_score', ascending=False)

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.barh(df_scores['title'], df_scores['rt_score'], color='#f28482')
                ax.set_xlabel('Pontuação (Rotten Tomatoes)')
                ax.set_ylabel('Filmes')
                ax.set_title('Pontuação dos Filmes no Rotten Tomatoes')
                ax.invert_yaxis()
                st.pyplot(fig)
            else:
                st.warning("A lista está vazia. Adicione filmes para gerar o gráfico de scores.")
