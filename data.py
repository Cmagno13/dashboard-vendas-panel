"""Geração de dados sintéticos de vendas (determinística, roda offline).

Não depende de nenhum arquivo externo: os números são gerados com uma semente
fixa, então o dashboard mostra sempre o mesmo cenário — ideal para portfólio e
para testes reproduzíveis.
"""

from __future__ import annotations

from functools import lru_cache

import numpy as np
import pandas as pd

REGIOES = ["Sudeste", "Sul", "Nordeste", "Norte", "Centro-Oeste"]

# Peso relativo de cada região (o Sudeste concentra mais vendas).
PESO_REGIAO = {
    "Sudeste": 1.6,
    "Sul": 1.1,
    "Nordeste": 0.9,
    "Norte": 0.5,
    "Centro-Oeste": 0.7,
}

# Categoria -> (preço médio, margem média, lista de produtos)
CATEGORIAS = {
    "Eletrônicos": (1800.0, 0.22, ["Smartphone", "Notebook", "Fone de Ouvido", "Smart TV"]),
    "Vestuário": (150.0, 0.45, ["Camiseta", "Calça Jeans", "Tênis", "Jaqueta"]),
    "Alimentos": (35.0, 0.30, ["Café", "Chocolate", "Azeite", "Cesta Básica"]),
    "Casa": (400.0, 0.38, ["Cafeteira", "Jogo de Panelas", "Luminária", "Aspirador"]),
    "Esporte": (260.0, 0.40, ["Bicicleta", "Halteres", "Bola", "Esteira"]),
}


@lru_cache(maxsize=1)
def gerar_vendas(seed: int = 42) -> pd.DataFrame:
    """Gera uma tabela de vendas diárias por região, categoria e produto.

    Retorna um DataFrame com uma linha por (dia, região, categoria), já com
    receita, custo e margem calculados. ~2 anos de histórico.
    """
    rng = np.random.default_rng(seed)

    datas = pd.date_range("2023-01-01", "2024-12-31", freq="D")
    dia_do_ano = datas.dayofyear.to_numpy()
    # Sazonalidade anual (pico no fim de ano) + leve tendência de crescimento.
    sazonal = 1.0 + 0.30 * np.sin((dia_do_ano / 365.0) * 2 * np.pi - 1.3)
    tendencia = np.linspace(1.0, 1.25, len(datas))

    linhas = []
    for i, data in enumerate(datas):
        fim_de_semana = 1.15 if data.weekday() >= 5 else 1.0
        for regiao in REGIOES:
            peso_r = PESO_REGIAO[regiao]
            for categoria, (preco_base, margem_base, produtos) in CATEGORIAS.items():
                # Volume de pedidos do dia para essa combinação.
                base = 6.0 * peso_r * sazonal[i] * tendencia[i] * fim_de_semana
                pedidos = int(max(0, rng.poisson(base)))
                if pedidos == 0:
                    continue
                produto = produtos[rng.integers(len(produtos))]
                # Preço com um pouco de variação; unidades por pedido.
                preco = preco_base * rng.normal(1.0, 0.06)
                unidades = int(pedidos * rng.integers(1, 4))
                receita = unidades * preco
                margem = np.clip(rng.normal(margem_base, 0.05), 0.05, 0.85)
                custo = receita * (1 - margem)
                linhas.append(
                    (data, regiao, categoria, produto, pedidos, unidades, receita, custo)
                )

    df = pd.DataFrame(
        linhas,
        columns=[
            "data", "regiao", "categoria", "produto",
            "pedidos", "unidades", "receita", "custo",
        ],
    )
    df["lucro"] = df["receita"] - df["custo"]
    df["mes"] = df["data"].dt.to_period("M").dt.to_timestamp()
    return df


if __name__ == "__main__":
    d = gerar_vendas()
    print(d.head())
    print(f"\nlinhas: {len(d):,} | período: {d['data'].min().date()} → {d['data'].max().date()}")
    print(f"receita total: R$ {d['receita'].sum():,.0f}")
