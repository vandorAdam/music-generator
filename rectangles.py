from constants import *
from utils import init_df, melody_to_sheet, random_choice, get_num_notes
from rhythm import generate_length_sequence, get_shift


def add_seventh(chord, chord_type):
    probs_add_seveth = [CONST.p_add_seventh, 1-CONST.p_add_seventh]
    add_seventh = random_choice([True, False], p=probs_add_seveth)
    if add_seventh:
        if chord_type == 'minor':
            chord += [chord[0] + 10]
        else:
            chord += [chord[0] + 11]
        probs_shift_seveth = [CONST.p_shift_seventh, 1-CONST.p_shift_seventh]
        shift_seventh = random_choice([True, False], p=probs_shift_seveth)
        if shift_seventh:
            chord[-1] -= 12
        return chord
    else:
        return chord

def invert_triad(chord):
    probs_invert = [CONST.p_no_inversion, CONST.p_first_inversion, CONST.p_second_inversion]
    inversions = ['Zero', 'First', 'Second']
    inversion = random_choice(inversions, p=probs_invert)
    if inversion == 'Zero':
        return chord
    elif inversion == 'First':
        chord[-1] -= 12
    elif inversion == 'Second':
        chord[-1] -= 12
        chord[-2] -= 12
    return chord

def build_triad(root_note, chord_type):
    chord =[root_note]
    if chord_type == 'minor':
        chord += [root_note + 3, root_note + 7]
    elif chord_type == 'major':
        chord += [root_note + 4, root_note + 7]
    elif chord_type == 'diminished':
        # Diminished
        chord += [root_note + 3, root_note + 6]
    return chord

def build_chord(root_note, chord_type):
    triad = build_triad(root_note, chord_type)
    triad = invert_triad(triad)
    chord = add_seventh(triad, chord_type)
    return chord

def shift_chord(chord):
    p_shifts = CONST.get_shift_probs()
    shifts = [-2, -1, 0, 1, 2]
    shift_rate = random_choice(shifts, p=p_shifts)
    if shift_rate != 0:
        chord = [c + shift_rate * 12  for c in chord]
    return chord

def generate_rect_melody(color, global_root_note, avg_shape_size, seq_length):
    shift = get_shift('rectangle', avg_shape_size)
    root_note = global_root_note + shift * 12
    probs_rect = CONST.get_rect_probs(color)
    rect_chords = CONST.get_rect_chords(color)
    chords = list()
    for i in range(seq_length):
        chord_indices = list(range(len(rect_chords)))
        chord_index = random_choice(chord_indices, p=probs_rect)
        chord_ = rect_chords[chord_index]
        root = chord_[0] + root_note
        chord_type = chord_[1]
        chord = build_chord(root, chord_type)
        chords.append(chord)
    return chords

def rect_data_to_sheet(chords, lengths):
    total_length = sum([len(chord) for chord in chords])
    df = init_df('sheet', n_rows=total_length)
    df_index = 0
    for chord, length in zip(chords, lengths):
        n_notes = len(chord)
        joins = [True] * (n_notes - 1) + [False]
        df.loc[df_index:df_index+n_notes-1, CONST.key_label] = chord
        df.loc[df_index:df_index+n_notes-1, CONST.join_label] = joins
        df.loc[df_index:df_index+n_notes-1, CONST.length_label] = length
        df_index += n_notes
    return df

def generate_rect_sheet(color, avg_shape_size, global_root_note, playfulness,  structure=None, seq_length=None):
    if seq_length is None:
        length = get_length('rectangle', avg_shape_size)
        seq_length = get_num_notes(length)
    lengths, _ = generate_length_sequence('rectangle', avg_shape_size, seq_length, playfulness=playfulness, structure=structure, extend_last=False)
    chords = generate_rect_melody(color, global_root_note, avg_shape_size, seq_length)
    sheet = rect_data_to_sheet(chords, lengths)
    return sheet
