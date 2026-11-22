# Music Discovery Agent.V1

Agente de descoberta musical. Você informa três artistas, o programa sugere um artista parecido, pergunta qual clima você quer ouvir e recomenda um álbum que combine com ele. Funciona no terminal e também como uma API (FastAPI).

Os dados musicais vêm do [Last.fm](https://www.last.fm/api), e o clima é interpretado por um modelo de linguagem (Google Gemini).

> **Status:** em desenvolvimento. É um projeto de estudo para aprender Python na prática e integração com IA.

## O que ele faz

1. Pede três artistas ao usuário (com validação de campo vazio).
2. Busca artistas parecidos com cada um deles (`artist.getSimilar`).
3. Remove da lista de candidatos os artistas que o usuário já citou, ignorando maiúsculas e acentos (`Bjork` e `Björk` contam como o mesmo artista).
4. Dá uma pontuação a cada candidato, contando quantas **tags** ele tem em comum com os três artistas (`artist.getTopTags`).
5. Sugere o candidato com a maior pontuação, junto com um resumo da biografia (`artist.getInfo`).
6. Se o usuário recusar, sugere o próximo melhor, até alguém ser aceito ou a lista acabar.
7. Depois que um artista é aceito, pergunta o clima em texto livre (por exemplo, "algo pra dia de chuva").
8. O **Gemini traduz a frase em tags** em inglês (por exemplo, `melancholic`, `ambient`).
9. Os álbuns do artista (`artist.getTopAlbums`) são ordenados pela quantidade de tags em comum com o clima (`album.getTopTags`), e o programa sugere um de cada vez, com a opção de pedir outro.

### Exemplo de uso (terminal)

```
Digite o 1º artista: ...
Digite o 2º artista: ...
Digite o 3º artista: ...

Artista sugerido: <nome>
Sobre: <resumo da biografia no Last.fm>

Deseja ouvir <nome>? (sim/não): sim
Que clima você quer ouvir hoje? algo pra dia de chuva

Álbum sugerido: <álbum que mais combina com o clima>

Deseja ouvir este álbum? (sim/não):
```

<!-- Adicione aqui um print ou GIF do programa rodando. -->

## Como funciona a recomendação

O **LLM só interpreta a linguagem**. Quem decide é o código, com base em dados reais do Last.fm. Isso evita que o modelo invente artistas ou álbuns e deixa a pontuação previsível e testável.

| Função | O que faz |
| --- | --- |
| `buscar_similares(artista)` | Pede ao Last.fm artistas parecidos. |
| `montar_candidatos(artistas)` | Junta os similares, sem repetir e sem incluir os artistas do usuário. |
| `buscar_tags(artista)` | Devolve as 4 tags mais fortes de um artista. |
| `contar_tags_em_comum(artistas_usuario, candidato)` | Soma os pontos de um candidato pelas tags em comum. |
| `escolher_candidato(artistas_usuario, candidatos)` | Escolhe o candidato com mais pontos. |
| `buscar_sobre(artista)` | Devolve o resumo da biografia. |
| `buscar_albuns(artista)` | Devolve os álbuns mais populares. |
| `buscar_tags_album(artista, album)` | Devolve as tags de um álbum. |
| `ordenar_albuns(artista, tags_clima)` | Ordena os álbuns pela afinidade com o clima. |
| `interpretar_atmosfera(frase)` | Pede ao Gemini as tags que representam o clima. |
| `normalizar(nome)` | Padroniza nomes (minúsculas e sem acento) para comparação. |
| `confirmar(pergunta)` | Pergunta sim/não e repete até receber uma resposta válida. |

As funções `buscar_*` apenas consultam APIs. As funções que usam `print` e `input` cuidam só da conversa no terminal. Essa separação permite que a mesma lógica seja usada pelo terminal e pela API.

## API (FastAPI)

O servidor reaproveita as funções do `main.py`. A API não guarda estado entre pedidos: quem controla a conversa (por exemplo, quais artistas já foram recusados) é quem chama.

| Endereço | O que faz |
| --- | --- |
| `GET /` | Confirma que a API está no ar. |
| `GET /artista/{nome}` | Devolve o resumo da biografia de um artista. |
| `POST /sugestao` | Recebe os três artistas (e os recusados) e devolve o melhor candidato com o resumo. |
| `POST /albuns` | Recebe o artista aceito e a frase do clima, e devolve a lista de álbuns ordenada. |

Exemplo de corpo para `POST /sugestao`:

```json
{
  "artistas": ["FKA twigs", "Björk", "Sevdaliza"],
  "recusados": []
}
```

Exemplo de corpo para `POST /albuns`:

```json
{
  "artista": "Arca",
  "frase": "algo pra dia de chuva"
}
```

Erros comuns viram respostas legíveis: `404` quando o Last.fm não conhece um artista e `502` quando o Last.fm não responde.

A documentação interativa fica em `http://127.0.0.1:8000/docs`, e permite testar todos os endereços sem precisar de um front-end.

## Tecnologias

- Python 3.11 ou superior
- [`requests`](https://pypi.org/project/requests/) para chamar o Last.fm
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) para ler as chaves do arquivo `.env`
- [`google-genai`](https://pypi.org/project/google-genai/) para o Gemini
- [`FastAPI`](https://fastapi.tiangolo.com/) e [`uvicorn`](https://www.uvicorn.org/) para a API
- API do Last.fm

## Como rodar

### 1. Clone o repositório

```bash
git clone https://github.com/SEU-USUARIO/music-discovery-agent.git
cd music-discovery-agent
```

### 2. Crie e ative o ambiente virtual

**Windows (PowerShell):**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

**Mac / Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as chaves de API

Você precisa de duas chaves gratuitas:

1. **Last.fm:** crie uma conta e gere uma chave em <https://www.last.fm/api/account/create>.
2. **Gemini:** gere uma chave no [Google AI Studio](https://aistudio.google.com/).

Copie o arquivo de exemplo e preencha com as suas chaves:

```bash
cp .env.example .env
```

No Windows, basta copiar o arquivo `.env.example` e renomear a cópia para `.env`. O conteúdo deve ser:

```
LASTFM_API_KEY=sua_chave_aqui
GEMINI_API_KEY=sua_chave_aqui
```

Sem aspas e sem espaços ao redor do `=`. O arquivo `.env` está no `.gitignore` e **nunca deve ser enviado ao GitHub**.

### 5. Execute

**No terminal:**

```bash
python main.py
```

**Como API:**

```bash
uvicorn api:app --reload
```

Depois abra `http://127.0.0.1:8000/docs`.

## Limitações conhecidas

- **Plano gratuito do Gemini:** os modelos às vezes respondem com erro de demanda (503). Nesse caso o programa avisa e segue sem o clima, e os álbuns ficam na ordem de popularidade.
- **Vocabulário das tags:** o modelo e o Last.fm podem usar palavras diferentes para a mesma ideia (`melancholic` e `melancholy`), e a comparação é por texto exato. Álbuns menos conhecidos também têm poucas tags.
- **Qualidade dos dados:** tags e biografias do Last.fm são editáveis pela comunidade. O programa usa apenas as tags mais fortes para reduzir o ruído, mas os dados não são oficiais.
- **Velocidade:** cada sugestão faz várias chamadas ao Last.fm, ainda sem cache.
- **Terminal:** artista inexistente ou falha de rede ainda encerram o programa de terminal com uma exceção. A API já trata esses casos.
- **Idioma:** as biografias costumam vir em inglês.

## Roadmap

- [x] Fluxo de conversa no terminal com validação de entradas
- [x] Integração com o Last.fm (similares, tags, biografia, álbuns)
- [x] Sugestão de artista por similaridade de tags
- [x] Interpretação do clima com LLM (Gemini)
- [x] Escolha do álbum pelo clima
- [x] API com FastAPI

## Estrutura do projeto

```
music-discovery-agent/
├── main.py            # lógica de recomendação e versão de terminal
├── api.py             # API FastAPI (usa as funções do main.py)
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Créditos

Dados fornecidos pela [API do Last.fm](https://www.last.fm/api). Interpretação de linguagem natural pelo [Google Gemini](https://ai.google.dev/). Este projeto não é afiliado ao Last.fm nem ao Google.
