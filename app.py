"""Dashboard Interativo de Vendas com HoloViz Panel.

Executar localmente:
    panel serve app.py --show --autoreload

Estrutura:
  - barra lateral com filtros (período, região, categoria) — reativos;
  - KPIs (receita, lucro, pedidos, ticket médio);
  - gráficos Plotly: receita mensal, por categoria, por região e top produtos.

Os dados são sintéticos e determinísticos (ver data.py), então roda offline.
"""

from __future__ import annotations

import pandas as pd
import panel as pn
import plotly.express as px
import plotly.graph_objects as go

from data import CATEGORIAS, REGIOES, gerar_vendas

pn.extension("plotly", sizing_mode="stretch_width")

ACCENT = "#2563eb"
PLOT_TEMPLATE = "plotly_white"

DF = gerar_vendas()

# ---------------------------------------------------------------------------
# Filtros (widgets)
# ---------------------------------------------------------------------------
filtro_periodo = pn.widgets.DateRangeSlider(
    name="Período",
    start=DF["data"].min(),
    end=DF["data"].max(),
    value=(DF["data"].min(), DF["data"].max()),
)
filtro_regiao = pn.widgets.MultiChoice(
    name="Região", options=REGIOES, value=list(REGIOES),
)
filtro_categoria = pn.widgets.MultiChoice(
    name="Categoria", options=list(CATEGORIAS), value=list(CATEGORIAS),
)


def _filtrar(periodo, regioes, categorias) -> pd.DataFrame:
    """Aplica os filtros selecionados e devolve o subconjunto do DataFrame."""
    ini, fim = periodo
    regioes = regioes or list(REGIOES)
    categorias = categorias or list(CATEGORIAS)
    m = (
        (DF["data"] >= pd.Timestamp(ini))
        & (DF["data"] <= pd.Timestamp(fim))
        & (DF["regiao"].isin(regioes))
        & (DF["categoria"].isin(categorias))
    )
    return DF.loc[m]


def _fig_vazia(msg: str = "Sem dados para os filtros selecionados") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(text=msg, showarrow=False, font=dict(size=14, color="#888"))
    fig.update_layout(template=PLOT_TEMPLATE, height=320,
                      xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


# ---------------------------------------------------------------------------
# KPIs
# ---------------------------------------------------------------------------
def kpis(periodo, regioes, categorias):
    d = _filtrar(periodo, regioes, categorias)
    receita = float(d["receita"].sum())
    lucro = float(d["lucro"].sum())
    pedidos = int(d["pedidos"].sum())
    margem = (lucro / receita * 100) if receita else 0.0
    ticket = (receita / pedidos) if pedidos else 0.0

    def card(titulo, valor, sub):
        return pn.pane.HTML(
            f"""
            <div style="background:#fff;border:1px solid #e5e7eb;border-radius:14px;
                        padding:1rem 1.2rem;box-shadow:0 1px 2px rgba(0,0,0,.04);">
              <div style="color:#6b7280;font-size:.8rem;text-transform:uppercase;
                          letter-spacing:.04em;">{titulo}</div>
              <div style="color:#111827;font-size:1.7rem;font-weight:700;
                          margin-top:.25rem;">{valor}</div>
              <div style="color:#2563eb;font-size:.8rem;margin-top:.15rem;">{sub}</div>
            </div>
            """,
            sizing_mode="stretch_width",
        )

    return pn.FlexBox(
        card("Receita", f"R$ {receita:,.0f}".replace(",", "."), "no período filtrado"),
        card("Lucro", f"R$ {lucro:,.0f}".replace(",", "."), f"margem {margem:.1f}%"),
        card("Pedidos", f"{pedidos:,}".replace(",", "."), "total de pedidos"),
        card("Ticket médio", f"R$ {ticket:,.0f}".replace(",", "."), "receita / pedido"),
        flex_direction="row", gap="1rem",
    )


# ---------------------------------------------------------------------------
# Gráficos
# ---------------------------------------------------------------------------
def fig_receita_mensal(periodo, regioes, categorias):
    d = _filtrar(periodo, regioes, categorias)
    if d.empty:
        return pn.pane.Plotly(_fig_vazia())
    g = d.groupby("mes", as_index=False)["receita"].sum()
    fig = px.area(g, x="mes", y="receita", markers=True,
                  labels={"mes": "Mês", "receita": "Receita (R$)"})
    fig.update_traces(line_color=ACCENT, fillcolor="rgba(37,99,235,.12)")
    fig.update_layout(template=PLOT_TEMPLATE, height=320, margin=dict(l=10, r=10, t=30, b=10),
                      title="Receita mensal")
    return pn.pane.Plotly(fig, config={"displayModeBar": False})


def fig_por_categoria(periodo, regioes, categorias):
    d = _filtrar(periodo, regioes, categorias)
    if d.empty:
        return pn.pane.Plotly(_fig_vazia())
    g = d.groupby("categoria", as_index=False)["receita"].sum().sort_values("receita")
    fig = px.bar(g, x="receita", y="categoria", orientation="h",
                 labels={"receita": "Receita (R$)", "categoria": ""})
    fig.update_traces(marker_color=ACCENT)
    fig.update_layout(template=PLOT_TEMPLATE, height=320, margin=dict(l=10, r=10, t=30, b=10),
                      title="Receita por categoria")
    return pn.pane.Plotly(fig, config={"displayModeBar": False})


def fig_por_regiao(periodo, regioes, categorias):
    d = _filtrar(periodo, regioes, categorias)
    if d.empty:
        return pn.pane.Plotly(_fig_vazia())
    g = d.groupby("regiao", as_index=False)["receita"].sum()
    fig = px.pie(g, names="regiao", values="receita", hole=0.55)
    fig.update_layout(template=PLOT_TEMPLATE, height=320, margin=dict(l=10, r=10, t=30, b=10),
                      title="Participação por região")
    return pn.pane.Plotly(fig, config={"displayModeBar": False})


def fig_top_produtos(periodo, regioes, categorias):
    d = _filtrar(periodo, regioes, categorias)
    if d.empty:
        return pn.pane.Plotly(_fig_vazia())
    g = (d.groupby("produto", as_index=False)["receita"].sum()
         .sort_values("receita", ascending=False).head(10).sort_values("receita"))
    fig = px.bar(g, x="receita", y="produto", orientation="h",
                 labels={"receita": "Receita (R$)", "produto": ""})
    fig.update_traces(marker_color="#0ea5e9")
    fig.update_layout(template=PLOT_TEMPLATE, height=360, margin=dict(l=10, r=10, t=30, b=10),
                      title="Top 10 produtos")
    return pn.pane.Plotly(fig, config={"displayModeBar": False})


# ---------------------------------------------------------------------------
# Ligação reativa: cada saída depende dos 3 filtros
# ---------------------------------------------------------------------------
_dep = dict(periodo=filtro_periodo, regioes=filtro_regiao, categorias=filtro_categoria)

kpi_row = pn.bind(kpis, **_dep)
g_mensal = pn.bind(fig_receita_mensal, **_dep)
g_categoria = pn.bind(fig_por_categoria, **_dep)
g_regiao = pn.bind(fig_por_regiao, **_dep)
g_produtos = pn.bind(fig_top_produtos, **_dep)

# ---------------------------------------------------------------------------
# Layout (template)
# ---------------------------------------------------------------------------
template = pn.template.FastListTemplate(
    title="Dashboard de Vendas",
    header_background=ACCENT,
    accent_base_color=ACCENT,
    sidebar=[
        pn.pane.Markdown("### Filtros"),
        filtro_periodo,
        filtro_regiao,
        filtro_categoria,
        pn.pane.Markdown(
            "---\nDados **sintéticos** e determinísticos.\n\n"
            "Feito com [HoloViz Panel](https://panel.holoviz.org) + Plotly."
        ),
    ],
    main=[
        pn.Column(
            kpi_row,
            pn.Row(g_mensal, g_regiao),
            pn.Row(g_categoria, g_produtos),
            sizing_mode="stretch_width",
        )
    ],
)

template.servable()


if __name__ == "__main__":
    pn.serve(template, port=5006, show=True, autoreload=True)
