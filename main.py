import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread
import asyncio

# --- 1. خادم Flask لإبقاء البوت متصل 24/7 ---
app = Flask('')

@app.route('/')
def home():
    return "Ticket Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. إعدادات البوت ---
intents = discord.Intents.default()
intents.message_content = True 
intents.guilds = True

bot = commands.Bot(command_prefix='!', intents=intents)

# ⚠️ ضع آيدي رتبة الإدارة هنا (التي ستشاهد التذاكر)
STAFF_ROLE_ID = 123456789012345678 

# --- 3. أزرار التكت ---
class TicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None) # لضمان بقاء الزر شغال دائماً

    @discord.ui.button(label="فتح تذكرة | Open Ticket", style=discord.ButtonStyle.green, custom_id="open_ticket_btn")
    async def open_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        guild = interaction.guild
        member = interaction.user
        staff_role = guild.get_role(STAFF_ROLE_ID)
        
        # إعداد خصوصية القناة
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=False),
            member: discord.PermissionOverwrite(view_channel=True, send_messages=True, read_message_history=True),
            guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True)
        }
        
        if staff_role:
            overwrites[staff_role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)
        
        # إنشاء قناة التكت
        channel = await guild.create_text_channel(name=f"ticket-{member.name}", overwrites=overwrites)
        
        embed = discord.Embed(
            title="تذكرة جديدة",
            description=f"مرحباً {member.mention}، فريق الإدارة سيتواصل معك قريباً.\nلإغلاق التذكرة اضغط على الزر أدناه.",
            color=discord.Color.blue()
        )
        
        view = CloseTicketView()
        await channel.send(embed=embed, view=view)
        await interaction.response.send_message(f"تم فتح تذكرتك هنا: {channel.mention}", ephemeral=True)

class CloseTicketView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="إغلاق التذكرة | Close", style=discord.ButtonStyle.red, custom_id="close_ticket_btn")
    async def close_ticket(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("سيتم حذف القناة خلال 5 ثوانٍ...")
        await asyncio.sleep(5)
        await interaction.channel.delete()

# --- 4. الأحداث والأوامر ---
@bot.event
async def on_ready():
    bot.add_view(TicketView())
    bot.add_view(CloseTicketView())
    print(f'✅ البوت يعمل الآن باسم: {bot.user.name}')

@bot.command()
@commands.has_permissions(administrator=True)
async def setup(ctx):
    """أمر لإرسال رسالة التكت (اكتب !setup في القناة)"""
    embed = discord.Embed(
        title="نظام التذاكر | Support System",
        description="إذا كان لديك استفسار أو شكوى، اضغط على الزر أدناه لفتح تذكرة خاصة.",
        color=discord.Color.green()
    )
    await ctx.send(embed=embed, view=TicketView())

# --- 5. التشغيل ---
if __name__ == "__main__":
    keep_alive() # تشغيل Flask
    token = os.getenv('DISCORD_TOKEN')
    if token:
        bot.run(token)
    else:
        print("❌ خطأ: لم يتم العثور على DISCORD_TOKEN!")
