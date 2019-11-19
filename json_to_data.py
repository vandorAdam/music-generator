import json
from constants import *

def get_size(shape):
    size = shape['transform']['scale']['x']
    if size < CONST.threshold_small:
        return 'small'
    elif size > CONST.threshold_large:
        return 'large'
    else:
        return 'medium'

def get_shape_name(shape):
    index = int(shape['shapeFilename'].split('-')[1])
    return CONST.shape_names[index - 1]

def get_color(shape):
    rgba = shape['shapeColor']
    r = rgba['r']
    g = rgba['g']
    b = rgba['b']
    grayscale = 0.2989 * r + 0.5870 * g + 0.1140 * b
    if grayscale < 0.5:
        return 'black'
    else:
        return 'white'

def add_num(L):
    [L[i].append(len(L)) for i in range(len(L))]

def json_to_data(json_file):

    comp_data = {}
    rectangle_data = list()
    triangle_data = list()
    circle_data = list()

    with open(json_file) as f:
        shapes = json.load(f)['shapes']

    for shape in shapes:
        data = list()
        name = get_shape_name(shape)
        data.append(get_color(shape))
        data.append(get_size(shape))

        if name == 'rectangle':
            rectangle_data.append(data)
        elif name == 'circle':
            circle_data.append(data)
        else:
            triangle_data.append(data)

    add_num(triangle_data)
    add_num(rectangle_data)
    add_num(circle_data)

    comp_data['rectangle'] = rectangle_data
    comp_data['circle'] = circle_data
    comp_data['triangle'] = triangle_data

    return comp_data
