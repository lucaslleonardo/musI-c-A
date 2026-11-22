import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

import main

app = FastAPI(title="Recomendação musica ia")



class PedidoSugestao(BaseModel):
    artistas: list[str]
    recusados: list[str] = []


class PedidoAlbuns(BaseModel):
    artista: str
    frase: str



def erro_artista_nao_encontrado():
    return HTTPException(
        status_code=404,
        detail="Não encontrei dados no Last.fm para um dos artistas. Confira os nomes.",
    )


def erro_servico_indisponivel():
    return HTTPException(
        status_code=502,
        detail="Não consegui falar com o Last.fm agora. Tente novamente em instantes.",
    )



@app.get("/")
def raiz():
    return {"mensagem": "Music Discovery Agent no ar"}


@app.get("/artista/{nome}")
def mostrar_artista(nome: str):
    try:
        sobre = main.buscar_sobre(nome)
    except KeyError:
        raise erro_artista_nao_encontrado()
    except requests.RequestException:
        raise erro_servico_indisponivel()

    return {"artista": nome, "sobre": sobre}


@app.post("/sugestao")
def sugerir(pedido: PedidoSugestao):
    try:
        candidatos = main.montar_candidatos(pedido.artistas)

        recusados_normalizados = []
        for nome in pedido.recusados:
            recusados_normalizados.append(main.normalizar(nome))

        disponiveis = []
        for candidato in candidatos:
            if main.normalizar(candidato) not in recusados_normalizados:
                disponiveis.append(candidato)

        if not disponiveis:
            return {"artista": None, "sobre": None}

        escolhido = main.escolher_candidato(pedido.artistas, disponiveis)
        sobre = main.buscar_sobre(escolhido)
    except KeyError:
        raise erro_artista_nao_encontrado()
    except requests.RequestException:
        raise erro_servico_indisponivel()

    return {"artista": escolhido, "sobre": sobre}


@app.post("/albuns")
def sugerir_albuns(pedido: PedidoAlbuns):
    tags_clima = main.interpretar_atmosfera(pedido.frase)

    try:
        albuns = main.ordenar_albuns(pedido.artista, tags_clima)
    except KeyError:
        raise erro_artista_nao_encontrado()
    except requests.RequestException:
        raise erro_servico_indisponivel()

    return {"tags_clima": tags_clima, "albuns": albuns}