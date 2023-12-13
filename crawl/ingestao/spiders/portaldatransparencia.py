import scrapy
import json
import re
import os
from requests.models import PreparedRequest
from unidecode import unidecode
from pathlib import Path


class PortaldatransparenciaSpider(scrapy.Spider):
    name = "portaldatransparencia"
    # allowed_domains = ["portaldatransparencia.gov.br"]

    def start_requests(self):

        base_url = "https://portaldatransparencia.gov.br/criterios/pessoa/autocomplete?"
        parameters = {
            'q': "positivo tecnologia"
        }
        req = PreparedRequest()
        req.prepare_url(base_url, parameters)
        mounted_url = req.url

        yield scrapy.Request(
            mounted_url
        )
    
    def parse(self, response):
        api_result = json.loads(response.text)
        positivo_ids = []

        for data in api_result:
            positivo_ids.append(data['id'])

        base_url = "https://portaldatransparencia.gov.br/despesas/favorecido/resultado?"

        parameters = {
            "paginacaoSimples":"false",
            "tamanhoPagina":"15",
            "offset":"0",
            "direcaoOrdenacao":"desc",
            "colunaOrdenacao":"valor",
            "colunasSelecionadas":"data,documentoResumido,localizadorGasto,fase,especie,favorecido,ufFavorecido,valor,ug,uo,orgao,orgaoSuperior,grupo,elemento,modalidade,planoOrcamentario,autor,subTitulo,funcao,subfuncao,programa,acao",
            "de":self.date,
            "ate":self.date,
            "favorecido": ','.join(positivo_ids),
            "faseDespesa":"2,1",
        }

        req = PreparedRequest()
        req.prepare_url(base_url, parameters)

        mounted_url = req.url
        
        yield scrapy.Request(
            mounted_url,
            callback=self.get_liquidacao_main_data
        )
    
    def get_liquidacao_main_data(self, response):
        api_result = json.loads(response.text)
        main_data = api_result['data']

        if not main_data:
            self.log('No data found!')

        metadata = {
            'type': 'pagamentos',
            'source': 'Portal da Transparencia - Governo Federal',
            'channel': 'crawl',
            'data': []
        }

        internal_urls = []
        
        for item in main_data:
            fase = unidecode(item['fase']).lower()
            internal_urls.append('https://portaldatransparencia.gov.br/despesas/'+fase+'/'+item['documento']+'?ordenarPor=fase&direcao=desc')
            
            data = {
                'date': item['data'],
                'documento': item['documento'],
                'documentoResumido': item['documentoResumido'],
                'observacao': item['observacao'],
                'funcao': item['funcao'],
                'subfuncao': item['subfuncao'],
                'programa': item['programa'],
                'acao': item['acao'],
                'subTitulo': item['subTitulo'],
                'localizadorGasto': item['localizadorGasto'],
                'fase': item['fase'],
                'especie': item['especie'],
                'favorecido': item['favorecido'],
                'codigoFavorecido': item['codigoFavorecido'],
                'nomeFavorecido': item['nomeFavorecido'],
                'ufFavorecido': item['ufFavorecido'],
                'valor': item['valor'],
                'ug': item['ug'],
                'uo': item['uo'],
                'orgao': item['orgao'],
                'orgaoSuperior': item['orgaoSuperior'],
                'categoria': item['categoria'],
                'grupo': item['grupo'],
                'elemento': item['elemento'],
                'modalidade': item['modalidade'],
                'numeroProcesso': item['numeroProcesso'],
                'planoOrcamentario': item['planoOrcamentario'],
                'autor': item['autor'],
                'favorecidoIntermediario': item['favorecidoIntermediario'],
                'favorecidoListaFaturas': item['favorecidoListaFaturas'],
            }

            metadata['data'].append(data)

            liquidacao_date = re.sub(r'[ \/]', '', self.date)
            root = str(Path(os.path.abspath(os.curdir)).parent.absolute())
            directory = root+'/datalake/raw_zone/licitacao/pagamentos/'
            filename = liquidacao_date+'_'+fase+'_pt_governo_federal.json'
            
            json_object = json.dumps(metadata, indent=4, ensure_ascii=False)

            if not os.path.isdir(directory):
                os.makedirs(directory)
                with open (directory+filename, 'w') as outfile:
                    outfile.write(json_object)

            elif not os.path.exists(directory+filename):
                with open (directory+filename, 'w') as outfile:
                    outfile.write(json_object)

            elif os.path.exists(directory+filename):
                exist_data = {}
                with open(directory+filename, 'r') as outfile:
                    exist_data = json.load(outfile)
            
                if exist_data:
                    exist_data['data'].append(data)

                    new_data = json.dumps(exist_data, indent=4, ensure_ascii=False)
            
                    with open (directory+filename, 'w') as outfile:
                        outfile.write(new_data)
            
        # for url in internal_urls:
            # yield scrapy.Request(
            #     base_url,
            #     meta={'playwright': True},
            #     callback=self.get_details
            # )
        
    def get_details(self, response):

        data = {}

        cache_file_name = re.sub(r'[ :.\/]', '_', response.url)

        cache_directory = str(Path(os.path.abspath(os.curdir)).parent.absolute())+'/datalake/cache/licitacao/crawled/'

        is_cache_dir = os.path.isdir(cache_directory)
        if not is_cache_dir:
            os.makedirs(directory)

        with open (cache_directory+cache_file_name+'.html', 'w') as outfile:
            outfile.write(response.text)

        container = response.xpath('//main/div[2]')

        rows_section1 = container.xpath('.//section[1]/div[contains(@class, "row")]')
        for row in rows_section1:
            for div in row.xpath('.//div'):
                generated_key = re.sub(r'[ \/]', '_', unidecode(div.xpath('.//strong/text()').extract_first()).lower())
                data.update({ generated_key : div.xpath('.//span/text()').extract_first() })
        
        rows_section2 = container.xpath('.//section[2]//div[contains(@class, "row")]')
        for row in rows_section2:
            for div in row.xpath('.//div'):
                generated_key = re.sub(r'[ \/]', '_', unidecode(div.xpath('.//strong/text()').extract_first()).lower())
                value = div.xpath('.//a/text()').extract_first() or div.xpath('.//span/text()').extract_first()
                data.update({ generated_key : value })

        rows_section3 = container.xpath('.//section[3]//div[contains(@class, "row")]')
        for row in rows_section3:
            for div in row.xpath('.//div'):
                generated_key = re.sub(r'[ \/]', '_', unidecode(div.xpath('.//strong/text()').extract_first()).lower())
                value1 = div.xpath('.//span[1]/text()').extract_first()
                value2 = div.xpath('.//a/text()').extract_first() or div.xpath('.//span[2]/text()').extract_first()
                data.update({ generated_key : value1 + ' - ' + value2 })

        trs_section4 = container.xpath('.//section[4]//table[contains(@id, "listaEmpenhosImpactados")]/tbody/tr')
        for tr in trs_section4:
            data.update({
                'empenhoResumido': tr.xpath('.//td[1]//a/text()').extract_first(),
                'subitem': tr.xpath('.//td[2]//span/text()').extract_first(),
                'valorLiquidado': tr.xpath('.//td[3]//span/text()').extract_first(),
                'valorInscritoRestoPagar': tr.xpath('.//td[4]//span/text()').extract_first(),
                'valorRestoPagarCancelado': tr.xpath('.//td[5]//span/text()').extract_first(),
                'valorRestoPagarPago': tr.xpath('.//td[6]//span/text()').extract_first(),
            })

        liquidacao_date = re.sub(r'[ \/]', '', self.date)
        fase = response.url.split('/')[2]
        root = str(Path(os.path.abspath(os.curdir)).parent.absolute())
        directory = root+'/datalake/raw_zone/licitacao/pagamentos/'
        filename = liquidacao_date+'_'+fase+'_pt_governo_federal.json'
        
        exist_data = {}

        isdir = os.path.isdir(directory)
        if not isdir:
            os.makedirs(directory)


        with open(directory+filename, 'r') as outfile:
            exist_data = json.load(outfile)
        
        if exist_data:
            exist_data['data'].update(data)

        new_data = json.dumps(exist_data, indent=4, ensure_ascii=False)
        with open (directory+filename, 'w') as outfile:
            outfile.write(new_data)