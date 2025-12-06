"""
gantt_routes.py
----------------
Módulo responsável pela geração da visualização do gráfico Gantt contendo:

- Períodos de férias
- Folgas por assiduidade
- Feriados nacionais, estaduais e municipais
- Realce de finais de semana
- Suporte a tema claro e escuro
- Sistema de filtros por funcionário, mês e ano

Este módulo utiliza Plotly para renderização do gráfico e integra dados vindos dos
serviços `ferias_service.py` e `folga_service.py`.
"""

from flask import Blueprint, render_template, request
from services.ferias_service import listar_periodos_para_gantt
from services.folga_service import listar_folgas
import plotly.express as px
import plotly.graph_objects as go
import datetime as dt
import holidays

gantt_bp = Blueprint("gantt", __name__)


# ============================================================================
# FUNÇÃO PARA OBTER LISTA COMPLETA DE FERIADOS
# ============================================================================
def obter_feriados():
    """
    Retorna um dicionário contendo todos os feriados relevantes para o gráfico.

    Inclui:
    - Feriados nacionais e estaduais usando a biblioteca `holidays`.
    - Feriados municipais fixos (ex.: Aniversário de Osasco).
    - Feriados móveis: Carnaval, Corpus Christi, e outros suportados pela lib.

    Formato do retorno:
        {
            "YYYY-MM-DD": "Nome do feriado",
            ...
        }

    Returns:
        dict: chave = data no formato YYYY-MM-DD, valor = nome do feriado
    """

    ano_atual = dt.datetime.now().year
    ano_prox = ano_atual + 1

    # Feriados nacionais + estaduais
    feriados = holidays.Brazil(
        years=[ano_atual, ano_prox],
        state="SP",
        language="pt_BR"
    )

    resultado = {}

    # ---------------- FERIADO MUNICIPAL ----------------
    resultado[f"{ano_atual}-02-19"] = "Aniversário de Osasco"
    resultado[f"{ano_prox}-02-19"] = "Aniversário de Osasco"

    # ---------------- FERIADOS MÓVEIS ----------------
    for ano in [ano_atual, ano_prox]:
        # Carnaval
        try:
            datas = holidays.Brazil(years=[ano]).get_named("Carnaval")
            if datas:
                resultado[datas[0].strftime("%Y-%m-%d")] = "Carnaval"
        except:
            pass

        # Corpus Christi
        try:
            datas = holidays.Brazil(years=[ano]).get_named("Corpus Christi")
            if datas:
                resultado[datas[0].strftime("%Y-%m-%d")] = "Corpus Christi"
        except:
            pass

        # Santo Antônio (fixo)
        resultado[f"{ano}-06-13"] = "Santo Antônio"

    # ---------------- FERIADOS PADRÃO ----------------
    for data, nome in feriados.items():
        if isinstance(data, dt.date):
            resultado[data.strftime("%Y-%m-%d")] = nome

    return resultado


# ============================================================================
# ROTA DO GRÁFICO GANTT
# ============================================================================
@gantt_bp.route("/gantt")
def pagina_gantt():
    """
    Gera e exibe o gráfico de Gantt com todos os períodos de férias, folgas,
    feriados e finais de semana.

    Funcionalidades suportadas:
    - Tema claro/escuro (parâmetro GET: theme=dark)
    - Filtros:
        funcionário
        mês
        ano
    - Feriados marcados com linha vermelha
    - Finais de semana sombreado automaticamente
    - Legendas personalizadas

    Renderiza o template `gantt.html` contendo:
    - O gráfico gerado como HTML
    - Lista de feriados ordenados
    - Lista de funcionários únicos para o filtro
    """

    # =====================================================
    # DETECTAR TEMA (LIGHT / DARK)
    # =====================================================
    theme = request.args.get("theme", "light")

    if theme == "dark":
        paper_bg = "#121212"
        plot_bg = "#1a1a1a"
        text_color = "#e0e0e0"
        grid_color = "#333"
        weekend_color = "rgba(255,255,255,0.05)"
        legend_bg = "rgba(0,0,0,0)"
        hover_bg = "#333"
        hover_text = "white"
    else:
        paper_bg = "white"
        plot_bg = "white"
        text_color = "#222"
        grid_color = "#ccc"
        weekend_color = "rgba(0,0,0,0.05)"
        legend_bg = "white"
        hover_bg = "#eee"
        hover_text = "black"

    # =====================================================
    # CAPTURA DOS FILTROS RECEBIDOS VIA GET
    # =====================================================
    funcionario_filtro = request.args.get("funcionario")
    mes_filtro = request.args.get("mes")
    ano_filtro = request.args.get("ano")

    # Dados vindos do banco
    dados = listar_periodos_para_gantt()   # férias
    folgas = listar_folgas()               # folgas
    feriados = obter_feriados()            # feriados

    # Função auxiliar para validar filtros
    def dentro_do_filtro(inicio, fim):
        dt_inicio = dt.datetime.strptime(inicio, "%Y-%m-%d")
        dt_fim = dt.datetime.strptime(fim, "%Y-%m-%d")

        # Filtro por ano
        if ano_filtro and dt_inicio.year != int(ano_filtro) and dt_fim.year != int(ano_filtro):
            return False

        # Filtro por mês
        if mes_filtro and dt_inicio.month != int(mes_filtro) and dt_fim.month != int(mes_filtro):
            return False

        return True

    # ---------------- FILTRAR FÉRIAS ----------------
    if funcionario_filtro:
        dados = [d for d in dados if d[0] == funcionario_filtro]

    dados = [d for d in dados if dentro_do_filtro(d[1], d[2])]

    # ---------------- FILTRAR FOLGAS ----------------
    if funcionario_filtro:
        folgas = [f for f in folgas if f["nome"] == funcionario_filtro]

    folgas = [
        f for f in folgas
        if dentro_do_filtro(f["data_folga"], f["data_folga"])
    ]

    # ---------------- LISTA ÚNICA DE FUNCIONÁRIOS ----------------
    funcionarios_unicos = sorted({d[0] for d in listar_periodos_para_gantt()})

    # =====================================================
    # GERAR LISTA DE TAREFAS (FÉRIAS + FOLGAS)
    # =====================================================
    tasks = []

    # Férias
    for nome, inicio, fim in dados:
        tasks.append({
            "Funcionário": nome,
            "Inicio": inicio,
            "Fim": fim,
            "Tipo": "Férias"
        })

    # Folgas
    for f in folgas:
        nome = f["nome"]
        d = f["data_folga"]

        dt_inicio = dt.datetime.strptime(d, "%Y-%m-%d")
        dt_fim = dt_inicio + dt.timedelta(days=1)

        tasks.append({
            "Funcionário": nome,
            "Inicio": dt_inicio.strftime("%Y-%m-%d"),
            "Fim": dt_fim.strftime("%Y-%m-%d"),
            "Tipo": "Folga"
        })

    # Caso não existam resultados com os filtros aplicados
    if not tasks:
        return render_template(
            "gantt.html",
            grafico_html="<h3>Sem dados com esses filtros</h3>",
            feriados={},
            funcionarios=funcionarios_unicos
        )

    # =====================================================
    # GERAÇÃO DO GRÁFICO COM PLOTLY
    # =====================================================
    fig = px.timeline(
        tasks,
        x_start="Inicio",
        x_end="Fim",
        color="Tipo",
        color_discrete_map={
            "Férias": "#1e88e5",
            "Folga": "#ffa726"
        },
        y="Funcionário"
    )

    fig.update_yaxes(autorange="reversed", tickfont=dict(size=18))

    shapes = []

    # ---------------- FERIADOS (LINHAS VERMELHAS) ----------------
    for data, nome in feriados.items():
        dt_data = dt.datetime.strptime(data, "%Y-%m-%d")

        shapes.append(dict(
            type="line",
            x0=dt_data, x1=dt_data,
            y0=-0.5, y1=len(tasks) - 0.5,
            line=dict(color="red", width=2, dash="dot"),
            xref="x", yref="y"
        ))

    # ---------------- FINAIS DE SEMANA ----------------
    ano = dt.datetime.now().year
    inicio = dt.datetime(ano, 1, 1)
    fim = dt.datetime(ano + 1, 12, 31)

    for i in range((fim - inicio).days):
        dia = inicio + dt.timedelta(days=i)
        if dia.weekday() in (5, 6):  # sábado ou domingo
            shapes.append(dict(
                type="rect",
                x0=dia, x1=dia + dt.timedelta(days=1),
                y0=-0.5, y1=len(tasks) - 0.5,
                fillcolor=weekend_color,
                line=dict(width=0),
                layer="below"
            ))

    # =====================================================
    # LAYOUT E ESTILO (Tema Dinâmico)
    # =====================================================
    fig.update_layout(
        shapes=shapes,
        paper_bgcolor=paper_bg,
        plot_bgcolor=plot_bg,
        font=dict(color=text_color),

        xaxis=dict(
            showgrid=True,
            gridcolor=grid_color,
            zeroline=False,
            tickfont=dict(color=text_color),
            linecolor=grid_color
        ),

        yaxis=dict(
            showgrid=False,
            tickfont=dict(color=text_color)
        ),

        legend=dict(
            bgcolor=legend_bg,
            font=dict(color=text_color)
        ),

        hoverlabel=dict(
            bgcolor=hover_bg,
            font_size=14,
            font_color=hover_text
        )
    )

    # ------- LEGENDA EXTRA (Feriado e Final de Semana) -------
    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="lines",
        line=dict(color="red", width=2, dash="dot"),
        name="Feriados"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None], mode="markers",
        marker=dict(size=15, color="rgba(200,200,200,0.6)"),
        name="Sábados e Domingos"
    ))

    grafico_html = fig.to_html(full_html=False)

    # =====================================================
    # FERIADOS ORDENADOS PARA APRESENTAÇÃO NA TELA
    # =====================================================
    ano_lista = ano_filtro if ano_filtro else dt.datetime.now().year

    feriados_filtrados = {
        data: nome for data, nome in feriados.items()
        if data.startswith(str(ano_lista))
    }

    feriados_ordenados = dict(sorted(
        feriados_filtrados.items(),
        key=lambda x: (int(x[0][5:7]), int(x[0][8:10]))
    ))

    return render_template(
        "gantt.html",
        grafico_html=grafico_html,
        feriados=feriados_ordenados,
        funcionarios=funcionarios_unicos
    )
