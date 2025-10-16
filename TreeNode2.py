class TreeNode:

    coord = None
    priority = None
    value_gx = None
    parent = None
    runes_usage = None # NOVO: Dicionário ou Tupla representando os usos restantes das runas
    visited_events = None # NOVO: Set dos caracteres dos eventos já visitados

    def __init__(self, coord, fx, gx, runes_usage=None, visited_events=None):
        self.coord = coord
        self.priority = fx
        self.value_gx = gx
        # NOVO CÓDIGO AQUI
        # runas_usage: Dicionário {'1': 5, '2': 5, ...} ou Tupla (5, 5, 5, 5, 5)
        # Usaremos uma tupla para facilitar o uso como chave em dicionários de visitados
        self.runes_usage = runes_usage if runes_usage is not None else (5, 5, 5, 5, 5)
        self.visited_events = visited_events if visited_events is not None else set()
        # FIM NOVO CÓDIGO

    def get_coord(self):
        return self.coord

    def get_priority(self):
        return self.priority

    def get_value_gx(self):
        return self.value_gx

    def set_parent(self, value):
        self.parent = value

    def get_parent(self):
        return self.parent

    # NOVO CÓDIGO AQUI
    def get_runes_usage(self):
        return self.runes_usage

    def get_visited_events(self):
        return self.visited_events

    def get_state_key(self):
        # Chave complexa para o dicionário de visitados: (coordenada, tupla de usos das runas, tupla de eventos visitados)
        # O set de eventos deve ser convertido em uma tupla para ser hashable
        sorted_events_tuple = tuple(sorted(list(self.visited_events)))
        return (self.coord, self.runes_usage, sorted_events_tuple)
    # FIM NOVO CÓDIGO

    def __lt__(self, other):
        return self.priority < other.priority