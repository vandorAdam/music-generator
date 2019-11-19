from constants import *
from rectangles import generate_rect_sheet
from circles import generate_circle_sheet
from triangles import generate_triangle_sheet
from utils import init_df, fix_combined_index
from pandas import concat

def merge_melodies(shape, shape_data, global_root):
    if shape_data is None:
        return None

    if shape == 'circle':
        shape_multiplier = CONST.circle_multiplier
    elif shape == 'triangle':
        shape_multiplier = CONST.triangle_multiplier

    combined = init_df('sheet')
    pos = 0
    _, _, n = shape_data[0]
    seq_length = n * shape_multiplier
    section = int(seq_length / len(shape_data))

    for i, data in enumerate(shape_data):
        color, size, n = data
        if shape == 'circle':
            sheet = generate_circle_sheet(color, size, global_root, playfulness=CONST.playfulness, arp_ratio=CONST.arp_ratio, seq_length=seq_length)
        elif shape == 'triangle':
            sheet = generate_triangle_sheet(color, size, global_root, playfulness=CONST.playfulness, seq_length=seq_length)
        if i == len(shape_data) - 1:
            section += 1
        combined = concat((combined, sheet[pos:pos+section]))
        pos += section
    combined = fix_combined_index(combined)
    return combined

def merge_chords(shape_data, global_root):
    combined = init_df('sheet')
    for i, data in enumerate(shape_data):
        color, size, seq_length = data
        sheet = generate_rect_sheet(color, size, global_root, playfulness=CONST.playfulness, seq_length=seq_length)
        chord_index = sheet[sheet['Join'] == False].index.tolist()
        if i == 0:
            combined = concat((combined, sheet[:chord_index[0] + 1]))
        else:
            combined = concat((combined, sheet[chord_index[i-1]+1:chord_index[i]+1]))
    combined = fix_combined_index(combined)
    return combined
