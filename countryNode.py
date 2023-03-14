class node:
    def __init__(self, code, name, depth = -1, color = 'white', parent_code = 0, engaged = False):
        self.code = code
        self.name = name
        self.depth = depth
        self.engaged = engaged
        self.color = color
        self.parent = parent_code
        self.trade_value = 0
        self.imp_partners = []
        self.trade_with_partners = 0
        # white = unvisited, red = someone's imp trade partner