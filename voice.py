import os
import discord
from discord import app_commands

# 音声ファイルを置くルートディレクトリ
SOUNDS_ROOT = "sounds"


def get_sound_dir(bot_name: str) -> str:
    """bot_name (lili / nana / makaron) ごとの音声フォルダのパスを返す"""
    return os.path.join(SOUNDS_ROOT, bot_name)


def list_sounds(bot_name: str) -> list[str]:
    """再生可能な音声ファイル名(拡張子なし)の一覧を返す"""
    d = get_sound_dir(bot_name)
    if not os.path.isdir(d):
        return []
    return sorted(
        os.path.splitext(f)[0]
        for f in os.listdir(d)
        if f.lower().endswith((".mp3", ".wav", ".ogg", ".m4a"))
    )


def find_sound_path(bot_name: str, name: str) -> str | None:
    """名前から実際のファイルパスを探す(拡張子はいろいろ試す)"""
    d = get_sound_dir(bot_name)
    for ext in (".mp3", ".wav", ".ogg", ".m4a"):
        path = os.path.join(d, f"{name}{ext}")
        if os.path.isfile(path):
            return path
    return None


def register_voice_commands(bot, bot_name: str, display_name: str, blacklist, is_in_target_area):
    """
    各Botの setup_hook 内から呼び出す。
    /join, /leave, /play, /soundlist の4つのスラッシュコマンドを追加する。
    """

    @bot.tree.command(name="join", description=f"{display_name}をボイスチャンネルに呼ぶ")
    async def join(interaction: discord.Interaction):
        if interaction.user.id in blacklist:
            await interaction.response.send_message("………", ephemeral=True)
            return
        if not is_in_target_area(interaction.channel):
            await interaction.response.send_message("ピピーー！(ここではお話しできないよ)", ephemeral=True)
            return
        if not isinstance(interaction.user, discord.Member) or interaction.user.voice is None:
            await interaction.response.send_message("ビーッ！(先にボイスチャンネルに入ってね！)", ephemeral=True)
            return

        channel = interaction.user.voice.channel
        vc = interaction.guild.voice_client

        try:
            if vc is None:
                await channel.connect()
            elif vc.channel.id == channel.id:
                await interaction.response.send_message("ピコピコ(もう一緒にいるよ！)", ephemeral=True)
                return
            else:
                await vc.move_to(channel)
            await interaction.response.send_message(f"ピコﾝ！({channel.name} に来たよ～！)")
        except Exception as e:
            await interaction.response.send_message(f"ピコﾋﾟー（入れなかった…({e})）", ephemeral=True)

    @bot.tree.command(name="leave", description=f"{display_name}をボイスチャンネルから退出させる")
    async def leave(interaction: discord.Interaction):
        if interaction.user.id in blacklist:
            await interaction.response.send_message("……。", ephemeral=True)
            return

        vc = interaction.guild.voice_client if interaction.guild else None
        if vc is None:
            await interaction.response.send_message("ピピピ…(どこにもいないよ？)", ephemeral=True)
            return

        await vc.disconnect(force=True)
        await interaction.response.send_message("ピーー！(ばいばーい！)")

    @bot.tree.command(name="play", description=f"{display_name}に音声ファイルを再生させる")
    @app_commands.describe(name="再生したい音声ファイル名(拡張子なし)")
    async def play(interaction: discord.Interaction, name: str):
        if interaction.user.id in blacklist:
            await interaction.response.send_message("………", ephemeral=True)
            return
        if not is_in_target_area(interaction.channel):
            await interaction.response.send_message("ピピーー！(ここではお話しできないよ)", ephemeral=True)
            return

        vc = interaction.guild.voice_client if interaction.guild else None

        if vc is None or not vc.is_connected():
            if isinstance(interaction.user, discord.Member) and interaction.user.voice:
                vc = await interaction.user.voice.channel.connect()
            else:
                await interaction.response.send_message("ピッピッ(先にボイスチャンネルに入ってね！)", ephemeral=True)
                return

        path = find_sound_path(bot_name, name)
        if path is None:
            available = list_sounds(bot_name)
            hint = "、".join(available) if available else "ピピ（まだ音声ファイルがないよ）"
            await interaction.response.send_message(
                f"その音声はないよ…！使える音声：{hint}", ephemeral=True
            )
            return

        if vc.is_playing():
            vc.stop()

        try:
            source = discord.FFmpegPCMAudio(path)
        except Exception as e:
            await interaction.response.send_message(f"ピコピコ…(再生できなかった…({e}))", ephemeral=True)
            return

        vc.play(source)
        await interaction.response.send_message(f"🎵 ﾋﾟー！({name} を再生するよ！)")

    @play.autocomplete("name")
    async def play_autocomplete(interaction: discord.Interaction, current: str):
        return [
            app_commands.Choice(name=s, value=s)
            for s in list_sounds(bot_name)
            if current.lower() in s.lower()
        ][:25]

    @bot.tree.command(name="stop", description=f"{display_name}が再生中の音声を止める")
    async def stop(interaction: discord.Interaction):
        if interaction.user.id in blacklist:
            await interaction.response.send_message("……。", ephemeral=True)
            return
 
        vc = interaction.guild.voice_client if interaction.guild else None
        if vc is None or not vc.is_connected():
            await interaction.response.send_message("どこにもいないよ？", ephemeral=True)
            return
 
        if not vc.is_playing() and not vc.is_paused():
            await interaction.response.send_message("今は何も再生してないよ！", ephemeral=True)
            return
 
        vc.stop()
        await interaction.response.send_message("ﾋﾟ！(止めたよ！)")
 
    @bot.tree.command(name="volume", description=f"{display_name}の再生音量を変更する")
    @app_commands.describe(percent="音量(%)。0〜200の数字で指定(未指定なら現在の音量を表示)")
    async def volume(interaction: discord.Interaction, percent: app_commands.Range[int, 0, 200] = None):
        if interaction.user.id in blacklist:
            await interaction.response.send_message("……。", ephemeral=True)
            return
        if not is_in_target_area(interaction.channel):
            await interaction.response.send_message("ここではお話しできないよ。", ephemeral=True)
            return
 
        key = (bot_name, interaction.guild.id)
 
        if percent is None:
            current = int(_volumes.get(key, 1.0) * 100)
            await interaction.response.send_message(f"ピピピ(今の音量は {current}% だよ！)", ephemeral=True)
            return
 
        volume_value = percent / 100
        _volumes[key] = volume_value
 
        vc = interaction.guild.voice_client if interaction.guild else None
        if vc is not None and isinstance(vc.source, discord.PCMVolumeTransformer):
            vc.source.volume = volume_value
 
        await interaction.response.send_message(f"🔊 ピコン(音量を {percent}% にしたよ！)")

    @bot.tree.command(name="soundlist", description=f"{display_name}が再生できる音声の一覧を表示する")
    async def soundlist(interaction: discord.Interaction):
        if interaction.user.id in blacklist:
            await interaction.response.send_message("………", ephemeral=True)
            return

        sounds = list_sounds(bot_name)
        if not sounds:
            await interaction.response.send_message("ビーー(まだ音声ファイルが置かれてないよ！)", ephemeral=True)
            return

        text = "\n".join(f"・{s}" for s in sounds)
        await interaction.response.send_message(f"ピコﾋﾟ(再生できる音声一覧だよ！\n{text})", ephemeral=True)
    @bot.tree.error
    async def on_voice_command_error(interaction: discord.Interaction, error: Exception):
        # ここに来ると必ずログに出るので、何が起きたか追いやすくなる
        print(f"[{display_name} slash command error] {type(error).__name__}: {error}")
        import traceback
        traceback.print_exception(type(error), error, error.__traceback__)
 
        try:
            if interaction.response.is_done():
                await interaction.followup.send("エラーが起きたみたい…！ごめんね。", ephemeral=True)
            else:
                await interaction.response.send_message("エラーが起きたみたい…！ごめんね。", ephemeral=True)
        except Exception:
            pass
