import json
import os
import unicodedata

import requests
from dotenv import load_dotenv
from google import genai

load_dotenv()
chave = os.getenv("LASTFM_API_KEY")
URL = "http://ws.audioscrobbler.com/2.0/"
client = genai.Client()


# ---------- ENTRADA E SAÍDA COM O USUÁRIO ----------

def pedir_artista(numero):
    while True:
        nome = input(f"Digite o {numero}º artista: ").strip()
        if nome:
            return nome
        print("ERRO! Resposta em branco.")


def pedir_texto(pergunta):
    while True:
        texto = input(pergunta).strip()
        if texto:
            return texto
        print("ERRO! Resposta em branco.")


def confirmar(pergunta):
    while True:
        resposta = input(pergunta).strip().lower()
        if resposta in ["sim", "s"]:
            return True
        if resposta in ["não", "nao", "n"]:
            return False
        print("Digite sim ou não.")


def listar_artistas(lista):
    print(" ")
    print("Artistas selecionados:")

    for indice, artista in enumerate(lista, start=1):
        print(f"{indice}. {artista}")


def sugerir_artista(nome):
    sobre = buscar_sobre(nome)
    print(" ")
    print(f"Artista sugerido: {nome}\nSobre: {sobre}")
    print(" ")


def sugerir_album(nome, tags_clima):
    albuns = ordenar_albuns(nome, tags_clima)

    if not albuns:
        print("Nenhum álbum encontrado.")
        return

    for i, album in enumerate(albuns):
        print(" ")
        print(f"Álbum sugerido: {album}")
        print(" ")

        if confirmar("Deseja ouvir este álbum? (sim/não): "):
            print("Boa escuta!")
            return

        if i < len(albuns) - 1:
            if not confirmar("Deseja sugestão de outro álbum? (sim/não): "):
                return

    print("Esses foram todos os álbuns que encontrei.")


# ---------- DADOS DO LAST.FM ----------

def buscar_tags(artista):
    parametros = {
        "method": "artist.getTopTags",
        "artist": artista,
        "api_key": chave,
        "format": "json",
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    nomes = []
    for tag in dados["toptags"]["tag"][:4]:
        nomes.append(tag["name"].lower())

    return nomes


def buscar_similares(artista):
    parametros = {
        "method": "artist.getSimilar",
        "artist": artista,
        "api_key": chave,
        "format": "json",
        "limit": 5,
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    nomes = []
    for item in dados["similarartists"]["artist"]:
        nomes.append(item["name"])

    return nomes


def buscar_albuns(artista):
    parametros = {
        "method": "artist.getTopAlbums",
        "artist": artista,
        "api_key": chave,
        "format": "json",
        "limit": 5,
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    nomes = []
    for album in dados["topalbums"]["album"]:
        if album["name"] != "(null)":
            nomes.append(album["name"])

    return nomes


def buscar_sobre(artista):
    parametros = {
        "method": "artist.getInfo",
        "artist": artista,
        "api_key": chave,
        "format": "json",
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    resumo = dados["artist"]["bio"]["summary"]
    resumo = resumo.split("<a href")[0].strip()

    if not resumo:
        return "Sem informações disponíveis."
    return resumo

def buscar_tags_album(artista, album):
    parametros = {
        "method": "album.getTopTags",
        "artist": artista,
        "album": album,
        "api_key": chave,
        "format": "json",
    }

    resposta = requests.get(URL, params=parametros)
    dados = resposta.json()

    lista_de_tags = dados.get("toptags", {}).get("tag", [])

    nomes = []
    for tag in lista_de_tags[:6]:
        nomes.append(tag["name"].lower())

    return nomes


# ---------- LÓGICA DE RECOMENDAÇÃO ----------

def normalizar(nome):
    nome = nome.strip().lower()
    decomposto = unicodedata.normalize("NFD", nome)  # separa o acento da letra, tipo a ´

    sem_acento = ""
    for letra in decomposto:
        if unicodedata.category(letra) != "Mn":  # pega o acento
            sem_acento += letra  # guarda só a letra

    return sem_acento

def montar_candidatos(artistas):
    artistas_normalizados = []
    for artista in artistas:
        artistas_normalizados.append(normalizar(artista))

    candidatos = []
    candidatos_normalizados = []
    for artista in artistas:
        for similar in buscar_similares(artista):
            nome_normalizado = normalizar(similar)
            if nome_normalizado not in artistas_normalizados and nome_normalizado not in candidatos_normalizados:
                candidatos.append(similar)
                candidatos_normalizados.append(nome_normalizado)

    return candidatos

def contar_tags_em_comum(artistas_usuario, candidato):
    tags_candidato = buscar_tags(candidato)
    pontos = 0

    for artista in artistas_usuario:
        for tag in buscar_tags(artista):
            if tag in tags_candidato:
                pontos += 1

    return pontos


def escolher_candidato(artistas_usuario, candidatos):
    melhor_candidato = None
    melhor_pontuacao = -1

    for candidato in candidatos:
        pontos = contar_tags_em_comum(artistas_usuario, candidato)
        if pontos > melhor_pontuacao:
            melhor_candidato = candidato
            melhor_pontuacao = pontos

    return melhor_candidato

def ordenar_albuns(artista, tags_clima):
    albuns = buscar_albuns(artista)
    pontuacoes = {}

    for album in albuns:
        tags_album = buscar_tags_album(artista, album)
        pontos = 0

        for tag in tags_clima:
            if tag in tags_album:
                pontos += 1

        pontuacoes[album] = pontos

    return sorted(albuns, key=pontuacoes.get, reverse=True)


# ---------- IA (GEMINI) ----------

def interpretar_atmosfera(frase):
    prompt = f"""Você traduz pedidos de clima musical em tags de música.

Pedido do usuário: "{frase}"

Responda SOMENTE com um JSON neste formato, sem nenhum texto antes ou depois:
{{"tags": ["tag1", "tag2", "tag3"]}}

Use de 2 a 4 tags, em inglês, em minúsculas, como as usadas no Last.fm
(exemplos: melancholic, dark, electronic, chill, dance, experimental)."""

    try:
        resposta = client.models.generate_content(
            model="gemini-3.1-flash-lite",
            contents=prompt,
            config={"response_mime_type": "application/json"},
        )
        return json.loads(resposta.text)["tags"]
    except Exception as erro:
        print(f"(IA indisponível: {erro})")
        return []



# ---------- CÓDIGO PRINCIPAL ----------
def main():
    artistas = []

    for i in range(1, 4):
        nome = pedir_artista(i)
        artistas.append(nome)

    listar_artistas(artistas)

    # candidatos = artistas parecidos que o usuário NÃO digitou
    artistas_normalizados = []
    for artista in artistas:
        artistas_normalizados.append(normalizar(artista))

    candidatos = []
    candidatos_normalizados = []
    for artista in artistas:
        for similar in buscar_similares(artista):
            nome_normalizado = normalizar(similar)
            if nome_normalizado not in artistas_normalizados and nome_normalizado not in candidatos_normalizados:
                candidatos.append(similar)
                candidatos_normalizados.append(nome_normalizado)

    aceitou = False


    while candidatos:
        artista_da_vez = escolher_candidato(artistas, candidatos)
        sugerir_artista(artista_da_vez)

        if confirmar(f"Deseja ouvir {artista_da_vez}? (sim/não): "):
            aceitou = True

            frase = pedir_texto("Que clima você quer ouvir hoje? ")
            tags_clima = interpretar_atmosfera(frase)
            print(" ")

            print("Gerando sugestão...")
            sugerir_album(artista_da_vez, tags_clima)
            break

        candidatos.remove(artista_da_vez)

        if candidatos:
            if not confirmar("Deseja sugestão de outro artista? (sim/não): "):
                break

    if not aceitou:
        print("Ok! Até a próxima!")

if __name__ == "__main__":
    main()