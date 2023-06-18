import streamlit as st
from pydub import AudioSegment
from pydub.playback import play
import random
import time
from bardapi import Bard
import os
import threading
import streamlit.components.v1 as stc
import base64
import re
from yt_dlp import YoutubeDL
root = '/content'
os.environ["_BARD_API_KEY"]="XQhE09mZ6oKiTJ5A32eJ_QDQP3xqbwqMnX0LIN50dLKTrK4iPI9SJiWPsqaFLFJvlQOzlQ."
#url抽出モジュール
def extract_urls(text):
    pattern = r"https://[a-zA-Z0-9./?=_-]+"
    urls = re.findall(pattern, text)
    return urls
#ここからコード
themes=["https://www.youtube.com/watch?v=-geI_lMECjg","https://www.youtube.com/watch?v=dQw4w9WgXcQ","https://www.youtube.com/watch?v=dQw4w9WgXcQ","勉強に集中できる音楽","ゾーンに入る"]
#startfrom=random.randint(0,len(themes))
startfrom=0
cashTime=[0,0,0]
#ダウンロードとトリミング
def dl(n):
  if "https" in themes[(startfrom+n)%len(themes)]:
    links=[themes[(startfrom+n)%len(themes)]]
  else:
    links=extract_urls(Bard().get_answer("リラックスできる["+themes[(startfrom+n)%len(themes)]+"]の環境音楽のyoutubeのリンクとURLを１つ教えて")["content"])
  if len(links)==0:
    #url失敗
    print("error")
    return
  #youtubeダウンロード
  ydl_video_opts = {
       'outtmpl': root +'dl'+str(n)+'.mp3',
        'format': 'bestaudio/best'
  }
  with YoutubeDL(ydl_video_opts) as ydl:
     result = ydl.download(links[0])
  # フェードインとフェードアウトの長さ（ミリ秒単位）
  fade_duration = 2000  # 2秒
  # 音声ファイルの読み込み
  filename=root +"dl"+str(n)+".mp3"
  audio = AudioSegment.from_file(filename)
  # ランダムなトリミング範囲の生成
  start_time = random.randint(0, 5*60)
  end_time = start_time + random.randint(10 * 60* 1000, 20 *60* 1000)  # 10分から20分の範囲でトリミング
  cashTime[(n+2)%n]=end_time-start_time
  # トリミング
  trimmed_audio = audio[start_time:end_time]
  # フェードインとフェードアウトの適用
  trimmed_audio = trimmed_audio.fade_in(fade_duration).fade_out(fade_duration)
  #cashに保存
  trimmed_audio.export(root +"cash"+str((n+2)%3)+".mp3", format='mp3')
  os.remove(root +"dl"+str(n)+".mp3")

def playm(n):
  # トリミングされた音声の再生
  filename=f"cash{(n+1)%3}.mp3"
  print(filename)
  audio_path1 = root+filename #入力する音声ファイル
  audio_placeholder = st.empty()
  file_ = open(audio_path1, "rb")
  contents = file_.read()
  file_.close()
  audio_str = "data:audio/ogg;base64,%s"%(base64.b64encode(contents).decode())
  audio_html = """
                    <audio autoplay=True>
                    <source src="%s" type="audio/ogg" autoplay=True>
                    Your browser does not support the audio element.
                    </audio>
                """ %audio_str
  audio_placeholder.empty()
  time.sleep(0.5) #これがないと上手く再生されません
  audio_placeholder.markdown(audio_html, unsafe_allow_html=True)

def trash(n):
  #キャッシュの削除
  os.remove(root +"cash"+str(n%3)+".mp3")

def bach(n):
  # ダウンロード処理を別スレッドで実行
  download_thread = threading.Thread(target=dl, args=(n))
  download_thread.start()
  playm(n)
  trash(n)
  time.sleep(cashTime[(1+1)%3]-5)


def main():
  st.title("Spotify")
  st.empty()
  with st.spinner("1曲目をダウンロード中"):
   dl(0)
  with st.spinner("2曲目をダウンロード中"):
   dl(1)
  for i in range(10):
    with st.spinner(f"{n+2}曲目を再生中"):
     bach(i+2)

if __name__ == "__main__":
    main()
