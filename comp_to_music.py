from constants import *
from json_to_data import json_to_data
from generate_sheets import *
from utils import create_midi, midi_to_audio, sheets_to_midi, get_global_root_note
from argparse import ArgumentParser
import sys

def comp_to_music(json_file, global_root, bpm, midi_file=None, soundfont='full_grand_piano'):

    title = json_file.split('.')[0]
    path_comp = '%s%s'%(CONST.COMP_DIR, json_file)

    comp = json_to_data(path_comp)

    rectangle_data = comp['rectangle']
    triangle_data = comp['triangle']
    circle_data = comp['circle']

    sheets = list()

    if triangle_data:
        sheet_triangle = merge_melodies('triangle', triangle_data, global_root)
        sheets.append(['triangle', sheet_triangle])

    if circle_data:
        sheet_cirlce = merge_melodies('circle', circle_data, global_root)
        sheets.append(['circle', sheet_cirlce])

    if rectangle_data:
        sheet_rect = merge_chords(rectangle_data, global_root)
        sheets.append(['rectangle', sheet_rect])

    song_data = sheets_to_midi(sheets)

    if midi_file is None:
        midi_file = 'temp_midi.mid'

    create_midi(song_data, midi_file, bpm=int(bpm/4))

    output_audio_file = '%s.mp3'%(title)
    path_midi = '%s%s'%(CONST.MIDI_DIR, midi_file)
    path_audio = '%s%s'%(CONST.AUDIO_DIR, output_audio_file)
    soundfont = '%s%s.sf2'%(CONST.SOUND_FONT_DIR, soundfont)
    midi_to_audio(path_midi, path_audio, soundfont)

if __name__ == '__main__':

    parser = ArgumentParser('')
    parser.add_argument('comp', nargs='?', type=str, default=None)
    parser.add_argument('--seed', type=int, default=None)
    parser.add_argument('--root', type=int, default=None)
    parser.add_argument('--bpm', type=int, default=120)
    args = parser.parse_args()

    CONST.set_global_seed(args.seed)

    if len(sys.argv) < 2:
        print('Usage: python comp_to_music.py <comp.json> [--seed] [--bpm] [--root]')
        sys.exit()

    bpm = args.bpm
    global_root = get_global_root_note(args.root)
    json_file = args.comp

    comp_to_music(json_file, global_root, bpm)
