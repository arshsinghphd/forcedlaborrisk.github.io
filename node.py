class node:
    def __init__(self, code, name, depth = -1, color = 'white', parent_code = 0):
        self.code = code
        self.name = name
        self.depth = depth
        self.color = color
        self.parent = parent_code
        self.trade_value = 0
        self.imp_partners = []
        # white = unvisited, red = someone's imp trade partner
        
