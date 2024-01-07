def get_bot_role(ctx):
    roles = ctx.guild.me.roles
    role_names = [role.name for role in roles]
    if "Total_Filter" in role_names:
        role = "Total_Filter"
    elif "Harmful_Filter" in role_names:
        role = "Harmful_Filter"
    else:
        role = None
    return role
