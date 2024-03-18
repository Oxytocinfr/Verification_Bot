import discord
from discord.ext import commands
from db import create_table, view_emails, insert_email, insert_phone, view_emails_with_username, view_username_with_email

intents = discord.Intents.default()
intents.dm_messages = True
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.command()
async def start_verification(ctx):
    embed = discord.Embed(
        title="Verification Process",
        description="React to this message to start the verification process.",
        color=discord.Color.blue()
    )
    message = await ctx.send(embed=embed)
    await message.add_reaction("✅")  # Add a check mark reaction

@bot.event
async def on_reaction_add(reaction, user):
    if user.name == 'Verification':
        print('Reaction added by bot')
    print(f"Reaction added: {reaction.emoji} by {user.name}")
    ctx = await bot.get_context(reaction.message)
    await ctx.invoke(bot.get_command('verify'))

    # # Check if the reaction is on the verification message
    # if reaction.message.content.startswith("Verification Process"):
    #     print("Verification process started...")
    #     # Check if the reaction is the specified emoji
    #     if str(reaction.emoji) == "✅":
    #         print("Check mark reaction detected...")
    #         # Call the verify command for the user who reacted
    #         ctx = await bot.get_context(reaction.message)
    #         print(f"Calling verify command for {user.name}")
    #         await ctx.invoke(bot.get_command('verify'), ctx)

@bot.command()
async def verify(ctx):
    print("Verification command invoked...")
    # Check if the user already has the "Verified" role
    verified_role = discord.utils.get(ctx.guild.roles, name='Verified')
    if verified_role in ctx.author.roles:
        print("User is already verified.")
        await ctx.send("You are already verified.")
        return

    print("User is not verified. Starting verification process...")
    # Create a new channel
    overwrites = {
        ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
        ctx.author: discord.PermissionOverwrite(read_messages=True)
    }
    channel = await ctx.guild.create_text_channel(f'verify-{ctx.author.display_name}', overwrites=overwrites)

    await channel.send(f"{ctx.author.mention}, please provide your Email ID in this channel.")

    def check_message(msg):
        return msg.author == ctx.author and msg.channel == channel

    email_msg = await bot.wait_for('message', check=check_message)

    # Storing email ID in the database
    insert_email(ctx.author.id, email_msg.content)

    await channel.send("Please provide your phone number.")

    def check_phone(msg):
        return msg.author == ctx.author and msg.channel == channel and len(msg.content) >= 10

    phone_msg = await bot.wait_for('message', check=check_phone)

    # Ensure phone number has at least 10 digits
    if len(phone_msg.content) < 10:
        print("Phone number verification failed. Not enough digits.")
        await ctx.send("Phone number must contain at least 10 digits. Verification failed.")
        return

    # Storing phone number in the database
    insert_phone(ctx.author.id, phone_msg.content)

    # Delete the channel
    await channel.delete()

    # Provide role to the user
    role_id = 1218950735077838979  # Role ID for 'Verified' role
    role = discord.utils.get(ctx.guild.roles, id=role_id)
    await ctx.author.add_roles(role)
    await ctx.send(f"{ctx.author.mention}, you're now verified.")

@bot.command()
@commands.has_permissions(administrator=True)
async def view_data(ctx):
    emails = view_emails()
    if emails:
        email_list = "\n".join([f"<@{row[1]}>: Email - {row[2]}, Phone - {row[3]}" for row in emails])  # Display user ID, email, and phone number
        await ctx.send(f"Stored emails:\n```{email_list}```")
    else:
        await ctx.send("No emails stored in the database.")

@bot.command()
@commands.has_permissions(administrator=True)
async def get_username(ctx, email: str):
    user_id_list = view_username_with_email(email)
    if user_id_list:
        user_id = user_id_list[0][0]  # Assuming only one user with the given email
        member = ctx.guild.get_member(int(user_id))
        if member:
            await ctx.send(f"The username associated with email {email} is: {member.display_name}")
        else:
            await ctx.send("User not found in the server.")
    else:
        await ctx.send(f"No user found with the email {email}.")

@bot.command()
@commands.has_permissions(administrator=True)
async def get_email(ctx, user_id: int):
    email_list = view_emails_with_username(user_id)
    if email_list:
        await ctx.send(f"The email associated with user ID {user_id} is: {email_list[0][0]}")
    else:
        await ctx.send(f"No email found for user ID {user_id}.")


@bot.command()
async def ping(ctx):
    await ctx.send('Pong!')


if __name__ == '__main__':
    bot.run('token')
