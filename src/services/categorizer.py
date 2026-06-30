import re

KEYWORDS = {
    "alimentação": ["mercado", "supermercado", "feira", "padaria", "açougue", "verduras", "hortifruti", "marmita", "quentinha"],
    "transporte": ["ônibus", "metro", "metrô", "uber", "99", "gasolina", "combustível", "passagem", "pedágio", "estacionamento"],
    "moradia": ["aluguel", "condomínio", "água", "luz", "energia", "iptu", "gás", "contabilidade"],
    "lazer": ["cinema", "bar", "restaurante", "ifood", "shopping", "hotel", "passeio", "parque"],
    "saúde": ["farmácia", "médico", "dentista", "plano de saúde", "exame", "consulta", "hospital", "remédio"],
    "educação": ["curso", "faculdade", "escola", "livro", "mensalidade", "matrícula", "professor"],
    "assinaturas": ["netflix", "spotify", "streaming", "prime video", "disney", "hbo", "apple tv"],
    "compras": ["roupa", "calçado", "eletrônico", "celular", "presente"],
    "restaurante": ["lanche", "pizza", "hambúrguer", "sushi"],
}


def categorizar(descricao: str) -> str:
    desc = descricao.lower().strip()
    if not desc:
        return "outros"
    for categoria, palavras in KEYWORDS.items():
        for palavra in palavras:
            if re.search(rf"\b{re.escape(palavra)}\b", desc):
                return categoria
    return "outros"
