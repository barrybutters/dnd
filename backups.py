"""Atomic named backup copies to an explicitly selected destination folder."""
import os,shutil,uuid
from pathlib import Path
from datetime import datetime

def write_folder_backup(folder,raw):
    folder=Path(folder)
    if not folder.is_dir():raise ValueError('Choose an existing destination folder')
    if shutil.disk_usage(folder).free<len(raw)+1024*1024:raise ValueError('Not enough free space in the selected folder')
    name='Ember-Table-Backup-'+datetime.now().strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6]+'.zip'
    temporary=folder/(name+'.part')
    try:
        with temporary.open('xb') as target:target.write(raw);target.flush();os.fsync(target.fileno())
        os.replace(temporary,folder/name)
    finally:temporary.unlink(missing_ok=True)
    return {'name':name,'bytes':len(raw)}
