from constants import *
from pygame.mixer import init, music
# from pygame import time, error, get_error
from midi import write_midifile, Pattern, Track, SetTempoEvent, EndOfTrackEvent, NoteOnEvent, NoteOffEvent
from midi2audio import FluidSynth

def root_int_to_str(global_root_note):
    dictionary = load_note_dictionary()
    global_root_note_str = dictionary.loc[global_root_note][0]
    return global_root_note_str

def get_global_root_note(root_note=None):
    if root_note is not None:
        return root_note
    probs = [1/12] * 12
    shifts = list(range(12))
    # shift = choice(shifts, p=probs)
    shift = random_choice(shifts, p=probs, seed=CONST.GLOBAL_SEED)
    return CONST.middle_A + shift

def set_bpm(bpm):
    return int(bpm / 4)

# def play_midi(path, title, midi_dir=True):
#     if midi_dir:
#         path = CONST.MIDI_DIR + path
#     freq = 44100    # audio CD quality
#     bitsize = -16   # unsigned 16 bit
#     channels = 2    # 1 is mono, 2 is stereo
#     buffer = 1024    # number of samples
#     init(freq, bitsize, channels, buffer)
#     music.set_volume(1.0)
#     try:
#         clock = time.Clock()
#         try:
#             music.load(path)
#         except error:
#             print ("File %s not found! (%s)" % (music_file, get_error()))
#             return
#         print('Playing %s...'%(title))
#         music.play()
#         while music.get_busy():
#             clock.tick(30)
#     except KeyboardInterrupt:
#         music.fadeout(1000)
#         music.stop()
#         raise SystemExit

def save_midi(path, midi_pattern, midi_dir=True):
    if midi_dir:
        path = CONST.MIDI_DIR + path
    write_midifile(path, midi_pattern)

def create_midi(midi_dfs, output_file, bpm=CONST.bpm, resolution=CONST.resolution, midi_dir=True, return_pattern=False):

    # Load note dict
    dictionary = load_note_dictionary(CONST.PATH_DICTIONARY)

    # Initialize highest level pattern
    pattern = Pattern(resolution=int(resolution))
    tempo_track = Track()
    tempo = SetTempoEvent()
    tempo.set_bpm(bpm)
    tempo_track.append(tempo)
    eot = EndOfTrackEvent(tick=1)
    tempo_track.append(eot)
    pattern.append(tempo_track)

    for midi_df in midi_dfs:
        midi_data = midi_df.values
        key_flags = [False] * len(dictionary)
        track = Track()
        pattern.append(track)
        for event in midi_data:
            if key_flags[event[CONST.KEY_INDEX]]:
                off = NoteOffEvent(tick=int(event[CONST.TICK_INDEX]), pitch=event[CONST.KEY_INDEX])
                track.append(off)
                key_flags[event[CONST.KEY_INDEX]] = False
            else:
                on = NoteOnEvent(tick=int(event[CONST.TICK_INDEX]), velocity=event[CONST.VEL_INDEX], pitch=event[CONST.KEY_INDEX])
                track.append(on)
                key_flags[event[CONST.KEY_INDEX]] = True
        eot = EndOfTrackEvent(tick=1)
        track.append(eot)

    save_midi(output_file, pattern, midi_dir=midi_dir)

    if return_pattern:
        return pattern

def midi_to_audio(path_midi, path_audio, soundfont='sound_font.sf2'):
    try:
        fs = FluidSynth(soundfont)
        fs.midi_to_audio(path_midi, path_audio)
    except:
        print('Unable to create audio file.')

def str2bool(v, default=False):
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        return default

def load_note_dictionary(path=CONST.PATH_DICTIONARY):
    with open(path, 'rb') as f:
        dictionary = load(f)
    return dictionary

def get_section(df, i_start):
    i = i_start
    while df.loc[i][CONST.join_label]:
        i += 1
    return df.loc[i_start:i], i+1

def init_df(df_type='midi', n_rows=1):
    df = DataFrame(zeros((n_rows, 3), dtype=int))
    if df_type == 'midi':
        df.columns = [CONST.tick_label, CONST.key_label, CONST.velocity_label]
    elif df_type == 'sheet':
        df.columns = [CONST.key_label, CONST.length_label, CONST.join_label]
    return df

def fix_combined_index(df_sheet_combined):
    df_sheet_combined.index = list(range(len(df_sheet_combined)))
    df_sheet_combined = df_sheet_combined.drop([0])
    df_sheet_combined.index = list(range(len(df_sheet_combined)))
    return df_sheet_combined

def catch_pause(key):
    if key == CONST.rest:
        return 0
    else:
        return key

def catch_key_overflow(key):
    if key >= CONST.piano_ceiling:
        while key >= CONST.piano_ceiling:
            key -= 12
    elif key < 0:
        while key < 0:
            key += 12
    return key

def sheets_to_midi(df_sheets, resolution=CONST.resolution):

    midi_dfs = list()

    for df_data in df_sheets:

        shape = df_data[0]
        df_sheet = df_data[1]

        if shape == 'rectangle':
            velocity_range = CONST.rect_velocity_range
        elif shape == 'circle':
            velocity_range = CONST.circle_velocity_range
        else:
            velocity_range = CONST.triangle_velocity_range

        df_midi = init_df(df_type='midi')
        i_midi = 0
        i_sheet = 0

        while i_sheet < len(df_sheet):

            # Single note
            if not df_sheet.iloc[i_sheet][CONST.join_label]:

                # Note On Event
                tick = 0
                key = catch_pause(df_sheet.iloc[i_sheet][CONST.key_label])
                key = catch_key_overflow(key)
                velocity = randint(velocity_range[0], velocity_range[1]) if key != 0 else 0
                df_midi.loc[i_midi] = [tick, key, velocity]

                # Note Off Event
                tick = resolution / df_sheet.iloc[i_sheet][CONST.length_label]
                key = catch_pause(df_sheet.iloc[i_sheet][CONST.key_label])
                key = catch_key_overflow(key)
                velocity = 0
                df_midi.loc[i_midi+1] = [tick, key, velocity]

                i_midi += 2
                i_sheet += 1

            # Simultanious notes
            else:
                section, i_next = get_section(df_sheet, i_sheet)

                # Note On Events
                for i, note in section.iterrows():
                    tick = 0
                    key = catch_pause(note[CONST.key_label])
                    key = catch_key_overflow(key)
                    velocity = randint(velocity_range[0], velocity_range[1]) if key != 0 else 0
                    df_midi.loc[i_midi] = [tick, key, velocity]

                    i_midi += 1

                # Note Off Events
                flag_off = False
                for i, note in section.iterrows():
                    if not flag_off:
                        tick = resolution / note[CONST.length_label]
                        flag_off = True
                    else:
                        tick = 0
                    key = catch_pause(note[CONST.key_label])
                    key = catch_key_overflow(key)
                    velocity = 0
                    df_midi.loc[i_midi] = [tick, key, velocity]
                    i_midi += 1
                i_sheet = i_next

        df_midi = df_midi.astype(int)
        midi_dfs.append(df_midi)

    return midi_dfs

def melody_to_sheet(melody, add_end_note=True):
    keys, lens, joins = melody
    df_sheet = DataFrame(zeros((len(keys), 3), dtype=int))
    df_sheet.columns = [CONST.key_label, CONST.length_label, CONST.join_label]
    df_sheet[CONST.key_label] = keys
    df_sheet[CONST.length_label] = lens
    df_sheet[CONST.join_label] = joins
    if add_end_note:
        df_sheet.loc[len(df_sheet)] = [CONST.rest, 4, False]
    return df_sheet

# def get_next_sum(df, i_start, accumulated_sum):
#     section, i_next = get_section(df, i_start)
#     new_sum = 1 / section[-1:][CONST.length_label].values[0] + accumulated_sum
#     return new_sum, i_next, section
#
# def combine_sections(section_A, section_B):
#     combined_sections = concat([section_A, section_B])
#     L = len(combined_sections) - 1
#     combined_sections[CONST.join_label] = [True] * L + [False]
#     return combined_sections
#
# def catch_up_section(df_sheet_combined, df_X, df_Y, i_X, i_Y, sum_X, sum_Y, section_X, section_Y, i_glob):
#
#     df_sheet_combined_copy = df_sheet_combined.copy()
#     df_X_copy = df_X.copy()
#     df_Y_copy = df_Y.copy()
#     section_X_copy = section_X.copy()
#     section_Y_copy = section_Y.copy()
#     i_X_copy, i_Y_copy, sum_X_copy, sum_Y_copy, i_glob_copy = i_X, i_Y, sum_X, sum_Y, i_glob
#     concat_flag = False
#
#     while sum_X_copy <= sum_Y_copy:
#
#         if not concat_flag:
#             combined_sections = combine_sections(section_Y_copy, section_X_copy)
#             df_sheet_combined_copy = concat([df_sheet_combined_copy, combined_sections])
#             sum_X_copy, i_X_copy, section_X_copy = get_next_sum(df_X_copy, i_X_copy, sum_X_copy)
#             concat_flag = True
#             i_glob_copy = max(i_Y_copy, i_X_copy)
#
#         else:
#             df_sheet_combined_copy = concat([df_sheet_combined_copy, section_X_copy])
#             sum_X_copy, i_X_copy, section_X_copy = get_next_sum(df_X_copy, i_X_copy, sum_X_copy)
#             i_glob_copy = max(i_Y_copy, i_X_copy)
#
#         if sum_X_copy == sum_Y_copy:
#             df_sheet_combined_copy = concat([df_sheet_combined_copy, section_X_copy])
#             sum_X_copy, i_X_copy, section_X_copy = get_next_sum(df_X_copy, i_X_copy, sum_X_copy)
#             sum_Y_copy, i_Y_copy, section_Y_copy = get_next_sum(df_Y_copy, i_Y_copy, sum_Y_copy)
#             i_glob_copy = max(i_X_copy, i_Y_copy)
#             break
#
#     return df_sheet_combined_copy, df_X_copy, df_Y_copy, i_X_copy, i_Y_copy, sum_X_copy, sum_Y_copy, section_X_copy, section_Y_copy, i_glob_copy
#
# def combine_sheets(sheet_A, sheet_B):
#
#     sum_A, sum_B, i_A, i_B, i_glob = 0, 0, 0, 0, 0
#     max_num_notes = max(len(sheet_A), len(sheet_B))
#     df_sheet_combined = init_df(df_type='sheet')
#
#     sum_A, i_A, section_A = get_next_sum(sheet_A, i_A, sum_A)
#     sum_B, i_B, section_B = get_next_sum(sheet_B, i_B, sum_B)
#
#     while i_glob < max_num_notes:
#
#         if sum_B == sum_A:
#             combined_sections = combine_sections(section_A, section_B)
#             df_sheet_combined = concat([df_sheet_combined, combined_sections])
#             sum_A, i_A, section_A = get_next_sum(sheet_A, i_A, sum_A)
#             sum_B, i_B, section_B = get_next_sum(sheet_B, i_B, sum_B)
#             i_glob = max(i_A, i_B)
#
#         elif sum_B < sum_A:
#             df_sheet_combined, sheet_B, sheet_A, i_B, i_A, sum_B, sum_A, section_B, section_A, i_glob = catch_up_section(df_sheet_combined, sheet_B, sheet_A, i_B, i_A, sum_B, sum_A, section_B, section_A, i_glob)
#             # break
#
#         elif sum_A < sum_B:
#             df_sheet_combined, sheet_A, sheet_B, i_A, i_B, sum_A, sum_B, section_A, section_B, i_glob = catch_up_section(df_sheet_combined, sheet_A, sheet_B, i_A, i_B, sum_A, sum_B, section_A, section_B, i_glob)
#             # break
#
#     df_sheet_combined = fix_combined_index(df_sheet_combined)
#
#     return df_sheet_combined

def get_time(sheet):
    t = sum([1/denom for denom in sheet[CONST.length_label]])
    return t

def combine_melodies(keys_1, keys_2, ratio=0.5):

    '''
        ratio applies to keys_1.
        e.g. ratio = 0.3 --> keys = keys_1 * 0.3 + keys_2 * 0.7

        Note: this is super random, need to come up with a way to replace
        musical phrases instead of single notes.

    '''

    keys_1, keys_2 = equalize_keys(keys_1, keys_2)
    n_keys = len(keys_1)
    mask_size = int((1 - ratio) * n_keys)
    key_index = list(range(n_keys))
    shuffle(key_index)
    mask_index = key_index[:mask_size]
    combined = [keys_2[i] if i in mask_index else keys_1[i] for i in range(n_keys)]
    return combined

def random_choice(items, p, seed=CONST.GLOBAL_SEED):
    if seed is not None:
        np_seed(seed)
    chosen = choice(items, p=p)
    return chosen

def get_num_notes(length):
    total_sum = CONST.get_total_sum()
    inverse_length = 1 / length
    n_notes = int(total_sum / inverse_length)
    return n_notes

def equalize(keys, lens):
    if len(keys) == len(lens):
        return keys, lens
    else:
        if len(lens) > len(keys):
            lens = lens[:len(keys)]
        else:
            keys = keys[:len(lens)]
        return keys, lens

def equalize_keys(k1, k2):
    if len(k1) > len(k2):
        k1 = k1[:len(k2)]
    elif len(k2) > len(k1):
        k2 = k2[:len(k1)]
    return k1, k2
