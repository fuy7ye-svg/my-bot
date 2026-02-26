import discord
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as: {bot.user.name}')

@bot.event
async def on_member_join(member):
    channel = discord.utils.get(member.guild.channels, name='✈️welcome')
    if channel:
        embed = discord.Embed(
            
            description=f"**حيّاك الله** {member.mention}",
            color=0x2f3136
        )
        embed.set_image(url=member.display_avatar.url)
        await channel.send(embed=embed)

# تأكد من وضع التوكن الجديد هنا

bot.run('MTQ3NjI2ODY3NDc4Nzg0MDIwMg.Gdq9i3.OhfSMcvb6RL15yWtywFHiVjJsrE_dRDYp36OG0')
