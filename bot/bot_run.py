import discord
from discord.ext import commands
import yt_dlp
import os, sqlite3, random, time, shutil
from mutagen.mp3 import MP3
import config
from config import YOUTUBE_DL_OPTIONS as ydl_opts

        
bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())

def str_list(list_of_obj):
    result = f'Плейлист(песен - {len(list_of_obj)}):'
    for f, s in enumerate(list_of_obj[:10]):
        result += f'\n\t{f} - {s[:s.rfind("[")]}'
    return result
        
@bot.event
async def on_ready(): #старт бота
    global my_list
    print(f"Bot {bot.user} is ready")
    global base, cur 
    base = sqlite3.connect("BOT.db")
    cur = base.cursor()
    if base: print("DataBase connected!")
    
    my_list = os.listdir('./play_list')
    print(type(my_list))
    
@bot.event
async def on_member_join(member): #если кто то зашел на сервер
    if config.HELLO_MESSAGE:
        await member.send(f'{member.mention} Приветствую на сервере \n Просмотр команд: /info')
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'основной':
            await bot.get_channel(ch.id).send(f"{member.name} зашел на сервер! ")
            
@bot.event
async def on_member_remove(member): #если кто то покинул сервер
    for ch in bot.get_guild(member.guild.id).channels:
        if ch.name == 'основной':
            await bot.get_channel(ch.id).send(f"{member.mention} покинул сервер!")

@bot.event()
async def on_message(ctx):
    pass

    
@bot.command()   
async def join(ctx): #Войти в канал
    if config.DEBUG: print('[START] join')
    
    try:
        if config.DEBUG: print('[IN FUNCTION] voice connecting') #DEBUG COMAND 
        
        voicechannel = ctx.author.voice.channel
        await voicechannel.connect(timeout=6000)

    except PermissionError:
        await ctx.send("Ошибка подключения")
    except Exception as e:
        print('[EXCEPTION]', e)
        
    if config.DEBUG: print('[END] join')

@bot.command()
async def add_music(ctx, url: str):#Добавить музыку в плейлист
    if config.DEBUG: print('[START] add_music')
    
    global my_list, ydl_opts
    try:
        
        if config.DEBUG: print('[IN FUNCTION] Start download music') #DEBUG COMAND
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl: ydl.download([url]) 

        if config.DEBUG: print('[IN FUNCTION] Try file transfer') #DEBUG COMAND
            
        for melody in os.listdir('./'):                                        
            if melody.endswith(".mp3") and not melody.endswith("song.mp3"):                    
                my_list.append(melody)            
                shutil.move('./' + my_list[-1], './play_list/'+ my_list[-1])  
                                   
    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        await ctx.send("Неправильная ссылка")
        print('[EXCEPTION]', e)
        
    await ctx.send("Мелодия добавлена")      
    
    if config.DEBUG: print('[END] add_music')


@bot.command()
async def music(ctx, url: str='', repeat=False):#Воспроизвести музыку из плейлиста, так же добавить по ссылке
    if config.DEBUG: print('[START] music') #DEBUG COMAND
    global my_list, ydl_opts
    try:
    
        if url != '':
            if config.DEBUG: print('[IN FUNCTION] start adding new music files') #DEBUG COMAND  
            await add_music(ctx, url)
            
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)  
        if not voice: await join(ctx)                                              
        if my_list != ():
            
            if config.DEBUG: print('[IN FUNCTION] voice check') #DEBUG COMAND
            voice = discord.utils.get(bot.voice_clients, channel=ctx.message.author.voice.channel)    
                
            if config.DEBUG: print('[IN FUNCTION] chek now play!') #DEBUG COMAND
            try: voice.stop()  
            except Exception as e:
                if config.DEBUG: print(repr(e)) #ERROR SEND
            await ctx.send("Cейчас играет: {}".format(my_list[0][:my_list[0].rfind("[")]))
            
            if config.DEBUG: print('[IN FUNCTION] delete old song.mp3') #DEBUG COMAND                
            if os.path.isfile('song.mp3'):
                os.remove('song.mp3')                   
                
            if config.DEBUG: print('[IN FUNCTION] create new song.mp3') #DEBUG COMAND               
            shutil.move('./play_list/' + my_list[0], './' )
            os.rename(my_list[0], 'song.mp3')
            
            
            if config.DEBUG: print('[IN FUNCTION] start playing') #DEBUG COMAND                
            voice = discord.utils.get(bot.voice_clients, channel=ctx.message.author.voice.channel)  
            audio = MP3('song.mp3')
            voice.play(discord.FFmpegPCMAudio('song.mp3'))  
            length = audio.info.length
            lap(ctx, length)    
            if config.DEBUG: print('[IN FUNCTION] update play_list') #DEBUG COMAND               
            my_list.pop(0)
        else: 
            await ctx.send("Плейлист пустой")
                    
        if config.DEBUG: print('[IN FUNCTION] Try to do next lap') #DEBUG COMAND
        
    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e)
                   
    if config.DEBUG: print('[END] music')  #DEBUG COMAND  

@bot.command()
async def lap(ctx, length):
    time.sleep(length + 5)
    try:
        if os.path.isfile('song.mp3'):
            os.remove('song.mp3')
        await music(ctx)  
    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e)    

@bot.command()
async def play_list(ctx): #Распечатать Плейлист
    if config.DEBUG: print('[START] play_list')  #DEBUG COMAND
    
    global my_list
    try:

        await ctx.send(str_list(my_list))
        
    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e) 

    if config.DEBUG: print('[END] play_list')  #DEBUG COMAND
    
@bot.command()
async def next(ctx):
    global my_list
    try:
        if config.DEBUG: print('[START] next')  #DEBUG COMAND  
        
        if my_list != ():
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

            if config.DEBUG: print('[IN FUNCTION] chek voice')  #DEBUG COMAND  
            
            if not voice:   
                voicechannel = ctx.author.voice.channel
                await voicechannel.connect(timeout=6000)   
            voice = discord.utils.get(bot.voice_clients, guild=ctx.guild) 

            if config.DEBUG: print('[IN FUNCTION] chek play')  #DEBUG COMAND  
               
            if voice.is_playing():
                voice.stop() 
            my_list.pop(0)

            if config.DEBUG: print('[IN FUNCTION] new music lap')  #DEBUG COMAND    
            
            await music(ctx)
        else: 
            await ctx.send("Список пуст")    
 
    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e) 
        
    if config.DEBUG: print('[END] next')  #DEBUG COMAND
                   
@bot.command()
async def leave(ctx):
    try:
        if config.DEBUG: print('[START] leave')  #DEBUG COMAND 
        
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if config.DEBUG: print('[IN FUNCTION] Try leave')  #DEBUG COMAND 
        
        await voice.disconnect() 
 
    except KeyError as e:
        await ctx.send('Бот не подключен')
    except Exception as e:
        print('[EXCEPTION]', e)
        
    if config.DEBUG: print('[END] leave')  #DEBUG COMAND   

@bot.command()
async def pause(ctx):
    try:
        if config.DEBUG: print('[START] pause')  #DEBUG COMAND 
        
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)

        if config.DEBUG: print('[IN FUNCTION] chek pause')  #DEBUG COMAND 
        
        if voice.is_playing():
            voice.pause()
            await ctx.send("Пауза")
            
        else:
    
            await ctx.send("Музыка не играет")
    
    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e) 
         
    if config.DEBUG: print('[END] pause')  #DEBUG COMAND

@bot.command()
async def play(ctx):      
    try:
        if config.DEBUG: print('[START] play')  #DEBUG COMAND 
        
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)      
        voice.resume()
        await ctx.send("Продолжаем")

    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e)    

    if config.DEBUG: print('[END] play')  #DEBUG COMAND 
        
@bot.command()
async def stop(ctx):
    try:
        if config.DEBUG: print('[START] stop')  #DEBUG COMAND 
        
        voice = discord.utils.get(bot.voice_clients, guild=ctx.guild)
        if voice.is_playing():
            voice.stop()
        await ctx.send("Музыка остановлена")

    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e)     

    if config.DEBUG: print('[END] stop')  #DEBUG COMAND 
        
@bot.command()
async def clear_list(ctx):
    global my_list
    
    if config.DEBUG: print('[START] clear_list')  #DEBUG COMAND 
    
    my_list = []
    try:
        if config.DEBUG: print('[IN FUNCTION] Try to clear files')  #DEBUG COMAND 

        os.chdir('./play_list/') 
        for var in os.listdir('./'):
            os.remove(var)
        os.chdir(os.pardir)
        
        await ctx.send("Плейлист очищен")   

    except KeyError as e:
        await ctx.send(config.INFO_MSG["music"])
    except Exception as e:
        print('[EXCEPTION]', e)  
            
    if config.DEBUG: print('[END] clear_list')  #DEBUG COMAND 
                 
@bot.command()
async def roll(ctx, args='0-100'):
    
    if config.DEBUG: print('[START] roll')  #DEBUG COMAND 
    
    random.seed(time.time())
    min_max = args.split('-')
    try:
        if len(min_max) == 2:
            min, max = int(min_max[0]), int(min_max[1])
        elif len(min_max) == 1:
            min, max = 0, int(min_max[0])
        msg = ("\nПример:\n/roll 0-100", random.randint(min, max))[min < max]
        await ctx.send(msg)
        
    except KeyError as e:
        await ctx.send("\nПример:\n/roll 0-100")
    except Exception as e:
        print('[EXCEPTION]', e) 
    
    if config.DEBUG: print('[END] roll')  #DEBUG COMAND 

@bot.command()
async def info(ctx, name=''):
    
    if config.DEBUG: print('[START] info')  #DEBUG COMAND 
    
    try:
        if name == '':
            result = "Список команд:'"
            for key, val in config.INFO_NAMES.items():
                result += f'\n**/{key}** - {val}'
        elif name in config.INFO_NAMES.keys():
            result = f'\n**/{name}** - {config.INFO_NAMES[name]}'
        else:
            result = '/info [имя команды] или /info '    
        await ctx.send(result)
        
    except KeyError as e:
        await ctx.send(str(bot.get_prefix) + 'info `название команды(необязательно)`')
    except Exception as e:
        print('[EXCEPTION]', e)        
    if config.DEBUG: print('[END] info')  #DEBUG COMAND             


    


bot.run(os.getenv('TOKEN'))

