import json
from dotenv import load_dotenv
from google import genai

load_dotenv()
client = genai.Client()


def interpretar_atmosfera(frase):
    prompt = f"""Você traduz pedidos de clima musical em tags de música.

Pedido do usuário: "{frase}"

Responda SOMENTE com um JSON neste formato, sem nenhum texto antes ou depois:
{{"tags": ["tag1", "tag2", "tag3"]}}

Use de 2 a 4 tags, em inglês, em minúsculas, como as usadas no Last.fm
(exemplos: melancholic, dark, electronic, chill, dance, experimental)."""

    resposta = client.models.generate_content(
        model="gemini-3.1-flash-lite",
        contents=prompt,
        config={"response_mime_type": "application/json"},
    )

    return json.loads(resposta.text)


print(interpretar_atmosfera("quero algo pra dia de chuva, bem introspectivo"))