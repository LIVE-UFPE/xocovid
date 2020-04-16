import App.IA.pre_processing as pre_processing
import App.IA.casesbyday as casesbyday
import App.IA.interpolacao as interpolacao
import App.IA.predicao as predicao


def main():
    print("Inicio do pipeline")
    pre_processing.main()
    casesbyday.main()
    interpolacao.main()
    predicao.main()