import discord


async def ensure_bot_role(guild: discord.Guild, role_name: str,
                          colour: discord.Colour = discord.Colour.default()):
    """Bot専用ロールがなければ作成し、Bot自身に付与する(何度呼んでも安全)"""
    me = guild.me
    if me is None:
        return None

    # Discordが自動で作る「managed」ロールは除外して、自作ロールだけ探す
    role = discord.utils.find(
        lambda r: r.name == role_name and not r.managed, guild.roles
    )

    if role is None:
        if not me.guild_permissions.manage_roles:
            print(f"[{guild.name}] ロール管理権限がないため '{role_name}' を作成できません")
            return None
        try:
            role = await guild.create_role(
                name=role_name,
                colour=colour,
                reason="Bot専用ロールの自動作成",
            )
        except discord.HTTPException as e:
            print(f"[{guild.name}] ロール作成失敗: {e}")
            return None

    # すでにあるロールの色が違う場合は指定色にそろえる
    if role.colour != colour:
        try:
            await role.edit(colour=colour, reason="Bot専用ロールの色を更新")
        except discord.HTTPException as e:
            print(f"[{guild.name}] ロール色の更新失敗: {e}")

    if role not in me.roles:
        try:
            await me.add_roles(role, reason="Bot専用ロールの自動付与")
        except discord.HTTPException as e:
            print(f"[{guild.name}] ロール付与失敗: {e}")
            return None

    return role
