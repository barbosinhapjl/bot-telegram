"""
Bot do Telegram - Clima das Praias do Brasil
"""

import requests
import telebot
from telebot import types

# ============================================
# CONFIGURAÇÃO
# ============================================

TELEGRAM_TOKEN = "8337117027:AAFjSp1VjOTAXHsMfW2EVdfgpd-NxV8KkKo"
WEATHER_API_KEY = "35691b90bdbfea6881c47789c3365d7b"

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# ============================================
# PRAIAS DO BRASIL
# ============================================

PRAIAS_BRASIL = {
    'Copacabana': 'Rio de Janeiro,BR',
    'Ipanema': 'Rio de Janeiro,BR',
    'Boa Viagem': 'Recife,BR',
    'Ponta Negra': 'Natal,BR',
    'Salvador': 'Salvador,BR',
    'Florianópolis': 'Florianópolis,BR',
    'Guarujá': 'Guarujá,BR',
    'Santos': 'Santos,BR',
    'Fortaleza': 'Fortaleza,BR',
    'Maceió': 'Maceió,BR'
}


# ============================================
# FUNÇÕES BÁSICAS
# ============================================

def obter_clima(cidade):
    """Obtém clima da cidade"""
    url = "http://api.openweathermap.org/data/2.5/weather"
    params = {
        'q': cidade,
        'appid': WEATHER_API_KEY,
        'units': 'metric',
        'lang': 'pt_br'
    }
    
    try:
        print(f"Buscando clima de: {cidade}")
        response = requests.get(url, params=params, timeout=10)
        print(f"Status code: {response.status_code}")
        
        if response.status_code == 200:
            dados = response.json()
            print(f"Dados recebidos para {cidade}")
            return dados
        else:
            print(f"Erro na API: {response.status_code}")
            return None
    except Exception as e:
        print(f"Erro ao buscar clima: {e}")
        return None


def emoji_clima(temp, descricao=''):
    """Retorna emoji baseado na temperatura"""
    try:
        if temp >= 30:
            return '🔥'
        elif temp >= 25:
            return '☀️'
        elif temp >= 20:
            return '🌤️'
        else:
            return '☁️'
    except:
        return '🌡️'


def formatar_clima_simples(dados):
    """Formata dados do clima de forma simples"""
    try:
        nome = dados['name']
        temp = dados['main']['temp']
        sensacao = dados['main']['feels_like']
        descricao = dados['weather'][0]['description']
        emoji = emoji_clima(temp, descricao)
        
        msg = f"{emoji} *{nome}*: {temp:.1f}°C\n"
        msg += f"Sensação: {sensacao:.1f}°C\n"
        msg += f"{descricao.capitalize()}"
        
        if temp >= 25:
            msg += "\n\n🏖️ *Perfeito para praia!*"
        
        return msg
    except Exception as e:
        print(f"Erro ao formatar: {e}")
        return "Erro ao processar dados"


# ============================================
# COMANDOS DO BOT
# ============================================

@bot.message_handler(commands=['start', 'ajuda', 'help'])
def comando_start(message):
    """Mensagem de boas-vindas"""
    try:
        texto = """
🏖️ *Bot de Clima - Praias do Brasil* 🌊

*Comandos disponíveis:*

/praias - Ver clima das praias
/clima São Paulo - Ver clima de uma cidade
/ajuda - Esta mensagem

*Você também pode enviar apenas o nome da cidade!*
"""
        bot.reply_to(message, texto, parse_mode='Markdown')
        print(f"Comando /start recebido de {message.from_user.username}")
    except Exception as e:
        print(f"Erro no comando start: {e}")
        bot.reply_to(message, "Olá! Use /praias para ver o clima das praias brasileiras!")


@bot.message_handler(commands=['praias'])
def comando_praias(message):
    """Mostra clima de todas as praias do Brasil"""
    try:
        print(f"Comando /praias recebido de {message.from_user.username}")
        
        msg_loading = bot.reply_to(message, "🏖️ Buscando clima das praias... Aguarde!")
        
        mensagem = "🏖️ *PRAIAS DO BRASIL* 🌊\n\n"
        praias_encontradas = 0
        
        for praia, cidade in PRAIAS_BRASIL.items():
            try:
                dados = obter_clima(cidade)
                
                if dados:
                    temp = dados['main']['temp']
                    emoji = emoji_clima(temp)
                    
                    if temp >= 25:
                        mensagem += f"{emoji} *{praia}*: {temp:.0f}°C 🏖️\n"
                    else:
                        mensagem += f"{emoji} {praia}: {temp:.0f}°C\n"
                    
                    praias_encontradas += 1
            except Exception as e:
                print(f"Erro ao processar {praia}: {e}")
                continue
        
        if praias_encontradas > 0:
            mensagem += f"\n✅ {praias_encontradas} praias consultadas"
            mensagem += "\n🔥 Temp ≥ 25°C = Ideal para banho!"
        else:
            mensagem = "❌ Erro ao buscar dados. Tente novamente."
        
        bot.edit_message_text(
            mensagem, 
            msg_loading.chat.id, 
            msg_loading.message_id, 
            parse_mode='Markdown'
        )
        
    except Exception as e:
        print(f"Erro no comando praias: {e}")
        bot.reply_to(message, "❌ Erro ao buscar praias. Tente: /clima [cidade]")


@bot.message_handler(commands=['clima'])
def comando_clima(message):
    """Mostra clima de uma cidade específica"""
    try:
        print(f"Comando /clima recebido: {message.text}")
        
        partes = message.text.split(' ', 1)
        
        if len(partes) < 2:
            bot.reply_to(message, "❌ Use: /clima São Paulo")
            return
        
        cidade = partes[1].strip()
        
        if not cidade:
            bot.reply_to(message, "❌ Informe uma cidade!\nExemplo: /clima Rio de Janeiro")
            return
        
        msg_loading = bot.reply_to(message, f"🔍 Buscando {cidade}...")
        
        dados = obter_clima(cidade)
        
        if dados:
            temp = dados['main']['temp']
            sensacao = dados['main']['feels_like']
            temp_min = dados['main']['temp_min']
            temp_max = dados['main']['temp_max']
            descricao = dados['weather'][0]['description']
            umidade = dados['main']['humidity']
            emoji = emoji_clima(temp)
            
            resposta = f"{emoji} *{dados['name']}, {dados['sys']['country']}*\n\n"
            resposta += f"🌡️ Temperatura: *{temp:.1f}°C*\n"
            resposta += f"🤚 Sensação: {sensacao:.1f}°C\n"
            resposta += f"📊 Min/Max: {temp_min:.0f}°C / {temp_max:.0f}°C\n"
            resposta += f"☁️ {descricao.capitalize()}\n"
            resposta += f"💧 Umidade: {umidade}%"
            
            if temp >= 25:
                resposta += "\n\n🏖️ *Ótimo para praia!*"
            elif temp < 18:
                resposta += "\n\n🧥 *Melhor levar casaco!*"
            
            bot.edit_message_text(
                resposta,
                msg_loading.chat.id,
                msg_loading.message_id,
                parse_mode='Markdown'
            )
        else:
            bot.edit_message_text(
                f"❌ Não encontrei '{cidade}'.\n\nTente:\n• Verificar ortografia\n• Usar nome em inglês (London, Paris)",
                msg_loading.chat.id,
                msg_loading.message_id
            )
            
    except Exception as e:
        print(f"Erro no comando clima: {e}")
        bot.reply_to(message, f"❌ Erro: {str(e)}\n\nTente: /clima São Paulo")


@bot.message_handler(func=lambda message: True)
def mensagem_texto(message):
    """Responde mensagens de texto"""
    try:
        cidade = message.text.strip()
        
        print(f"Mensagem recebida: {cidade}")
        
        if len(cidade) < 3:
            bot.reply_to(message, "Digite o nome de uma cidade ou use /praias")
            return
        
        # Verificar se é uma praia conhecida
        if cidade.title() in PRAIAS_BRASIL:
            cidade = PRAIAS_BRASIL[cidade.title()]
            print(f"Praia reconhecida, buscando: {cidade}")
        
        dados = obter_clima(cidade)
        
        if dados:
            mensagem = formatar_clima_simples(dados)
            bot.reply_to(message, mensagem, parse_mode='Markdown')
        else:
            bot.reply_to(
                message, 
                f"❌ Não encontrei '{cidade}'.\n\nTente:\n• /praias\n• /clima São Paulo"
            )
            
    except Exception as e:
        print(f"Erro ao processar mensagem: {e}")
        bot.reply_to(message, "❌ Erro ao processar.\n\nUse:\n/praias - clima das praias\n/clima [cidade] - clima específico")


# ============================================
# TRATAMENTO DE ERROS
# ============================================

@bot.message_handler(func=lambda message: True, content_types=['photo', 'document', 'audio', 'video'])
def outros_tipos(message):
    """Responde a outros tipos de mensagem"""
    bot.reply_to(message, "Envie o nome de uma cidade ou use /praias 🏖️")


# ============================================
# INICIAR BOT
# ============================================

if __name__ == "__main__":
    print("="*50)
    print("🤖 BOT DE CLIMA DAS PRAIAS")
    print("="*50)
    
    # Verificar tokens
    if TELEGRAM_TOKEN == "SEU_TOKEN_DO_TELEGRAM_AQUI":
        print("❌ ERRO: Configure o TELEGRAM_TOKEN!")
        print("   Fale com @BotFather no Telegram para obter")
        exit()
    
    if WEATHER_API_KEY == "SEU_TOKEN_OPENWEATHERMAP_AQUI":
        print("❌ ERRO: Configure o WEATHER_API_KEY!")
        print("   Obtenha em: https://openweathermap.org/api")
        exit()
    
    print("✅ Tokens configurados")
    print("✅ Iniciando bot...")
    
    try:
        # Testar API
        teste = obter_clima("São Paulo,BR")
        if teste:
            print("✅ API funcionando!")
            print(f"✅ Teste: São Paulo está com {teste['main']['temp']:.1f}°C")
        else:
            print("⚠️ Aviso: API pode estar com problemas")
        
        print("✅ Bot rodando! Pressione Ctrl+C para parar")
        print("="*50)
        
        # Iniciar bot
        bot.infinity_polling(timeout=60, long_polling_timeout=60)
        
    except KeyboardInterrupt:
        print("\n👋 Bot finalizado!")
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        print("\nVerifique:")
        print("1. Token do Telegram está correto?")
        print("2. Token da API OpenWeather está ativo?")
        print("3. Tem conexão com internet?")
        print("4. Instalou: pip install pyTelegramBotAPI requests"