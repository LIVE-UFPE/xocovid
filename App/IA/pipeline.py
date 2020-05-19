import App.IA.casesbydayBR as casesbydayBR
import App.IA.interpolacao as interpolacao
import App.IA.predicao as predicao


def main():
    print("Inicio do pipeline (interpolação)")
    casesbydayBR.main()
    interpolacao.main()
    predicao.main()
