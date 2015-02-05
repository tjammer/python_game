from xml.etree import ElementTree as etree

pre = '{http://www.collada.org/2005/11/COLLADASchema}'


def parse_dae(filename, scale=0.94):
    scale = 36. * scale
    root = etree.parse(filename).getroot()
    #geometry data
    mesh = [source for source in root.iter(pre + 'source')
            if 'Plane-mesh' in source.attrib['id']]

    allverts = [float(i) * scale for i in mesh[0][0].text.split()]
    vertices = pair(allverts, 3)

    allnorms = [float(i) for i in mesh[1][0].text.split()]
    normals = pair(allnorms, 3)

    allfaces = [vert for vert in root.iter(pre + 'polylist')
                if 'Plane-mesh' in vert[0].attrib['source']]
    faces = []
    for item in allfaces:
        #check if all quads
        for face in item.find(pre + 'vcount').text.split():
            if int(face) != 4:
                raise (TypeError, 'not a quad')

        allvals = [int(i) for i in item.find(pre + 'p').text.split()]
        facev = allvals[::2]
        facen = allvals[1::2]

        material = item.attrib['material'][:-9] + '-effect'
        col = [ef for ef in root.iter(pre + 'effect')
               if material in ef.attrib['id']][0]
        color = [float(i) for i in [d for d in col.iter(
            pre + 'diffuse')][0].getchildren()[0].text.split()]
        faces.append((color, facev, facen))

    #skeletal data
    joint_names = [item for item in root.iter(pre + 'Name_array')
                   if 'base' in item.attrib['id']][0].text.split()
    root_sid = [it for it in root.iter(pre + 'skeleton')][0].text[1:]
    sk_root = [it for it in root.iter(pre + 'node') if 'sid' in it.keys()
               and it.attrib['sid'] == root_sid][0]

    joints = Joint(sk_root)
    joints.set_index(joint_names)
    joint_data = [joint.data for i in range(len(joint_names))
                  for joint in joints if joint.index == i]

    bind_poses = [float(i) for i in [arr.text for arr in root.iter(
        pre + 'float_array') if 'bind_poses' in arr.attrib['id']][0].split()]
    inverse_m = pair(bind_poses, 16)

    skin_weights = [float(i) for i in [arr.text for arr in root.iter(
        pre + 'float_array') if 'skin-weights' in arr.attrib['id']][0].split()]

    #vertex weights
    vw = [i for i in root.iter(pre + 'vertex_weights')][0]
    vcount = [int(i) for i in vw.getchildren()[2].text.split()]
    weights = [int(i) for i in vw.getchildren()[3].text.split()]
    bone_weigth_ids = weights[::2]
    weight_inds = weights[1::2]

    skin_arr = (skin_weights, vcount, bone_weigth_ids, weight_inds, inverse_m)

    #animation data
    anim_count = count_anims(root.iter(pre + 'animation'))
    anims = [[None for i in range(len(joint_names))]
             for j in range(anim_count)]

    for animation in root.iter(pre + 'animation'):
        for child in animation.getchildren():
            if 'id' in child.keys():
                if 'input' in child.attrib['id']:
                    times = map(float, child.getchildren()[0].text.split())
                elif 'output' in child.attrib['id']:
                    m_arr = map(float, child.getchildren()[0].text.split())
                    matrices = pair(m_arr, 16)
            if 'target' in child.keys():
                index = joint_names.index(child.attrib['target'].split('/')[0])
        for i in range(anim_count):
            step = 100. / 24
            temp = [time for time in times if i*step < time < (i+1)*step]
            an_times = [time - temp[0] for time in temp]
            an_matrices = [matrices[times.index(time)] for time in temp]
            anims[i][index] = (an_times, an_matrices)

        #anims[index] = (times, matrices)

    return vertices, normals, faces, joint_data, joints, skin_arr, anims, scale


def pair(arr, n):
    return [arr[i:i+n] for i in range(0, len(arr), n)]


class Joint(object):
    """docstring for Joint"""
    def __init__(self, element):
        super(Joint, self).__init__()
        #xml element of joint element
        #matrix data
        self.data = [float(item) for item in
                     element.find(pre + 'matrix').text.split()]
        self.name = element.attrib['name']
        self.nodes = [Joint(el) for el in element.findall(pre + 'node')]

    def __iter__(self):
        ar = [it for node in self.nodes for it in node.__iter__()] + [self]
        return iter(ar)

    def set_index(self, names):
        self.index = names.index(self.name.replace('.', '_'))
        self.len = len(self.nodes)
        for node in self.nodes:
            node.set_index(names)


def count_anims(animgen):
    for animation in animgen:
        for child in animation.getchildren():
            if 'id' in child.keys():
                if 'input' in child.attrib['id']:
                    times = map(float, child.getchildren()[0].text.split())
                    maxt = max(times)
                    #blender runs animation at 24 fps
                    step = 100. / 24
                    return int(maxt // step) + 1
    return 0
