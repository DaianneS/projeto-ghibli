class No:
    def __init__(self, dados):
        self.dados = dados
        self.proximo = None


class ListaEncadeada:
    def __init__(self):
        self.cabeca = None

    def inserir(self, dados):
        novo_no = No(dados)
        if self.cabeca is None:
            self.cabeca = novo_no
        else:
            atual = self.cabeca
            while atual.proximo:
                atual = atual.proximo
            atual.proximo = novo_no

    def exibir_lista(self):
        dados_lista = []
        atual = self.cabeca
        while atual:
            dados_lista.append(atual.dados)
            atual = atual.proximo
        return dados_lista

    def gerar_graphviz(self):
        from graphviz import Digraph

        grafico = Digraph()
        atual = self.cabeca
        contador = 0
        while atual:
            label = f"{atual.dados['title']}\n({atual.dados['release_date']})"
            grafico.node(str(contador), label=label)
            if atual.proximo:
                grafico.edge(str(contador), str(contador + 1))
            atual = atual.proximo
            contador += 1
        return grafico

    def resetar(self):
        self.cabeca = None