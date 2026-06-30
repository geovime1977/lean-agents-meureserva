SALARIO_MINIMO = 1621.00

CATEGORIAS_NECESSIDADES = {
    "alimentação": 0.20,
    "moradia": 0.12,
    "transporte": 0.08,
    "saúde": 0.05,
    "educação": 0.05,
}

CATEGORIAS_DESEJOS = {
    "lazer": 0.10,
    "restaurante": 0.06,
    "compras": 0.06,
    "assinaturas": 0.04,
    "viagem": 0.04,
}


def calcular_orcamento(renda_mensal):
    if renda_mensal <= 0:
        renda_mensal = SALARIO_MINIMO
    return {
        "necessidades": round(renda_mensal * 0.50, 2),
        "desejos": round(renda_mensal * 0.30, 2),
        "poupanca": round(renda_mensal * 0.20, 2),
    }


def sugestao_por_categoria(renda_mensal):
    if renda_mensal <= 0:
        renda_mensal = SALARIO_MINIMO
    orcamento = calcular_orcamento(renda_mensal)
    sugestoes = {}
    for cat, pct in CATEGORIAS_NECESSIDADES.items():
        sugestoes[cat] = round(orcamento["necessidades"] * pct / 0.50, 2)
    for cat, pct in CATEGORIAS_DESEJOS.items():
        sugestoes[cat] = round(orcamento["desejos"] * pct / 0.30, 2)
    sugestoes["poupança"] = round(orcamento["poupanca"], 2)
    return sugestoes


def categorias_necessidades_list():
    return list(CATEGORIAS_NECESSIDADES.keys())


def categorias_desejos_list():
    return list(CATEGORIAS_DESEJOS.keys())


def todas_categorias():
    return categorias_necessidades_list() + categorias_desejos_list() + ["poupança", "outros"]
