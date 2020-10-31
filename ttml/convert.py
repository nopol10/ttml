#!/usr/bin/python
# -*- coding: utf-8 -*-
'''

convert.py
on-three
Friday, April 18th 2014

Convert an (NHK specific?) .ttml file to a more usable format (.ass or .srt)

Currently only an .ass is dumped. .Srt is lacking

Example of the NHK format is below. It might be very unique, so this code
is probably of use to no one but myself.

<cuepoints x="170" y="450" font="ＭＳ ゴシック,Osaka−等幅,ヒラギノ角ゴ ProW3,Osaka" color="0xffffff" size="36" underline="false" bold="false" italic="false" ruby="false">
<cuepoint name="1" time="2.967"/>
<cuepoint name="2" time="3">
<subtitle id="201" x="210" y="450" xx="210" yy="560" background="0x000000" opacity="0.5" lang="jpn" letterspacing="4" substitution_string="♪" gaiji_pattern="000000000000000000000000F000000FFF00001FFFF00003FFF300003FE0300003800300003000300003007F000033FFF00003FFFF00003FF8300003C00300003000300003000300003000300003000300003000300003000300003000300003000300003000700003001F00003003F0000F007F0003F00FE0007E00FE000FE01FC001FC01F8001FC00F0003F80060003F00000001E00000000C0000000000000000" gaiji_width="36" gaiji_height="36" width="44" height="40">
<![CDATA[　]]>
</subtitle>
<subtitle id="202" x="254" y="450" xx="254" yy="560" background="0x000000" opacity="0.5" lang="jpn" letterspacing="4" width="67" height="40">
<![CDATA[｢お]]>


'''
from __future__ import print_function
from datetime import datetime
from bs4 import BeautifulSoup
import re
import argparse
import os
import codecs
import time
import datetime
import math
import glob

def get_ext(filename):
  # Get extension to normal file
  f, e = os.path.splitext(filename)
  return e.lower()

# Input: string of the format "seconds.milliseconds" (without quotations)
def to_srt_time(seconds_ms):
  '''convert strictly seconds string (may have fractional part)
    to a standard .srt file time: 00:00:33,381 --> 00:00:36,384
  '''
  split_time = seconds_ms.split('.')
  sec = int(split_time[0])
  milliseconds = int(split_time[1] if len(split_time) >= 2 else '0')

  days = math.floor(sec / 86400)
  sec -= 86400 * days

  hrs = math.floor(sec / 3600)
  sec -= 3600 * hrs

  mins = math.floor(sec / 60)
  sec -= 60 * mins

  return u'{h:02d}:{m:02d}:{s:02d},{ms:03d}'.format(h=hrs, m=mins, s=sec, ms=milliseconds)

def to_ass_time(seconds_ms):
  # convert strictly seconds string (may have fractional part)
  #  to a standard .ass file time: 0:00:15.333,0:00:20.634
  
  split_time = seconds_ms.split('.')
  sec = int(split_time[0])
  milliseconds = int(split_time[1] if len(split_time) >= 2 else '0')

  days = math.floor(sec / 86400)
  sec -= 86400*days

  hrs = math.floor(sec / 3600)
  sec -= 3600*hrs

  mins = math.floor(sec / 60)
  sec -= 60*mins

  return u'{h:01d}:{m:02d}:{s:02d}.{ms:02d}'.format(h=hrs, m=mins, s=sec, ms=milliseconds)
  

class Style(object):
  def __init__(self):
    self.color = 0xffffff
    self.size = 36
    self.underline = False
    self.bold = False
    self.italic = False
    self.ruby = False
    self.font = 'ＭＳ ゴシック,Osaka−等幅,ヒラギノ角ゴ ProW3,Osaka'
    self.x = 170
    self.y = 450

class Scaling(object):
  # Describe scaling from one screen resolution to another
  def __init__(self, initial_w, initial_h, final_w, final_h):
    self.iw = initial_w
    self.ih = initial_h
    self.fw = final_w
    self.fh = final_h

  def scale(self, x, y):
    # Scale given x,y from inital to final screen coordinates 
    scale_w = float(self.fw)/float(self.iw)
    scale_h = float(self.fh)/float(self.ih)
    return (int(float(x)*scale_w), int(float(y)*scale_h))

  def __call__(self, x, y):
    return self.scale(x,y)

class Subtitle(object):
  # Encapsultate a given subtitle text and its format 
  def __init__(self, text, x=0, y=0, style=None):
    pass

def ConvertToAss(content, outfile_name, scaling):
  # Convert to more flexible .ass format.
  # More appropriate for these subs which have furigana, color etc

  outfile = codecs.open(outfile_name,'w',encoding='utf8')
  soup = BeautifulSoup(content, features="xml")

  info = u'''[Script Info]
  Title: {title}
  ScriptType: v4.00+
  WrapStyle: 0
  PlayResX: {width}
  PlayResY: {height}
  ScaledBorderAndShadow: yes
  Video Aspect Ratio: 0
  Video Zoom: 6
  Video Position: 0
  '''.format(title=outfile_name, width=scaling.fw, height=scaling.fh)
  print(info, file=outfile)

  #gonna leave these styles in place
  #TODO: draw them out of the file
  styles = u'''[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,MS UI Gothic,24,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,1,10,10,10,0
Style: Box,MS UI Gothic,24,&HFFFFFFFF,&H000000FF,&H00FFFFFF,&H00FFFFFF,0,0,0,0,100,100,0,0,1,2,2,2,10,10,10,0
Style: Rubi,MS UI Gothic,14,&H00FFFFFF,&H000000FF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,2,2,1,10,10,10,0
'''
  print(styles, file=outfile)

  events='''[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
  print(events, file=outfile)
  
#  
#  subsequent lines should be of form:
#  Dialogue: 0,0:02:12.78,0:02:15.78,Default,,0000,0000,0000,,{\pos(580,1020)}＜世はグルメ時代＞\N
#  Dialogue: 0,0:02:15.78,0:02:18.78,Default,,0000,0000,0000,,{\pos(420,1020)}＜食の探求者 美食屋たちは・\N
#  Dialogue: 0,0:02:18.78,0:02:22.79,Default,,0000,0000,0000,,{\pos(420,1020)}あまたの食材を追い求める＞\N
#  Dialogue: 0,0:02:22.79,0:02:28.79,Default,,0000,0000,0000,,{\pos(420,840)}＜そして この世の食材の頂点\N
#  Dialogue: 0,0:02:22.79,0:02:28.79,Rubi,,0000,0000,0000,,{\pos(500,900)}ゴッド\N
#  
  cuepoints = soup.cuepoints
  captions = cuepoints.find_all('cuepoint')

  for i, caption in enumerate(captions[:-1]):
    #we need next caption to interpret the display time
    next_caption_time = captions[i+1]['time']
    #print caption.time
    subtitles = caption.find_all('subtitle')
    if not subtitles: continue

    #.ass time display
    #00:00:33,381 --> 00:00:36,384
    start_time_s = to_ass_time(caption['time'])
    end_time_s = to_ass_time(next_caption_time)
    #print(u'{s} --> {e}'.format(s=start_time_s, e=end_time_s), file=outfile)
    
    #form caption text from 'subtitle' entries
    caption_text = u''
    for s in subtitles:
      blurb= s.contents[0].strip()
      #this subtitle may be a "gaiji" (actually DRCS) character. If so we'll just use the
      #provided substitution string
      blurb = s.get('substitution_string', blurb)
      
      x, y = scaling(s['xx'],s['yy'])
      style = 'Default'
      if s.get('ruby', u'false') != u'false':
        style = 'Rubi'
      # color=s.get('color',u'0xffffff')
      # background=s['background']
      # opacity=s['opacity']
      
      dialog = u'Dialogue: 0,{start},{end},{style},,0000,0000,0000,,{{\pos({x},{y})}}{blurb}'.format(
      start=start_time_s,
      end=end_time_s,
      style=style,
      x=x,
      y=y,
      blurb=blurb
      )
      print(dialog, file=outfile)
 #     '''
 #     print (u'{x},{y},{color},{background},{opacity},{style}-->{text}'.format(x=s['x'],
 #       y=s['y'], 
 #       color=s.get('color',u'0xffffff'),
 #       background=s['background'],
 #       opacity=s['opacity'],
 #       ruby=s.get('ruby', u'false'),
 #       text=blurb,), file=outfile)
 #     '''
  
def ConvertToSrt(content, outfile_name, scaling):
  '''Convert an NHK .ttml input file (contents string) to srt
  :param infile: string contents of input .ttml file 
  :type infile: str
  '''
  outfile = codecs.open(outfile_name,'w',encoding='utf8')
  soup = BeautifulSoup(content, features="xml")

  cuepoints = soup.cuepoints
  captions = cuepoints.find_all('cuepoint')

  caption_id = 1
  for i, caption in enumerate(captions[:-1]):
    #we need next caption to interpret the display time
    next_caption_time = captions[i+1]['time']
    #print caption.time
    subtitles = caption.find_all('subtitle')
    if not subtitles: continue

    #each .srt entry is designated by a identifier
    print(u'{id}'.format(id=caption_id), file=outfile)
    caption_id += 1

    #.ass time display
    #00:00:33,381 --> 00:00:36,384
    start_time_s = to_srt_time(caption['time'])
    end_time_s = to_srt_time(next_caption_time)
    print(u'{s} --> {e}'.format(s=start_time_s, e=end_time_s), file=outfile)
    
    #form caption text from 'subtitle' entries
    for s in subtitles:
      blurb= s.contents[0].strip()
      #this subtitle may be a "gaiji" (actually DRCS) character. If so we'll just use the
      #provided substitution string
      blurb = s.get('substitution_string', blurb)
      
      if s.get('ruby', u'false') == u'false':
        print(blurb, file=outfile)
      else:
        pass

    print(u'\n', file=outfile)

#'''
#Map output filetype extensions to output file converters
#'''
SUPPORTED_OUTPUT_FILETYPES = {
  '.ass' : ConvertToAss,
  '.srt' : ConvertToSrt,
}

def parse_file(infile, user_outfile=None, extension='srt'):
  if user_outfile:
    outfile = user_outfile
  else:
    outfile = '.'.join(infile.split('.')[0:-1]) + '.' + extension

  if get_ext(outfile) not in SUPPORTED_OUTPUT_FILETYPES:
    print('Sorry, unsupported file extension.')
    return -1

  ext = get_ext(outfile)
  conversion_impl = SUPPORTED_OUTPUT_FILETYPES[ext]

  content_file = open(infile,'r',encoding='utf8')
  content = content_file.read()
  scaling = Scaling(1600, 900, 640, 360)
  return conversion_impl(content, outfile, scaling)


def main():
  parser = argparse.ArgumentParser(description='Convert (NHK?) .ttml closed caption file to another format.')
  parser.add_argument('infile', help='Input NHK .ttml source file.', type=str)
  parser.add_argument('-o', '--outfile', help='Output filename with extension. If supported extenstion is not present (.ass or .srt) a .srt file using input argument filename will be generated.', type=str, default=None)
  parser.add_argument('-e', '--extension', help='Extension of the generated file. Only for use with --folder. (srt, ass)', type=str, default='srt')
  parser.add_argument('-f', '--folder', help='When set, infile is treated as a folder and all ttml files inside will be converted', action='store_true', default=None)
  args = parser.parse_args()

  if args.folder:
    extension = args.extension
    if '.' + extension not in SUPPORTED_OUTPUT_FILETYPES:
      print('Sorry, unsupported file extension.')
      return -1
    files = glob.glob(args.infile + '/*.ttml')
    print("Converting "+str(len(files))+ " ttml files")
    for file in files:
      parse_file(file, None, extension)
  else:
    parse_file(args.infile, args.outfile)
  
  print('Done!')

if __name__ == "__main__":
  main()
