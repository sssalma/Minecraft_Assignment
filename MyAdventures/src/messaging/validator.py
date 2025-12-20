class MessageValidator:

    @staticmethod #= metodes que operen de manera independent
    def validate(message):
        if not message.msg_type:
            raise ValueError("Falta Message type")

        if not message.source:
            raise ValueError("Falta Message source")

        if not message.target:
            raise ValueError("Falta target")

        if not isinstance(message.payload, dict):
            raise ValueError("Payload no es un diccionari")
