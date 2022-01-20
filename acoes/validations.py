from .models import Carteira


def valida_acao_existe_carteira(acao, usuario, campos_com_erro):
    """ Valida ação em carteira """
    try:
        Carteira.objects.get(
            acao=acao, user=usuario
        )
    except Carteira.DoesNotExist:
        campos_com_erro['acao'] = "Não existe a ação em carteira para venda!"

def valida_quantidade_carteira(acao, usuario, quantidade, campos_com_erro):
    try:
        carteira = Carteira.objects.get(
            acao=acao, user=usuario
        )
        if quantidade > carteira.quantidade:
            campos_com_erro['quantidade'] = (
                "Quantidade em carteira e menor que a de venda!"
            )
    except:
        pass