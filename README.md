# ppgcs

Dados estruturados do **corpo docente permanente** do Programa de Pós-Graduação em Ciências Sociais da UFBA (PPGCS/UFBA), extraídos dos currículos Lattes via [scriptLattes](https://github.com/jpmenachalco/scriptLattes).

- **Fonte da lista**: https://ppgcs.ufba.br/pt-br/corpo-docente
- **Data da coleta**: 2026-05-22
- **Período coberto**: histórico completo (1900–2026)
- **Docentes**: 23 permanentes

## Estrutura

```
data/
├── docentes_ppgcs.csv     Lista mestra: nome, id_lattes_16, url, vínculo, fonte_id
├── json/                  23 JSONs estruturados (um por docente)
├── relatorio/             Relatório HTML do scriptLattes (índice, páginas individuais, grafo)
└── cache/                 Snapshot bruto dos HTMLs Lattes baixados
```

## Conteúdo de cada JSON (`data/json/`)

Cada arquivo segue o padrão `<ordem>_<Nome-Hifenado>_<id_lattes>.json` e contém:

| Seção | Conteúdo |
|---|---|
| `informacoes_pessoais` | Nome, endereço, links pessoais |
| `formacao_academica` | Graduação, mestrado, doutorado, pós-doc |
| `atuacao_profissional` | Vínculos institucionais e atividades |
| `projetos_pesquisa`, `projetos_extensao`, `projetos_desenvolvimento` | Projetos com período, descrição e equipe |
| `areas_de_atuacao`, `linhas_de_pesquisa` | Grande área → especialidade |
| `idiomas` | Línguas e proficiência |
| `premios_titulos` | Distinções recebidas |
| `producao_bibliografica` | Artigos, livros, capítulos, trabalhos em eventos |
| `producao_tecnica`, `patentes_registros`, `producao_artistica` | Outras produções |
| `orientacoes` | Mestrado, doutorado, pós-doc, IC, TCC (em andamento e concluídas) |
| `eventos`, `bancas` | Participação e organização |
| `estatisticas` | Contadores por tipo |

## Como reprocessar

```bash
git clone https://github.com/jpmenachalco/scriptLattes.git
cd scriptLattes
make install
# copiar data/docentes_ppgcs.csv → gerar .list no formato: <id>\t,\t<nome>
python3 scriptLattes.py seu.config
```

## Docentes

Lista completa em [`data/docentes_ppgcs.csv`](data/docentes_ppgcs.csv).

## Licença

Os dados são públicos (Plataforma Lattes/CNPq). Este compilado é disponibilizado pelo LABHDUFBA para fins de pesquisa.
