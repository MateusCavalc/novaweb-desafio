# Custom Exception
class ContatoNotFound(Exception):
    def __init__(self, contato_nome):
        self.message = "Contato \'" + contato_nome + "\' not found."
        super().__init__(self.message)