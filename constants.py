from pickle import load, dump
from pandas import DataFrame, concat
from numpy import zeros, array, exp
from numpy.random import choice, randint, shuffle
from numpy.random import seed as np_seed

class Constants:
    def __init__(self):

        self.MIDI_DIR = 'midi_files/'
        self.AUDIO_DIR = 'audio_files/'
        self.PATH_DICTIONARY = 'note_dict/note_dict.pkl'
        self.SONG_DATA_DIR = 'song_data/'
        self.PICKLE_DIR = 'pickles/'
        self.SOUND_FONT_DIR = 'sound_fonts/'
        self.COMP_DIR = 'comps/'

        self.GLOBAL_SEED = None

        self.tick_label = 'Tick'
        self.key_label = 'Key'
        self.velocity_label = 'Velocity'
        self.note_label = 'Note'
        self.length_label = 'Length'
        self.join_label = 'Join'
        self.rest = 'R'
        self.scale_convention = 'major'

        self.resolution = 32 # Lowest level MIDI representation ( = PPQ )
        self.bpm = 20 # Quarter note per minute (assuming 4/4 time signature)
        self.melody_length = 100
        self.n_bars = 4
        self.velocity_range = (70, 110)

        self.rect_velocity_range = (100, 115)
        self.circle_velocity_range = (75, 100)
        self.triangle_velocity_range = (75, 115)

        self.uniform_lengths = True
        self.exclude_tuples = False
        self.lag = False

        self.arp_ratio = 0.7
        self.playfulness = 0.5

        self.circle_multiplier = 5
        self.triangle_multiplier = 3

        self.threshold_small = 1/3
        self.threshold_large = 2/3

        self.TICK_INDEX = 0
        self.KEY_INDEX  = 1
        self.VEL_INDEX  = 2

        self.minor_triad = [0, 3, 7]
        self.major_triad = [0, 4, 7]
        self.minor_seven = [0, 3, 7, 10]
        self.major_seven = [0, 4, 7, 11]

        self.middle_C = 48
        self.middle_A = 33
        self.piano_ceiling = 108

        self.whole = 1
        self.half = 2
        self.quarter = 4
        self.eighth = 8
        self.sixteenth = 16
        self.thirty_second = 32
        self.short_triplet = 12
        self.long_triplet = 6

        self.p_split_long_first = 0.7

        ''' Rectangle data '''

        # Minor convention -----------------------------------------------------
        self.p_rect_black_I = 0.25
        self.p_rect_black_IV_minor = 0.25
        self.p_rect_black_V_minor = 0.25
        self.p_rect_black_IV_major = 0.125
        self.p_rect_black_V_major = 0.125
        self.rect_black_chords = [[0, 'minor'], [5, 'minor'], [7, 'minor'], [5, 'major'], [7, 'major']]

        self.p_rect_white_III = 0.25
        self.p_rect_white_VI = 0.25
        self.p_rect_white_VII = 0.25
        self.p_rect_white_I = 0.125
        self.p_rect_white_II = 0.125
        self.rect_white_chords = [[3, 'major'], [8, 'major'], [10, 'major'], [0, 'minor'], [2, 'diminished']]
        # ---------------------------------------------------------------------

        # Major convention -----------------------------------------------------
        self.p_rect_black_VI = 0.25
        self.p_rect_black_II_minor = 0.25
        self.p_rect_black_III_minor = 0.25
        self.p_rect_black_II_major = 0.125
        self.p_rect_black_III_major = 0.125
        self.rect_black_chords = [[9, 'minor'], [2, 'minor'], [4, 'minor'], [2, 'major'], [4, 'major']]

        self.p_rect_white_I = 0.25
        self.p_rect_white_IV = 0.25
        self.p_rect_white_V = 0.25
        self.p_rect_white_VI = 0.125
        self.p_rect_white_VII = 0.125
        self.rect_white_chords = [[0, 'major'], [5, 'major'], [7, 'major'], [9, 'minor'], [11, 'diminished']]
        # ---------------------------------------------------------------------

        self.p_add_seventh = 0.5
        self.p_shift_seventh = 1/3 # Shift -1 octave!

        self.p_octave_shift_low_2 = 0.05
        self.p_octave_shift_low_1 = 0.15
        self.p_octave_shift_null = 0.6
        self.p_octave_shift_high_1 = 0.15
        self.p_octave_shift_high_2 = 0.05

        self.p_no_inversion = 0.4
        self.p_first_inversion = 0.4
        self.p_second_inversion = 0.2

        ''' Circle data '''

        self.major_scale = [0, 2, 2, 1, 2, 2, 2]
        self.minor_scale = [0, 2, 1, 2, 2, 1, 2]
        self.chromatics = [0, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1]
        self.minor_pentaton = [0, 3, 5, 7, 10, 12]
        self.major_pentaton = [0, 2, 4, 7, 10, 12]
        self.skip_probs = [0.2, 0.8]
        self.jump_probs = [0.55, 0.25, 0.1, 0.06, 0.04]
        self.insert_probs = [0.5, 0.5]
        self.p_shift_one = 0.1

        self.major_arpeggio = [0, 4, 7, 12, 16, 19, 24, 28, 31, 36]
        self.minor_arpeggio = [0, 3, 7, 12, 15, 19, 24, 27, 31, 36]
        self.dimin_arpeggio = [0, 3, 6, 12, 15, 18, 24, 27, 30, 36]
        self.arp_oct_index  = [3, 6, 9]
        self.white_arp_probs = [1/3, 1/3, 1/3]
        self.black_arp_probs = [2/7, 2/7, 2/7, 1/7]

        self.arpeggio_minor = [0, 3, 7, 12, 15, 19, 24]
        self.arpeggio_major = [0, 4, 7, 12, 16, 19, 24]

        ''' Triangle data '''

        self.diminished_scale = [2, 5, 8, 11, 14, 17, 20, 23]
        self.p_diminished = [1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8, 1/8]
        self.max_step_interval = 9

        self.third_white_up = [3, 3, 4, 3, 3, 4, 4]
        self.third_white_down = [4, 4, 3, 3, 4, 3, 3]
        self.third_black_up = [4, [5, 6], 3, 4, [4, 5, 7], 3, 5]
        self.third_black_down = [[1, 5], [3, 7], 3, 6, [5, 8], 3, 3]

        self.modes = [0, 1, 2, 3, 4, 5, 6]
        self.p_modes = [1/7, 1/7, 1/7, 1/7, 1/7, 1/7, 1/7]

        ''' Shapes '''

        self.shape_names = ['triangle', 'triangle', 'triangle', 'rectangle', 'rectangle', 'circle', 'circle', 'triangle']


    def get_rect_probs(self, color):
        rect_probs = list()
        if color == 'black':
            if self.scale_convention == 'minor':
                rect_probs.append(self.p_rect_black_I)
                rect_probs.append(self.p_rect_black_IV_minor)
                rect_probs.append(self.p_rect_black_V_minor)
                rect_probs.append(self.p_rect_black_IV_major)
                rect_probs.append(self.p_rect_black_V_major)
            else:
                rect_probs.append(self.p_rect_black_VI)
                rect_probs.append(self.p_rect_black_II_minor)
                rect_probs.append(self.p_rect_black_III_minor)
                rect_probs.append(self.p_rect_black_II_major)
                rect_probs.append(self.p_rect_black_III_major)
        elif color == 'white':
            if self.scale_convention == 'minor':
                rect_probs.append(self.p_rect_white_III)
                rect_probs.append(self.p_rect_white_VI)
                rect_probs.append(self.p_rect_white_VII)
                rect_probs.append(self.p_rect_white_I)
                rect_probs.append(self.p_rect_white_II)
            else:
                rect_probs.append(self.p_rect_white_I)
                rect_probs.append(self.p_rect_white_IV)
                rect_probs.append(self.p_rect_white_V)
                rect_probs.append(self.p_rect_white_VI)
                rect_probs.append(self.p_rect_white_VII)
        return rect_probs

    def get_rect_chords(self, color):
        if color == 'black':
            return self.rect_black_chords
        else:
            return self.rect_white_chords

    def get_shift_probs(self):
        shift_probs = list()
        shift_probs.append(self.p_octave_shift_low_2)
        shift_probs.append(self.p_octave_shift_low_1)
        shift_probs.append(self.p_octave_shift_null)
        shift_probs.append(self.p_octave_shift_high_1)
        shift_probs.append(self.p_octave_shift_high_2)
        return shift_probs

    def get_total_sum(self):
        # total_sum = (1/self.resolution) * 4 * self.n_bars
        # total_sum = 4 * self.n_bars
        total_sum = self.n_bars
        return int(total_sum)

    def set_global_seed(self, seed):
        self.GLOBAL_SEED = seed

    def set_bpm(self, bpm):
        self.bpm = int(bpm / 4)

CONST = Constants()
