from constants import *
from utils import melody_to_sheet, random_choice, get_num_notes, equalize
from rhythm import generate_length_sequence, get_shift


def get_next_diminished_note(previous_note, max_step_interval):
    if previous_note == None:
        previous_note = 0
    next_note = random_choice(CONST.diminished_scale, p=CONST.p_diminished)
    if next_note == previous_note or abs(next_note - previous_note) > max_step_interval:
        while next_note == previous_note or abs(next_note - previous_note) > max_step_interval:
            next_note = random_choice(CONST.diminished_scale, p=CONST.p_diminished)
    return next_note

def generate_diminished_melody(global_root_note, seq_length):
    diminished_melody = list()
    previous_note = None
    for i in range(seq_length):
        note = get_next_diminished_note(previous_note, CONST.max_step_interval)
        diminished_melody.append(global_root_note + note)
        previous_note = note
    return diminished_melody

def get_third_steps(color):
    if color == 'black':
        up = CONST.third_black_up
        down = CONST.third_black_down
    else:
        up = CONST.third_white_up
        down = CONST.third_white_down
    return up, down

def get_next_third_interval(table, mode):
    options = table[mode]
    if type(options) == list:
        p_options = [1/len(options) for _ in range(len(options))]
        next_step = random_choice(options, p=p_options)
    else:
        next_step = options
    return next_step

def generate_third_jump_melody(color, global_root_note, seq_length):
    up, down = get_third_steps(color)
    n_start_pos = int(seq_length / 2)
    third_melody = list()
    for i in range(n_start_pos):
        mode = random_choice(CONST.modes, p=CONST.p_modes)
        direction = random_choice(['up', 'down'], p=[0.51, 0.49])
        if direction == 'up':
            next_step = get_next_third_interval(up, mode)
        else:
            next_step = (-1) * get_next_third_interval(down, mode)
        first = abs(global_root_note + mode)
        second = abs(global_root_note + mode + next_step)
        third_melody.append(first)
        third_melody.append(second)
    return third_melody

def generate_triangle_sheet(color, avg_shape_size, global_root_note, playfulness, structure=None, seq_length=None):
    if seq_length is None:
        length = get_length('triangle', avg_shape_size)
        seq_length = get_num_notes(length)

    shift = get_shift('triangle', avg_shape_size)
    root_note = global_root_note + shift * 12
    diminished = random_choice([True, False], p=[0.5, 0.5])
    if color == 'black' and diminished:
        keys = generate_diminished_melody(root_note, seq_length)
    else:
        keys = generate_third_jump_melody(color, root_note, seq_length)
    lens, lag_flag = generate_length_sequence('triangle', avg_shape_size, seq_length, playfulness=playfulness, structure=structure)
    if lag_flag:
        keys = [CONST.rest] + keys
    keys, lens = equalize(keys, lens)
    joins = [False] * len(keys)
    melody = (keys, lens, joins)
    triangle_sheet = melody_to_sheet(melody)
    return triangle_sheet
