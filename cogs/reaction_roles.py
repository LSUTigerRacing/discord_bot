import discord
from discord.ext import commands
import json
import os
import logging

class ReactionRoles(commands.Cog, name="rr"):
    def __init__(self, bot):
        self.bot = bot
        self.role_messages = {}
        self.data_file = "reaction_roles.json"
        self.help_file = "reactionroleshelp.txt"

    async def save_data(self):
        # serialize data
        save_data = {
            str(msg_id): {str(emoji): role_id for emoji, role_id in roles.items()}
            for msg_id, roles in self.role_messages.items()
        }

        with open(self.data_file, "w") as file:
            json.dump(save_data, file, indent=4)

    async def load_data(self):
        if not os.path.exists(self.data_file):
            print(f"Reaction Roles: No data file found at {self.data_file}!")
            return
        
        try: 
            with open(self.data_file, 'r') as file:
                data = json.load(file)

                # convert data back into working format
                self.role_messages = {
                    int(msg_id): {emoji: role_id for emoji, role_id in roles.items()}
                    for msg_id, roles in data.items()
                }
        
        except (json.JSONDecodeError, FileNotFoundError):
            print(f"Reaction Roles: JSON at {self.data_file} either missing or corrupt!")

    @commands.Cog.listener()
    async def on_ready(self):
        await self.load_data()

    @commands.group(name="ReactionRoles",
                    aliases=["rr"],
                    help = "type !help rr",
                    description="Create and manage messages that assign roles when users react",
                    invoke_without_command = True # this makes !help work for this cog
                    )
    @commands.has_permissions(manage_roles=True)
    async def reaction_roles_group(self, ctx):
        if ctx.invoked_subcommand is None: # print out help command if nothing other than !rr
            await ctx.send_help(self.reaction_roles_group)

    
    @reaction_roles_group.command(
            name="create", 
            help="Create a new reaction role message",
            description="""
            Usage:`!rr create [title] [description]`

            Example: !rr create

            Arguments:
                title - The title of the RR message (default is "Reaction Roles")
                description - The description of the RR message (default is "Click on the emojis for roles!")
            
            The bot will output the message ID for use in other commands. YOU SHOULD WRITE DOWN THE MESSAGE ID SOMEWHERE.
            """
    )                
    async def create_reaction_message(self, ctx, title: str = "Reaction Roles", description: str = "Click on the emojis for roles!"):
        """Reaction Role Message"""
        embed = discord.Embed(
            title=title,
            description=description,
            color=discord.Color.dark_purple()
        )

        message = await ctx.send(embed=embed)
        self.role_messages[message.id] = {}
        await self.save_data()
        await ctx.send(f"Created new reaciton role message with message ID: {message.id}")

    @reaction_roles_group.command(
            name="add",
            help="Add a reaction role to a message",
            description="""
            Usage:`!rr add <message_id> <emoji> <@role> [role_type]`

            Example: !rr add 1391197722618499262 🔋 @powertrain sys
            
            Arguments:
                message_id - The ID of the reaction role message (integer)
                emoji - The emoji to use for the reaction (string or custom emoji)
                role - The role to assign (ping it)
                role_type - Optional: "sys" for system or "sub" for subsystem (default: "sys")""",
            )
    async def add_reaction_role(self, ctx, message_id: int, emoji: str, role: discord.Role, message_title: str="Reaction Roles", message_desc: str="Click the emojis for roles!"):
        try:
            message = await ctx.channel.fetch_message(message_id)

            # is message_id a designated reaction role message?
            if message_id not in self.role_messages:
                await ctx.send("This is not a reaction role message. Create one with !create.")
                return
            
            # if emoji is already in use
            if emoji in self.role_messages[message_id]:
                await ctx.send("This emoji is already assigned to a role!")
                return
            
            # add reaction role
            self.role_messages[message_id][emoji] = role.id
            await self.save_data()

            # add reaction to message
            await message.add_reaction(emoji)

            # update embed
            embed = message.embeds[0] if message.embeds else discord.Embed(title=message_title)

            # add or update roles listed
            roles_list = "\n".join(
                f"{emb} - {ctx.guild.get_role(rol).mention}"
                for emb, rol in self.role_messages[message_id].items()
            )

            embed.set_field_at(0, name=message_desc, value=roles_list)

            await message.edit(embed=embed)
            await ctx.send(f"Added role: {emoji} = {role.name}")

        except discord.NotFound:
            await ctx.send("Message not found. Make sure you use this command in the same channel as the message.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to add reaction role; Exception: {e}")

    @reaction_roles_group.command(
            name="remove",
            help="Remove a reaction role from a message",
            description="""
            Usage:`!rr remove <message_id> <emoji>`

            Example: !rr remove 1391197722618499262 🔋
            
            Arguments:
                message_id - The ID of the reaction role message (integer)
                emoji - The emoji to use for the reaction (string or custom emoji)""",
            )
    async def remove_reaction_role(self, ctx, message_id: int, emoji: str):
        try:
            try:
                message = await ctx.channel.fetch_message(message_id)
            except discord.NotFound:
                await ctx.send("Message not found. Make sure you use this command in the same channel as the message.")
                return
            except discord.HTTPException as e:
                await ctx.send(f"Failed to remove reaction role; Exception: {e}")
                return

            # is message_id a designated reaction role message?
            if message_id not in self.role_messages:
                await ctx.send("This is not a reaction role message. Create one with !create.")
                return
            
            # is emoji actually in message
            if emoji not in self.role_messages[message_id]:
                await ctx.send("Emoji not found on message!")
                print(self.role_messages[message_id])
                return
            

            #remove emoji reaction
            await message.clear_reaction(emoji)

            # add or update roles listed
            if message.embeds:
                embed = message.embeds[0]

                if self.role_messages[message_id]:
                    roles_list = "\n".join(
                        f"{emb} - {ctx.guild.get_role(rol).mention}"
                        for emb, rol in self.role_messages[message_id].items()
                    )
                await message.edit(embed=embed)

            await ctx.send(f"Removed role: {emoji}")
            # remove reaction role
            del self.role_messages[message_id][emoji]
            await self.save_data()

        except discord.NotFound:
            await ctx.send("Message not found. Make sure you use this command in the same channel as the message.")
            return
        except discord.HTTPException as e:
            await ctx.send(f"Failed to remove reaction role; Exception: {e}")
            return

    # actually assign the role
    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload): # check docs https://discordpy.readthedocs.io/en/stable/api.html?highlight=on_reaction_add#discord.on_raw_reaction_add
        if payload.message_id not in self.role_messages:
            print("Reaction Roles: React Failure, Reaction Message somehow not in JSON Database")
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None: 
            print("Reaction Roles: React Failure, No Guild found")
            return

        role_id = self.role_messages.get(payload.message_id).get(str(payload.emoji))
        if role_id is None: 
            print(f"Reaction Roles: React Failure, Role ID not found in {payload.emoji}")
            return

        role = guild.get_role(role_id)
        if role is None: return

        try:
            await payload.member.add_roles(role)
        except discord.HTTPException:
            print("Reaction Roles, React Failure, HTTP Exception")
            pass

    # take role away if reaction removed
    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload): # https://discordpy.readthedocs.io/en/stable/api.html?highlight=on_reaction_add#discord.on_raw_reaction_remove
        if payload.message_id not in self.role_messages:
            print("Reaction Roles: Unreact Failure, Reaction Message somehow not in JSON Database")
            return
        
        guild = self.bot.get_guild(payload.guild_id)
        if guild is None: 
            print("Reaction Roles: Unreact Failure, No Guild found")
            return

        role_id = self.role_messages.get(payload.message_id).get(str(payload.emoji))
        if role_id is None: 
            print(f"Reaction Roles: Unreact Failure, Role ID not found in {payload.emoji}")
            return

        role = guild.get_role(role_id)
        if role is None: return

        member = guild.get_member(payload.user_id)
        try:
            await member.remove_roles(role)
        except discord.HTTPException:
            pass

async def setup(bot):
    await bot.add_cog(ReactionRoles(bot))