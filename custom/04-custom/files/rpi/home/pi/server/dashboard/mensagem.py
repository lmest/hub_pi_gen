class Mensagem(object):
    def __init__(self, mensagem, ssid, tipo):
        self.mensagem = mensagem
        self.ssid     = ssid
        self.tipo     = tipo
        
    def __str__(self):
        return self.mensagem
