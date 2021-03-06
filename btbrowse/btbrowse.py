#!/usr/bin/env python3

import config

from tkinter import *
import tkinter.ttk as ttk
from urllib.parse import urlparse, parse_qs, urlencode
from datetime import datetime, timedelta
import urllib.request
import os
import re
import sys
import time
import subprocess
import hashlib
import bencodepy
import base64
import codecs

gui_mode = 'DISPLAY' in os.environ

def main():
  
  # Prompt for torrent URL if not provided
  if len(sys.argv) < 2:

    # If there's a display, try a GUI popup
    if gui_mode:
      try:
        master = Tk()
        master.wm_title(config.app_name)
        Label(master, text='Torrent URL: ').grid(row=0)
        url_entry = Entry(master)
        url_entry.grid(row=0, column=1)
        Button(master, text='Open', command=master.quit).grid(row=2, column=0, sticky=W, pady=4)
        url_entry.focus_set()
        mainloop()
        url = url_entry.get()
        master.destroy()
      except:
        print('Torrent URL is required')
        return

    # Otherwise console prompt
    else:
      print(config.app_name + ': usage: ' + config.app_name + ' [options] torrent_url')
      return

  # URL is first arg
  else:
    url = sys.argv[1]
  
  if len(url):
      open_torrent_url(url)


def open_torrent_url(url):
  """Mount the specified torrent and open it in the file browser

  Keyword arguments:
  url -- url to download the torrent file, path of torrent in filesystem, or magnet url
  """

  url_parsed = urlparse(url)
  
  
  # Magnet
  if url_parsed.scheme == 'magnet':
    print('MAGNET', url)
    query_params = parse_qs(url_parsed.query)
    
    magnet_params = {}
    if 'tr' in query_params:
      magnet_params['tr'] = query_params['tr']
    
    if magnet_params:
      encoded_params = '&' + urlencode(magnet_params, doseq=True)
    else:
      encoded_params = ''
    
    # For each torrent in the magnet
    for param_name, param_data in query_params.items():
      if param_name[:2] != 'xt':
        continue
      
      xt_data = param_data[0]
      
      btih = re.search(r'^urn:btih:([0-9a-fA-F]{40}|[2-7A-Z]{32})$', xt_data)
      if btih is not None:
        btih = btih.group(1)
        
        # Hex encoded
        if (len(btih) == 40):
          btih = btih.lower()
          
        # Base32 encoded
        else:
          btih = base64.b32decode(btih).hex()
        
        open_torrent_btih(btih, 'magnet:?xt=' + xt_data + encoded_params)
    
    return
    
    
  # Download torrent from URL
  if len(url_parsed.scheme):
    print('URL', url)
    torrent_file = os.path.join(config.torrent_dir, hashlib.md5(url.encode('utf-8')).hexdigest()+'.torrent')
    urllib.request.urlretrieve(url, torrent_file)
    url = torrent_file
  
  
  # Open torrent in file system
  if os.path.isfile(url):
    print('FILE', url)
    
    # Calculate bittorrent info hash
    metadata = bencodepy.decode_from_file(url)
    hashcontents = bencodepy.encode(metadata[b'info'])
    digest = hashlib.sha1(hashcontents).digest()
    btih = digest.hex()
    
    open_torrent_btih(btih, url)
    return
  
  
  print('Torrent URL is not supported')
  
    

def open_torrent_btih(btih, url):
  """Mount the torrent by it's btih and open it in the file browser

  Keyword arguments:
  btih -- bittorrent info hash
  """
  
  mount_dir = os.path.join(config.torrent_dir, btih)

  if not os.path.isdir(mount_dir):

    os.mkdir(mount_dir)
    
    btfs_params = ['btfs']
    if (config.browse_only):
      btfs_params.append('-b')
    btfs_params.append(url)
    btfs_params.append(mount_dir)
    
    btfs_return_code = subprocess.call(btfs_params)

    if btfs_return_code:
      print('btfs error', btfs_return_code)
      return

  # Wait for metadata to download
  while not os.listdir(mount_dir):
    time.sleep(0.1)

    
  open_success = False
    
  if gui_mode:
    # Open in file browser
    open_return_code = subprocess.call(['xdg-open', mount_dir])
      
    if open_return_code == 0:
      open_success = True
    else:
      print('Error ' + open_return_code + ' opening file browser')
      
  else:
    # Console
    print('Mounted to ' + mount_dir)
    open_success = True


  if open_success:

    destroy_immediately = False

    # If there's a display, show progress screen
    if gui_mode:
      try:
        master = Tk()
        master.wm_title(config.app_name + ' ' + btih)
        Label(master, text='Downloading ' + btih).grid(row=0)
        
        #progress_bar = ttk.Progressbar(master, orient='horizontal', length=200, mode='determinate')
        #progress_bar.pack()

        Button(master, text='Self-destruct', command=master.quit).grid(row=2, column=0, sticky=W, pady=4)
        mainloop()
        master.destroy()
        destroy_immediately = True
      except:
        print('Error in progress GUI', sys.exc_info())

    # Keep the torrent for the specified number of hours
    if not destroy_immediately:
      print('Torrent will self-destruct at ' + '{:%H:%M}'.format( datetime.now() + timedelta(hours=config.hours_to_live) ))
      try:
        time.sleep(3600 * config.hours_to_live)
      except:
        print('Interrupted')


  print('Destructing torrent...')	
  
  # Self-destruct
  close_torrent_btih(btih)



def close_torrent_btih(btih):
  """Unmount the torrent

  Keyword arguments:
  btih -- bittorrent info hash
  """
  
  mount_dir = os.path.join(config.torrent_dir, btih)

  if os.path.isdir(mount_dir):
    subprocess.call(['fusermount', '-u', '-z', mount_dir])
    os.rmdir(mount_dir)


if __name__ == '__main__':
  main()
