class TextButton(Text,ElementBehavior):
    def __init__(self,config:dict):
        Text.__init__(self, config)
        ElementBehavior.__init__(self, config)
    