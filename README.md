# Music Discovery Agent.V1

Agente de descoberta musical que roda no terminal. Você informa três artistas, e o programa sugere um artista parecido e um álbum para ouvir, usando dados reais do [Last.fm](https://www.last.fm/api).

> **Status:** em desenvolvimento. É um projeto de estudo para aprender Python na prática e, depois, integração com IA (LLMs). A versão atual **ainda não usa IA**: a recomendação é feita com regras em Python puro sobre os dados do Last.fm.

## O que ele faz hoje

1. Pede três artistas ao usuário (com validação de campo vazio).
2. Busca artistas parecidos com cada um deles (`artist.getSimilar`).
3. Remove da lista de candidatos os artistas que o usuário já citou.
4. Dá uma pontuação a cada candidato, contando quantas **tags** ele tem em comum com os três artistas (`artist.getTopTags`).
5. Sugere o candidato com a maior pontuação, junto com um resumo da biografia (`artist.getInfo`).
6. Se o usuário recusar, sugere o próximo melhor, até alguém ser aceito ou a lista acabar.
7. Depois de aceito, sugere os álbuns do artista por popularidade (`artist.getTopAlbums`), um de cada vez, com a opção de pedir outro.

### Exemplo de uso

```
Digite o 1º artista: ...
Digite o 2º artista: ...
Digite o 3º artista: ...

Artistas selecionados:
1. ...
2. ...
3. ...

Artista sugerido: <nome>
Sobre: <resumo da biografia no Last.fm>

Deseja ouvir <nome>? (sim/não): sim
Gerando sugestão...

Álbum sugerido: <álbum mais popular>

Deseja ouvir este álbum? (sim/não):
```

<!-- Adicione aqui um print ou GIF do programa rodando. -->

## Como funciona a recomendação

A lógica está separada em funções, cada uma com uma responsabilidade:

| Função | O que faz |
| --- | --- |
| `buscar_similares(artista)` | Pede ao Last.fm artistas parecidos (gera os candidatos). |
| `buscar_tags(artista)` | Devolve as 4 tags mais fortes de um artista. |
| `contar_tags_em_comum(artistas_usuario, candidato)` | Soma os pontos de um candidato pelas tags em comum. |
| `escolher_candidato(artistas_usuario, candidatos)` | Escolhe o candidato com mais pontos. |
| `buscar_sobre(artista)` | Devolve o resumo da biografia. |
| `buscar_albuns(artista)` | Devolve os álbuns mais populares. |
| `confirmar(pergunta)` | Pergunta sim/não e repete até receber uma resposta válida. |

As funções `buscar_*` apenas consultam a API. As funções que usam `print` e `input` cuidam só da conversa. Essa separação foi pensada para que a lógica possa ser reaproveitada depois, por uma API e um front-end.

## Tecnologias

- Python 3.11 ou superior
- [`requests`](https://pypi.org/project/requests/) para chamar a API
- [`python-dotenv`](https://pypi.org/project/python-dotenv/) para ler a chave do arquivo `.env`
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

### 4. Configure a chave da API

1. Crie uma conta no Last.fm e gere uma API key em <https://www.last.fm/api/account/create>.
2. Copie o arquivo de exemplo e preencha com a sua chave:

```bash
cp .env.example .env
```

No Windows, basta copiar o arquivo `.env.example` e renomear a cópia para `.env`. O conteúdo deve ser:

```
LASTFM_API_KEY=sua_chave_aqui
```

Sem aspas e sem espaços ao redor do `=`. O arquivo `.env` está no `.gitignore` e **nunca deve ser enviado ao GitHub**.

### 5. Execute

```bash
python main.py
```

## Roadmap

- [ ] Integração com um LLM (interpretação de linguagem natural e justificativas)
- [ ] API com FastAPI
- [ ] Front-end em Angular

## Estrutura do projeto

```
music-discovery-agent/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Créditos

Dados fornecidos pela [API do Last.fm](https://www.last.fm/api). Este projeto não é afiliado ao Last.fm.
