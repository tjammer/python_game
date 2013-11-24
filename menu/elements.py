class TextboxFramed(object):
    """docstring for Textbox_framed"""
    def __init__(self, pos, size, f_size):
        super(TextboxFramed, self).__init__()
        self.pos = pos
        self.size = size
        self.f_size = f_size
        # code for text here

    def in_box(self, m_pos):
        m_x = m_pos[0]
        m_y = m_pos[1]
        if m_x > self.pos[0] and m_x < self.pos[0] + self.size[0]:
            if m_y > self.pos[1] and m_y < self.pos[1] + self.size[1]:
                return True
        return False
