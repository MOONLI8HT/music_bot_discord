
HELLO_MESSAGE = False


INFO_NAMES = {
  'info': 'Показывает информацию о командах',  
  'music': 'Воспроизводит музыку по ссылке',    
  'next': 'Воспроизведение следующую по счету мелодию',     
  'pause': 'Поставить на паузу',   
  'play': 'Продолжить воиспороизволдить',    
  'stop': 'Остановить проигрывание',   
  'join': 'Подключиться к каналу',      
  'leave': 'Отключиться от канала',     
  'add_music': 'Добавить музыку в конец плейлиста', 
  'clear_list': 'Очистить плейлист',
  'play_list': 'Показать плейлист',   
  'roll': 'Зарандомить число (/roll 0-100)'      
              }

YOUTUBE_DL_OPTIONS = {'format': 'bestaudio/best', 'compat_opts': '', 'postprocessors': [{'key': 'FFmpegExtractAudio', 'preferredcodec': 'mp3', 'preferredquality': '192',}],}

DEBUG = False 
