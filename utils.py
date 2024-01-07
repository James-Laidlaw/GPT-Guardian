from detect_hate import filter_levels


def get_bot_role(ctx):
    roles = ctx.guild.me.roles
    role_names = [role.name for role in roles]
    for role in filter_levels:
        if role["name"] in role_names:
            return role
