from constants import *
from utils import melody_to_sheet, combine_melodies, random_choice, get_num_notes, equalize
from rhythm import generate_length_sequence, get_shift

def get_scale_root_note():
    mode_shift = randint(0, 8)
    scale_root_note = sum(CONST.major_scale[:mode_shift + 1])
    return scale_root_note

def get_next_note_index(i_note, n_oct, octave_turn):
    next_note_index = i_note % octave_turn
    if i_note > (octave_turn - 1):
        new_oct = n_oct + 1
    else:
        new_oct = n_oct
    return next_note_index, new_oct

def get_scale_vars(color):
    if color == 'white':
        scale = CONST.major_scale
        octave_turn = 7
    else:
        scale = CONST.chromatics
        octave_turn = 12
    return scale, octave_turn

def get_out_of_scale_note(note):
    insert = random_choice([True, False], p=CONST.insert_probs)
    if insert:
        out_of_scale_note = note + 1
        return out_of_scale_note
    else:
        return None

def prepare_new_note(global_root_note, scale, i_note, n_new_octave, octave_turn):
    sum_stop = (i_note % octave_turn) + 1
    note = sum(scale[0:sum_stop])
    note += (n_new_octave * 12)
    note += global_root_note
    return note, sum_stop

def generate_scale_melody(color, global_root_note, scale, octave_turn, motion_span):
    i_note = 0
    i_motion = 1
    n_new_octave = 0
    skip_sizes = list(range(1, 6)) # Skip {1, ..., 5} notes
    rising_motion = [global_root_note]
    while i_motion < motion_span:
        skip = random_choice([True, False], p=CONST.skip_probs)
        if skip:
            skip_step = random_choice(skip_sizes, p=CONST.jump_probs)
            i_note += (skip_step + 1)
        else:
            i_note += 1
        i_note, n_new_octave = get_next_note_index(i_note, n_new_octave, octave_turn)
        note, sum_stop = prepare_new_note(global_root_note, scale, i_note, n_new_octave, octave_turn)
        rising_motion.append(note)

        # Probabilistic insertion of {D#, F#, G#} in C major
        if color == 'white' and sum_stop in [2, 4, 5]:
            out_of_scale_note = get_out_of_scale_note(note)
            if out_of_scale_note is not None:
                rising_motion.append(out_of_scale_note)
                i_motion += 1
        i_motion += 1
    return rising_motion

def generate_scale(color, global_root_note, seq_length):
    motion_span = int(seq_length / 2)
    scale, octave_turn = get_scale_vars(color)
    rising_motion = generate_scale_melody(color, global_root_note, scale, octave_turn, motion_span)
    circle_motion = rising_motion[:-1] + rising_motion[::-1]
    if len(circle_motion) % 2 != 0:
        circle_motion += [circle_motion[int(len(circle_motion)/2)]]
    return circle_motion

def get_arpeggio_type(chord_type):
    if chord_type == 'minor':
        arpeggio_type = CONST.minor_arpeggio
    elif chord_type == 'major':
        arpeggio_type = CONST.major_arpeggio
    else:
        arpeggio_type = CONST.dimin_arpeggio
    return arpeggio_type

def build_arpeggio(root_note, chord_type, n_octaves):
    arpeggio_type = get_arpeggio_type(chord_type)
    n_notes = CONST.arp_oct_index[n_octaves - 1] + 1
    arpeggio = [root_note + arpeggio_type[n] for n in range(n_notes)]
    arpeggio = arpeggio[:-1] + arpeggio[::-1]
    return arpeggio

def get_arpeggio_vars(color):
    if color == 'black':
        adds = [2, 4, 9, 11] # Minor (2, 4, 9) + Diminished (11) shifts
        root_note = random_choice(adds, p=CONST.black_arp_probs)
        if root_note == 11:
            chord_type = 'diminished'
        else:
            chord_type = 'minor'
    else:
        adds = [0, 5, 7] # Major shifts
        root_note = random_choice(adds, p=CONST.white_arp_probs)
        chord_type = 'major'
    return root_note, chord_type

def generate_arpeggios(color, global_root_note, seq_length):
    arpeggios = list()
    while len(arpeggios) < seq_length:
        root_note, chord_type = get_arpeggio_vars(color)
        root_note += global_root_note
        n_octaves = random_choice([1, 2, 3], p=[1/3, 1/3, 1/3])
        arpeggio = build_arpeggio(root_note, chord_type, n_octaves)
        arpeggios.extend(arpeggio)
    if len(arpeggios) > seq_length:
        arpeggios = arpeggios[:seq_length]
    return arpeggios

def generate_circle_sheet(color, avg_shape_size, global_root_note, playfulness, structure=None, arp_ratio=1.0, seq_length=None):
    if seq_length is None:
        length = get_length('circle', avg_shape_size)
        seq_length = get_num_notes(length)

    shift = get_shift('circle', avg_shape_size)
    root_note = global_root_note + shift * 12
    keys_arp = generate_arpeggios(color, root_note, seq_length)
    keys_scale = generate_scale(color, root_note, seq_length)
    keys = combine_melodies(keys_arp, keys_scale, ratio=arp_ratio)
    lens, _ = generate_length_sequence('circle', avg_shape_size, seq_length, playfulness=playfulness, structure=structure)
    keys, lens = equalize(keys, lens)
    joins = [False] * len(keys)
    melody = (keys, lens, joins)
    circle_sheet = melody_to_sheet(melody)
    return circle_sheet
