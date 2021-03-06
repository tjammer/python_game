from caabb import cAABB as AABB


class QuadTree(object):
    """Heavily inspired from
    http://gamedevelopment.tutsplus.com/tutorials/quick-tip-use-quadtrees-to-detect-likely-collisions-in-2d-space--gamedev-374
    """
    def __init__(self, level, rect, server):
        super(QuadTree, self).__init__()
        self.maxobjects = 5
        self.maxlevel = 5

        self.level = level
        self.objects = []
        self.bounds = rect
        self.nodes = [None] * 4
        self.server = server
        if not server:
            from graphics.primitives import Rect
            self.Rect = Rect
        else:
            self.Rect = AABB

    def clear(self):
        """clears the QuadTree"""
        for quadtree in self.nodes:
            if quadtree is not None:
                quadtree.clear()
                quadtree = None

    def split(self):
        sub_width = self.bounds.width / 2
        sub_height = self.bounds.height / 2
        x = self.bounds.pos.x
        y = self.bounds.pos.y

        self.nodes[0] = QuadTree(self.level+1,
                                 self.Rect(x + sub_width, y,
                                           sub_width, sub_height), self.server)
        self.nodes[1] = QuadTree(self.level+1,
                                 self.Rect(x, y,
                                           sub_width, sub_height), self.server)
        self.nodes[2] = QuadTree(self.level+1,
                                 self.Rect(x, y + sub_height,
                                           sub_width, sub_height), self.server)
        self.nodes[3] = QuadTree(self.level+1,
                                 self.Rect(x + sub_width, y + sub_height,
                                           sub_width, sub_height), self.server)

    def get_index(self, rect):
        """the assumption is that no object is that no object is bigger
        than a cell if i am correct"""

        index = -1
        x_center = self.bounds.pos.x + self.bounds.width / 2
        y_center = self.bounds.pos.y + self.bounds.height / 2

        top = rect.pos.y > y_center
        bottom = rect.pos.y < y_center and rect.pos.y + rect.height < y_center

        # check for left quadrants
        if rect.pos.x < x_center and rect.pos.x + rect.width < x_center:
            if top:
                index = 2
            elif bottom:
                index = 1

        # check for right quadrants
        elif rect.pos.x > x_center:
            if top:
                index = 3
            elif bottom:
                index = 0

        return index

    def insert(self, rect):
        if self.nodes[0] is not None:
            index = self.get_index(rect)
            if index != -1:
                self.nodes[index].insert(rect)
                return

        self.objects.append(rect)

        if len(self.objects) > self.maxobjects and self.level < self.maxlevel:
            if self.nodes[0] is None:
                self.split()

            # temp list stoes values which go in child node and deletes them
            # from parent nodes objects
            temp_list = []
            for obj in self.objects:
                index = self.get_index(obj)
                if index != -1:
                    self.nodes[index].insert(obj)
                    temp_list.append(obj)

            for obj in temp_list:
                self.objects.remove(obj)

    def retrieve(self, lst, rect):
        if self.nodes[0] is not None:
            index = self.get_index(rect)
            if index != -1:
                self.nodes[index].retrieve(lst, rect)
            else:
                for node in self.nodes:
                    for rect in node.objects:
                        lst.append(rect)

        for rect in self.objects:
            lst.append(rect)
        return lst

    def retrieve_bound(self, rect):
        if self.nodes[0] is not None:
            index = self.get_index(rect)
            if index != -1:
                return self.nodes[index].retrieve_bound(rect)

        return self.bounds
