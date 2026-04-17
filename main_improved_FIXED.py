import os
import sys
import base64
import csv
import logging
from datetime import datetime
from typing import Optional, Dict, List, Tuple
from pathlib import Path
import time

# Configurar encoding UTF-8 para o console no Windows
if sys.platform == 'win32':
    try:
        # Tenta configurar console para UTF-8
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
    except:
        pass  # Se falhar, continua normalmente

from openai import OpenAI
from PIL import Image
from tqdm import tqdm
from dotenv import load_dotenv
import tenacity

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('processamento.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Carregar variáveis de ambiente
load_dotenv()

# Configurações
class Config:
    API_KEY = os.getenv("OPENAI_API_KEY")
    MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    INPUT_FOLDER = os.getenv("INPUT_FOLDER", "folders_entrada")
    OUTPUT_CSV = os.getenv("OUTPUT_CSV", "produtos_precos_03.csv")
    ERROR_CSV = os.getenv("ERROR_CSV", "erros_processamento.csv")
    MAX_IMAGE_SIZE = int(os.getenv("MAX_IMAGE_SIZE", "4096"))  # pixels - aumentado para não perder qualidade no OCR
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))
    MAX_RETRIES = int(os.getenv("MAX_RETRIES", "3"))
    RETRY_WAIT = int(os.getenv("RETRY_WAIT", "2"))  # segundos

# Inicializar cliente OpenAI
client = OpenAI(api_key=Config.API_KEY)


def otimizar_imagem(caminho: str) -> str:
    """
    Redimensiona a imagem se for muito grande para reduzir custos de API.
    Retorna o caminho da imagem otimizada (temporária) ou original.
    """
    try:
        img = Image.open(caminho)
        
        # Se a imagem já é pequena, retorna o caminho original
        if max(img.size) <= Config.MAX_IMAGE_SIZE:
            return caminho
        
        # Redimensiona mantendo aspect ratio
        ratio = Config.MAX_IMAGE_SIZE / max(img.size)
        new_size = tuple(int(dim * ratio) for dim in img.size)
        img_resized = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # Salva temporariamente com ALTA qualidade para manter texto legível
        temp_path = caminho + ".temp.jpg"
        img_resized.convert('RGB').save(temp_path, 'JPEG', quality=98)  # quality aumentada de 85 para 98
        
        logger.debug(f"Imagem otimizada: {caminho} ({img.size} -> {new_size})")
        return temp_path
        
    except Exception as e:
        logger.warning(f"Erro ao otimizar imagem {caminho}: {e}. Usando original.")
        return caminho


def imagem_para_base64(path: str) -> str:
    """Converte imagem para base64."""
    try:
        with open(path, "rb") as img:
            return base64.b64encode(img.read()).decode("utf-8")
    except Exception as e:
        logger.error(f"Erro ao converter imagem para base64 {path}: {e}")
        raise


@tenacity.retry(
    stop=tenacity.stop_after_attempt(Config.MAX_RETRIES),
    wait=tenacity.wait_exponential(multiplier=Config.RETRY_WAIT, min=2, max=10),
    retry=tenacity.retry_if_exception_type((Exception,)),
    before_sleep=lambda retry_state: logger.warning(
        f"Tentativa {retry_state.attempt_number} falhou. Aguardando antes de tentar novamente..."
    )
)
def extrair_informacoes_flyer(image_base64: str) -> str:
    """
    Extrai produtos, preços e informações do flyer (loja, tipo, validade).
    Usa retry automático em caso de falha.
    """
    prompt = """
Você é um sistema de OCR e EXTRAÇÃO 100% literal e preciso.
Você deve extrair exatamente o texto que aparece na imagem - sem corrigir, reescrever, completar ou inferir nada.

SUA TAREFA EM DUAS ETAPAS:

ETAPA 1 - IDENTIFICAR METADADOS (se existirem):
1. Procure o NOME DA LOJA (logotipo, cabeçalho)
2. Identifique o TIPO DE COMÉRCIO baseado nos produtos e layout
3. Procure a DATA DE VALIDADE (textos como "válido até", "ofertas válidas até")

REGRAS PARA METADADOS:
- Se NÃO encontrar o nome da loja, escreva: "Nome não identificado"
- Se NÃO conseguir identificar o tipo, escreva: "Tipo não identificado"  
- Se NÃO encontrar data de validade, escreva: "Validade não identificada"
- NUNCA invente nomes, tipos ou datas que não estão visíveis na imagem

ETAPA 2 - EXTRAIR PRODUTOS E PREÇOS:
- Leia nomes de produtos EXATAMENTE como estão na imagem
- NÃO corrigir ortografia
- NÃO alterar marcas
- Se o nome estiver em DUAS OU MAIS LINHAS, una em UMA frase mantendo a ordem
- Extraia TODAS as informações relevantes, mesmo que pequenas
- NÃO traduzir, NÃO inferir, NÃO resumir
- Se tiver dúvida sobre palavra, extraia do jeito que conseguir ler
- Nunca substitua por outra palavra
- FOQUE APENAS nos produtos e preços VISÍVEIS na imagem

FORMATO DA RESPOSTA:
Primeira linha (metadados separados):
LOJA: [nome ou "Nome não identificado"]
TIPO: [tipo ou "Tipo não identificado"]
VALIDADE: [data ou "Validade não identificada"]

Depois, liste APENAS os produtos que você consegue LER na imagem:
produto;preço

Exemplo de resposta quando HÁ nome da loja:
LOJA: Supermercado Preço Bom
TIPO: Supermercado
VALIDADE: Válido até 31/12/2024
Arroz Tio João 5kg;R$ 25,90
Feijão Preto 1kg;R$ 8,50

Exemplo quando NÃO HÁ nome da loja:
LOJA: Nome não identificado
TIPO: Farmácia
VALIDADE: Validade não identificada
Dipirona 500mg;R$ 12,00
Paracetamol 750mg;R$ 8,50
"""

    response = client.chat.completions.create(
        model=Config.MODEL,
        messages=[
            {
                "role": "system", 
                "content": "Você seguirá estritamente as regras do prompt. Seja preciso e literal. NUNCA invente produtos ou preços que não estão na imagem."
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url", 
                        "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                    }
                ]
            }
        ],
        temperature=Config.TEMPERATURE,
        max_tokens=2000
    )

    return response.choices[0].message.content.strip()


def validar_preco(preco: str) -> str:
    """
    Valida e limpa o formato do preço.
    Remove caracteres estranhos mas mantém o formato original quando possível.
    """
    if not preco:
        return "Preço não identificado"
    
    # Remove espaços extras
    preco = preco.strip()
    
    # Se já parece um preço válido, retorna
    if any(char.isdigit() for char in preco):
        return preco
    
    return "Preço não identificado"


def parsear_resposta_llm(resposta: str, arquivo: str) -> Tuple[Dict[str, str], List[List[str]]]:
    """
    Faz o parsing da resposta da LLM separando informações da loja e produtos.
    Retorna: (info_loja, lista_produtos)
    """
    info_loja = {
        'nome': 'Nome não identificado',
        'tipo': 'Tipo não identificado',
        'validade': 'Validade não identificada'
    }
    
    produtos = []
    linhas = resposta.split("\n")
    
    # Primeiro, extrair metadados das linhas LOJA:/TIPO:/VALIDADE:
    for linha in linhas:
        linha_upper = linha.upper().strip()
        
        if linha_upper.startswith("LOJA:"):
            info_loja['nome'] = linha.split(":", 1)[1].strip()
        elif linha_upper.startswith("TIPO:"):
            info_loja['tipo'] = linha.split(":", 1)[1].strip()
        elif linha_upper.startswith("VALIDADE:"):
            info_loja['validade'] = linha.split(":", 1)[1].strip()
    
    # Depois, extrair produtos no formato: produto;preço
    for linha in linhas:
        linha = linha.strip()
        
        # Pular linhas vazias ou de metadados
        if not linha or linha.upper().startswith(("LOJA:", "TIPO:", "VALIDADE:")):
            continue
            
        # Verificar se tem ponto-e-vírgula (produto;preço)
        if ";" in linha:
            partes = linha.split(";")
            
            # Formato simples: produto;preço (2 campos)
            if len(partes) == 2:
                produto = partes[0].strip()
                preco = validar_preco(partes[1].strip())
                
                if produto:
                    produtos.append([
                        arquivo,
                        produto,
                        preco,
                        info_loja['nome'],
                        info_loja['tipo'],
                        info_loja['validade']
                    ])
            
            # Formato expandido: produto;preço;loja;tipo;validade (5 campos)
            # Mantido para compatibilidade com respostas antigas
            elif len(partes) >= 5:
                produto = partes[0].strip()
                preco = validar_preco(partes[1].strip())
                loja = partes[2].strip() if partes[2].strip() else "Nome não identificado"
                tipo = partes[3].strip() if partes[3].strip() else "Tipo não identificado"
                validade = partes[4].strip() if partes[4].strip() else "Validade não identificada"
                
                if produto:
                    produtos.append([
                        arquivo,
                        produto,
                        preco,
                        loja,
                        tipo,
                        validade
                    ])
                    
                    # Atualizar info_loja se não foi definida ainda
                    if info_loja['nome'] == 'Nome não identificado' and loja != 'Nome não identificado':
                        info_loja['nome'] = loja
                        info_loja['tipo'] = tipo
                        info_loja['validade'] = validade
    
    return info_loja, produtos


def processar_imagem(arquivo: str, caminho: str) -> Tuple[Optional[List[List[str]]], Optional[str]]:
    """
    Processa uma única imagem.
    Retorna: (lista_produtos, mensagem_erro)
    """
    temp_path = None
    
    try:
        # Otimizar imagem
        temp_path = otimizar_imagem(caminho)
        
        # Converter para base64
        b64 = imagem_para_base64(temp_path)
        
        # Chamar API
        logger.info(f"Processando {arquivo}...")
        resposta = extrair_informacoes_flyer(b64)
        
        # Parsear resposta
        info_loja, produtos = parsear_resposta_llm(resposta, arquivo)
        
        logger.info(
            f"[OK] {arquivo}: {len(produtos)} produtos | "
            f"Loja: {info_loja['nome']} | Tipo: {info_loja['tipo']}"
        )
        
        return produtos, None
        
    except Exception as e:
        erro_msg = f"Erro ao processar {arquivo}: {str(e)}"
        logger.error(erro_msg)
        return None, erro_msg
        
    finally:
        # Limpar arquivo temporário se foi criado
        if temp_path and temp_path != caminho and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except:
                pass


def processar_pasta():
    """Processa todas as imagens da pasta de entrada."""
    
    # Verificar se a pasta existe
    if not os.path.exists(Config.INPUT_FOLDER):
        logger.error(f"Pasta {Config.INPUT_FOLDER} não encontrada!")
        return
    
    # Listar arquivos de imagem
    arquivos = [
        f for f in os.listdir(Config.INPUT_FOLDER)
        if f.lower().endswith((".jpg", ".jpeg", ".png"))
    ]
    
    # arquivos = ["folder_07.jpg"] # Descomente para processar somente uma imagem
    
    if not arquivos:
        logger.warning(f"Nenhuma imagem encontrada em {Config.INPUT_FOLDER}")
        return
    
    logger.info(f"Encontradas {len(arquivos)} imagens. Iniciando processamento...")
    logger.info(f"Modelo: {Config.MODEL} | Max retries: {Config.MAX_RETRIES}")
    
    resultados = []
    erros = []
    inicio = time.time()
    
    # Processar cada imagem
    for arquivo in tqdm(arquivos, desc="Processando imagens"):
        caminho = os.path.join(Config.INPUT_FOLDER, arquivo)
        produtos, erro = processar_imagem(arquivo, caminho)
        
        if produtos:
            resultados.extend(produtos)
        else:
            erros.append([arquivo, erro or "Erro desconhecido"])
    
    # Salvar resultados
    if resultados:
        with open(Config.OUTPUT_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow([
                "imagem", 
                "produto", 
                "preço", 
                "loja", 
                "tipo", 
                "validade"
            ])
            writer.writerows(resultados)
        logger.info(f"[OK] Arquivo gerado: {Config.OUTPUT_CSV} ({len(resultados)} produtos)")
    
    # Salvar erros
    if erros:
        with open(Config.ERROR_CSV, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter=";")
            writer.writerow(["imagem", "erro"])
            writer.writerows(erros)
        logger.warning(f"[AVISO] Arquivo de erros gerado: {Config.ERROR_CSV} ({len(erros)} erros)")
    
    # Resumo final
    tempo_total = time.time() - inicio
    logger.info("\n" + "="*60)
    logger.info("RESUMO DO PROCESSAMENTO")
    logger.info("="*60)
    logger.info(f"Total de imagens: {len(arquivos)}")
    logger.info(f"Processadas com sucesso: {len(arquivos) - len(erros)}")
    logger.info(f"Com erro: {len(erros)}")
    logger.info(f"Total de produtos extraídos: {len(resultados)}")
    logger.info(f"Tempo total: {tempo_total:.2f}s ({tempo_total/len(arquivos):.2f}s por imagem)")
    logger.info("="*60)


if __name__ == "__main__":
    try:
        processar_pasta()
    except KeyboardInterrupt:
        logger.warning("\nProcessamento interrompido pelo usuário.")
    except Exception as e:
        logger.error(f"Erro fatal: {e}", exc_info=True)