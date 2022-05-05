import os
import re
import tempfile
from time import sleep

import azure.cognitiveservices.speech as speechsdk

import discord
discord.opus.load_opus('/usr/local/opt/opus/lib/libopus.0.dylib')
client = discord.Client()

VOICES = {
    "ushuz": "zh-CN-YunyeNeural",
}

token = os.environ["DISCORD_TOKEN"]
azure_tts_key = os.environ["AZURE_SPEECH_KEY"]
azure_tts_region = os.environ["AZURE_SPEECH_REGION"]


def tts(text, voice):
    print(f'synthesizing: {text}')
    speech_config = speechsdk.SpeechConfig(subscription=azure_tts_key, region=azure_tts_region)
    speech_config.speech_synthesis_voice_name = voice
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=None)
    if '+' in voice:
        voice, opts = voice.split('+')
        opts = dict(opt.split('=') for opt in opts.split(','))
        pitch = opts.get('pitch', '0%')
        role = opts.get('role', 'Default')
        ssml = f"""
        <speak xmlns="http://www.w3.org/2001/10/synthesis" xmlns:mstts="http://www.w3.org/2001/mstts" version="1.0" xml:lang="zh">
            <voice name="{voice}">
            <prosody pitch="{pitch}">
            <mstts:express-as role="{role}">
            {text}
            </mstts:express-as>
            </prosody>
            </voice>
        </speak>"""
        result: speechsdk.SpeechSynthesisResult = synthesizer.speak_ssml_async(ssml).get()
    else:
        result: speechsdk.SpeechSynthesisResult = synthesizer.speak_text_async(text).get()
    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        return result.audio_data
    print(f'tts failure: {result.reason}')


P_STICKER = re.compile(r"^[:;][a-zA-Z0-9_-]+[:;]$")
P_EMOJI = re.compile(r"<a?:[a-zA-Z0-9_-]+:\d+>")
P_LINK = re.compile(r"https?://[^\s]+")


@client.event
async def on_message(message: discord.Message):
    # 忽略 bot 消息
    if message.author.bot:
        return
    # 发言人未开语音则忽略
    if not message.author.voice:
        return
    voice_channel: discord.VoiceChannel = message.author.voice.channel
    if not voice_channel:
        return
    # 获取语音 client
    voice_client = discord.utils.get(client.voice_clients, guild=message.guild)
    if not voice_client:
        voice_client = await voice_channel.connect()
    # 获取玩家语音配置
    voice = VOICES.get(message.author.name.lower())
    if not voice:
        print(f'skip: no voice for {message.author.name}')
        return
    # 整理文本
    text = message.clean_content.strip()
    print(f'receiving: {text}')
    text = discord.utils.remove_markdown(text)
    text = re.sub(P_STICKER, '', text)
    text = re.sub(P_EMOJI, '', text)
    text = re.sub(P_LINK, '', text)
    text = text.replace('@', '')
    text = text.replace('#', '')
    text = text.replace('「', '：「')
    if not text.strip():
        print('skip: no text')
        return
    # 合成语音
    data = tts(text=text, voice=voice)
    if not data:
        print('skip: no audio data')
        return
    # 如果当前正在播放就等一等
    while voice_client.is_playing():
        sleep(0.5)
    # 播放语音
    with tempfile.NamedTemporaryFile(mode='xb', prefix='seiyuubot-', suffix='.wav') as f:
        f.write(data); f.seek(0)
        audio = discord.FFmpegOpusAudio(f, pipe=True)
        voice_client.play(audio)


@client.event
async def on_ready():
    print(f'seiyuubot is live: {client.user.name} ({client.user.id})')
    print('------')
    for g in client.guilds:
        print(g.name)
    print('------')


client.run(token)
