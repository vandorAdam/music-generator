from constants import *
from utils import random_choice


''' ############################################################################
### RECTANGLES
############################################################################ '''


def get_rect_len(avg_shape_size):
    if avg_shape_size == 'large':
        length = CONST.whole
    elif avg_shape_size == 'medium':
        length = CONST.half
    else:
        length = CONST.half
    return length

def get_rect_shift(avg_shape_size):
    if avg_shape_size == 'large':
        shift = 0
    elif avg_shape_size == 'medium':
        shift = 0
    else:
        shift = 1
    return shift


''' ############################################################################
### CIRCLES
############################################################################ '''


def get_circle_len(avg_shape_size):
    if avg_shape_size == 'large':
        length = CONST.eighth
    elif avg_shape_size == 'medium':
        length = CONST.sixteenth
    else:
        # length = CONST.thirty_second
        length = CONST.sixteenth
    return length

def get_circle_shift(avg_shape_size):
    if avg_shape_size == 'large':
        shift = 0
    elif avg_shape_size == 'medium':
        shift = 0
    else:
        shift = 1
    return shift

def get_circle_num_octaves(n_shapes):
    if n_shapes == 'lots':
        n_octaves = 3
    elif n_shapes == 'medium':
        n_octaves = 2
    else:
        n_octaves = 1
    return n_octaves


''' ############################################################################
### TRIANGLES
############################################################################ '''


def get_triangle_len(avg_shape_size, use_tuples):
    ''' Only lagging. No tuples. '''
    if avg_shape_size == 'large':
        if use_tuples:
            length = CONST.long_triplet
        else:
            length = CONST.quarter
    elif avg_shape_size == 'medium':
        if use_tuples:
            length = CONST.short_triplet
        else:
            length = CONST.quarter
    else:
        if use_tuples:
            length = CONST.short_triplet
        else:
            length = CONST.eighth
    return length

def get_triangle_shift(avg_shape_size):
    if avg_shape_size == 'large':
        shift = -1
    elif avg_shape_size == 'medium':
        shift = 0
    else:
        shift = 1
    return shift

def get_length(shape, avg_shape_size, use_tuples=None):
    if shape == 'rectangle':
        length = get_rect_len(avg_shape_size)
    elif shape == 'circle':
        length = get_circle_len(avg_shape_size)
    else:
        length = get_triangle_len(avg_shape_size, use_tuples)
    return length

def get_shift(shape, avg_shape_size):
    if shape == 'rectangle':
        shift = get_rect_shift(avg_shape_size)
    elif shape == 'circle':
        shift = get_circle_shift(avg_shape_size)
    else:
        shift = get_triangle_shift(avg_shape_size)
    return shift

def get_note_length_probs(avg_shape_size):
    if avg_shape_size == 'very_large':
        lengths = [CONST.half, CONST.quarter]
        probs = [0.5, 0.5]

    elif avg_shape_size == 'large':
        lengths = [CONST.half, CONST.quarter, CONST.eighth]
        probs = [0.4, 0.4, 0.2]

    elif avg_shape_size == 'medium':
        lengths = [CONST.quarter, CONST.eighth, CONST.sixteenth]
        probs = [0.4, 0.4, 0.2]

    elif avg_shape_size == 'small':
        lengths = [CONST.eighth, CONST.sixteenth]
        probs = [0.4, 0.6]

    elif avg_shape_size == 'very_small':
        lengths = [CONST.sixteenth, CONST.thirty_second]
        probs = [0.5, 0.5]

    return lengths, probs

def get_split_lengths(length):
    long = 1 / ( 1/length + 1 / ( 2 * length))
    short = length / 2
    return long, short

def rigid_to_playful(note_lengths, playfulness, seq_length=None):
    if seq_length == None:
        seq_length = CONST.melody_length
    new_lengths = note_lengths.copy()
    i = 0
    while i < seq_length:
        section = new_lengths[i:i+2]
        if len(set(section)) == 1:
            split = random_choice(items=[True, False], p=[playfulness, 1-playfulness])
            if split:
                split_section = split_rhythm(section)
                new_lengths[i:i+2] = split_section
        i += 2
    if len(new_lengths) > seq_length:
        new_lengths = new_lengths[:seq_length]
    return new_lengths

def split_rhythm(section):
    length = section[0]
    long, short = get_split_lengths(length)
    long_first = random_choice([True, False], p=[CONST.p_split_long_first, 1-CONST.p_split_long_first])
    if long_first:
        split_section = [long, short]
    else:
        split_section = [short, long]
    return split_section

def lag(note_lengths):
    ''' Only apply to fully structured, non-tuple sequences. '''
    rest = [int(note_lengths[0] * 2)]
    middle_part = note_lengths[:-1]
    last_note = [int(note_lengths[-1] * 2)]
    lagging_lengths = rest + middle_part + last_note
    return lagging_lengths

def generate_length_sequence(shape, avg_shape_size, seq_length, playfulness=0.5, structure=None, extend_last=True):
    lag_flag = False
    if shape is 'triangle' and not CONST.exclude_tuples:
        use_tuples = random_choice([True, False], p=[0.5, 0.5])
    else:
        use_tuples = None
    if CONST.uniform_lengths or shape is 'triangle':
        length = get_length(shape, avg_shape_size, use_tuples)
        note_lengths = [length] * seq_length
    else:
        lengths, probs = get_note_length_probs(avg_shape_size)
        note_lengths = list()
        i = 0
        while i < seq_length:
            length = random_choice(lengths, p=probs)
            if structure is not None:
                for _ in range(structure):
                    note_lengths.append(length)
                i += structure
            else:
                i += 1
    if playfulness > 0 and shape is not 'triangle':
        note_lengths = rigid_to_playful(note_lengths, playfulness, seq_length=seq_length)
    if shape is 'triangle' and not use_tuples and CONST.lag:
        note_lengths = lag(note_lengths)
        lag_flag = True
    if extend_last:
        # Make last note last longer
        note_lengths[-1] = CONST.half
    # note_lengths[-1] = 0.5
    return note_lengths, lag_flag
