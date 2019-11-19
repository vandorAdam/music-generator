# from constants import *
from argparse import ArgumentParser
from json_to_midi import json_to_midi
from utils import get_global_root_note, root_int_to_str, str2bool, play_midi, midi_to_audio
from constants import *

parser = ArgumentParser('')
parser.add_argument('--play', type=str2bool, default=False)
parser.add_argument('--mp3', type=str2bool, default=False, help='Export to mp3.')
parser.add_argument('--seed', type=int, default=None)
args = parser.parse_args()

bpm = 20
CONST.set_global_seed(args.seed)
global_root = get_global_root_note()

title = '1'
soundfont = 'full_grand_piano'
midi_file = '%s.mid'%(title)

json = 'comps/comp-20191119-133148.json'

midi_file = json_to_midi(json, global_root, bpm)

if __name__ == '__main__':

    title = '%s_in_%s'%(title, root_int_to_str(global_root))

    if args.mp3:
        output_audio_file = '%s_%s.mp3'%(title, soundfont)
        path_midi = '%s%s'%(CONST.MIDI_DIR, midi_file)
        path_audio = '%s%s'%(CONST.AUDIO_DIR, output_audio_file)
        soundfont = '%s%s.sf2'%(CONST.SOUND_FONT_DIR, soundfont)
        midi_to_audio(path_midi, path_audio, soundfont)

    if args.play:
        play_midi(midi_file, title)
