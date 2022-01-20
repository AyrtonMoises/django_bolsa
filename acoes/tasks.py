from celery import shared_task
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import (
    NoSuchElementException, WebDriverException
)
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary

from acoes.models import Acao
from setup.settings import PATH_DRIVER_FIREFOX, PATH_BINARY_FIREFOX


@shared_task(bind=True, max_retries=3)
def task_scrap_acoes_dia_anterior(self):
    """ Busca ações cadastradas e atualiza seu preço """
    options = Options()
    options.headless = True
    binary = FirefoxBinary(PATH_BINARY_FIREFOX)

    driver = webdriver.Firefox(
        firefox_binary=binary,
        executable_path=PATH_DRIVER_FIREFOX,
        options=options
    )

    acoes = Acao.objects.all()

    feedback = {}
    for acao in acoes:
        try:
            driver.get(
                f"https://www.fundamentus.com.br/detalhes.php?papel={acao}"
            )
            row = driver.find_element(
                By.XPATH,
                "//table[@class='w728']/tbody/tr//td[@class='data destaque w3']/span"
            )
            valor_acao = row.text
            
            # Trata e salva novo valor
            valor_tratado = valor_acao.replace(',','.')
            acao.preco = valor_tratado
            acao.save()
            mensagem = f"atualizada para: {valor_tratado}"
            feedback[acao.ticker]= mensagem
        except NoSuchElementException:
            mensagem = f"Elemento não encontrado para ação"
            feedback[acao.ticker]= mensagem
        except WebDriverException as e:
            self.retry(exc=e, countdown=15)
            return 'Erro ao acessar a página'
    driver.quit()
            
    return feedback

