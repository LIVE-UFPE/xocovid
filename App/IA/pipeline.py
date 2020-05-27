import casesbydayBR
import interpolacao
import predicao


def main():
    print("Inicio do pipeline (interpolação)")
    casesbydayBR.main()
    interpolacao.main()
    predicao.main()

main()
