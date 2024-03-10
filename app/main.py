import discord
from discord.ext import commands
import os
import sqlite3
import re
import time
from core.start import DBot

# Secretsから環境変数を読み込む
TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.all()
intents.message_content = True

client = commands.Bot(command_prefix="!", intents=intents)

# データベース接続
conn = sqlite3.connect('message_history.db')
cursor = conn.cursor()

last_message_times = {}  # ユーザごとの最後のメッセージ送信時刻を記録する辞書
max_messages_within_interval = 5  # 一定期間内の最大メッセージ数
message_interval = 5  # メッセージ間の最小間隔（秒）

# メッセージ履歴のテーブルを作成
cursor.execute('''CREATE TABLE IF NOT EXISTS message_history
                  (id INTEGER PRIMARY KEY AUTOINCREMENT,
                   content TEXT,
                   sender INTEGER,
                   timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
conn.commit()

# URL判定機
_contains_url_matcher = re.compile(
    r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')

@client.event
async def on_ready():
    print(f'Logged in as {client.user.name}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return  # ボット自身のメッセージは無視

    # ゆるカフェのメンバーかどうかの確認
    yurucafe_member = getYurucafeMember(message.author)
    if yurucafe_member is None:
        # ゆるカフェのメンバーではないので無視
        return

    # 匿名掲示板の処理
    # ダイレクトメッセージの場合
    # 匿名チャンネルにメッセージを送信する。
    if isinstance(message.channel, discord.DMChannel):
        # メッセージの送信間隔をチェック
        now = time.time()
        last_message_time = last_message_times.get(message.author.id, 0)
        if now - last_message_time < message_interval:
            await message.author.send("警告：メッセージを送信する間隔が短すぎます。")
            await log_warn(message.author, "メッセージを送信する間隔が短すぎます。", message.content)
            return
        last_message_times[message.author.id] = now

        # メッセージ数のカウントと制限の確認
        message_count = sum(1 for t in last_message_times.values() if now - t < message_interval)
        if message_count >= max_messages_within_interval:
            await message.author.send("警告：一定期間内のメッセージ数が多すぎます。")
            await log_warn(message.author, "一定期間内のメッセージ数が多すぎます。", message.content)
            return

        # メッセージにURLを含む場合
        if contains_url(message.content):
            await message.author.send("警告：URLを送信しないでください。")
            await log_warn(message.author, "メッセージにURLが含まれています。", message.content)
            return

        # 禁止ワードを含む場合
        forbidden_words = ["死ね", "殺す", "殺害"]  # 禁止ワードのリスト
        for word in forbidden_words:
            if word in message.content:
                # メッセージが警告対象の単語を含む場合、送信者に警告を送る
                await message.author.send(
                    "警告！過激な言葉が含まれているから送信できないよ。もう一度文章を考えてみてね！")
                await log_warn(message.author, "死ね、殺す、殺害のどれか", message.content)
                return

        # 匿名メッセージの保存
        cursor.execute("INSERT INTO message_history (content, sender) VALUES (?, ?)",
                            (message.content, message.author.id))
        conn.commit()

        # 匿名メッセージを匿名チャンネルに送信
        server = client.get_guild(983702974792613969)  # ゆるカフェのサーバIDを指定
        channel = server.get_channel(1165550084394602497)  # 匿名掲示板チャンネルのIDを指定
        await channel.send(f'{message.content}')

        # ログを特定のチャンネルに送信
        log_channel_id = 995853282838847528  # ログを送信したいチャンネルのID
        log_channel = client.get_channel(log_channel_id)  # ログを送信したいチャンネルを取得

        if log_channel:
            await log_channel.send(f"{message.author.mention}: {message.content}")

        return  # 匿名掲示板の処理

async def log_warn(user, warning, content):
    log_channel_id = 1159370416779960412  # ログを送信したいチャンネルのID
    log_channel = client.get_channel(log_channel_id)  # ログを送信したいチャンネルを取得
    if log_channel:
        await log_channel.send(f"警告を送信: {user.mention} - {warning}: {content}")

# 指定ユーザがゆるカフェに入っているかを判定します。
def getYurucafeMember(user: discord.User) -> discord.Member:
    # メッセージを送信したユーザがサーバに属しているかどうかを確認
    guild = client.get_guild(983702974792613969)  # サーバのIDを指定
    if guild:
        return guild.get_member(user.id)
    else:
        return None

# 指定文字列の中に、URLが含まれるかを判定します。
def contains_url(content: str) -> bool:
    return bool(_contains_url_matcher.search(content))

# Bot立ち上げ
DBot(
    token=Token,
    intents=discord.Intents.all()
).run()
