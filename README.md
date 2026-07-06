# 📊 Dashboard Interativo de Vendas — HoloViz Panel

> Aplicação de dados interativa construída com **HoloViz Panel** + **Plotly**, com
> filtros reativos, KPIs e visualizações de um cenário de vendas no varejo.

Um dashboard de BI feito 100% em Python: a barra lateral tem filtros de **período**,
**região** e **categoria**, e todos os indicadores e gráficos se atualizam
automaticamente conforme a seleção. Os dados são **sintéticos e determinísticos**
(gerados com semente fixa), então o projeto **roda offline**, sem precisar de banco
ou de arquivos externos.

---

## ✨ O que tem

- **KPIs reativos:** receita, lucro (com margem %), pedidos e ticket médio.
- **Gráficos interativos (Plotly):**
  - receita mensal (área temporal);
  - participação por região (rosca);
  - receita por categoria (barras);
  - top 10 produtos (barras).
- **Filtros na barra lateral:** período (slider de datas), região e categoria
  (múltipla escolha) — ligados de forma reativa com `pn.bind`.
- **Template profissional** `FastListTemplate`, responsivo.

---

## 🧰 Stack

| Camada | Tecnologia |
|---|---|
| App / UI | HoloViz Panel |
| Gráficos | Plotly Express |
| Dados | pandas + NumPy (sintéticos, determinísticos) |

---

## 🚀 Como executar

> Pré-requisito: Python 3.11+.

```bash
# 1. Ambiente e dependências
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 2. Servir o dashboard
panel serve app.py --show --autoreload
```

O navegador abre em `http://localhost:5006/app`.

### Com Docker

```bash
docker build -t dashboard-vendas-panel .
docker run --rm -p 5006:5006 dashboard-vendas-panel
# acesse http://localhost:5006/app
```

---

## 📁 Estrutura

```
dashboard-vendas-panel/
├── app.py            # dashboard Panel (filtros, KPIs, gráficos)
├── data.py           # geração de dados sintéticos determinísticos
├── requirements.txt
├── Dockerfile
├── .gitignore
├── LICENSE
└── README.md
```

---

## 🔍 Detalhe técnico

Os dados simulam ~2 anos de vendas diárias (2023–2024) em 5 regiões e 5 categorias,
com **sazonalidade** (pico no fim de ano), **tendência** de crescimento e peso maior
para o Sudeste — ~18 mil linhas, geradas em `data.py` com `numpy.random.default_rng`
e semente fixa. Trocar a semente gera outro cenário; manter a semente garante um
resultado reproduzível.

---

<p align="center">Feito por <b>Carlos Magno</b> — projeto de estudo em dataviz e BI.</p>
