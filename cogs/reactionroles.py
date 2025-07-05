import discord
from discord.ext import commands
import json
import os
import logging

class ReactionRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_messages = {}
        self.data_file = "reaction_roles.json"

    async def save_data(self):
        print("called!")
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

    @commands.group(name="Reaction Roles", aliases=["rr"])
    @commands.has_permissions(manage_roles=True)
    async def reaction_roles_group(self, ctx):
        if ctx.invoked_subcommand is None:
            await ctx.send("List of commands")
    
    @reaction_roles_group.command(name="create")
    async def create_reaction_message(self, ctx, description: str = "mmm react for roles"):
        """Reaction Role Message"""
        embed = discord.Embed(
            title="Reaction Roles",
            description=description,
            color=discord.Color.purple()
        )

        message = await ctx.send(embed=embed)
        self.role_messages[message.id] = {}
        await self.save_data()
        await ctx.send(f"Created new reaciton role message with message ID: {message.id}")

    @reaction_roles_group.command(name="add")
    async def add_reaction_role(self, ctx, message_id: int, emoji: str, role: discord.Role):
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
            embed = message.embeds[0] if message.embeds else discord.Embed(title="Reaction Roles")

            # add or update roles listed
            roles_list = "\n".join(
                f"{emb} - {ctx.guild.get_role(rol).mention}"
                for emb, rol in self.role_messages[message_id].items()
            )

            if embed.fields and embed.fields[0].name == "Roles":
                embed.set_field_at(0, name="Roles", value=roles_list)
            else:
                embed.add_field(name="Roles", value=roles_list)

            await message.edit(embed=embed)
            await ctx.send(f"Added role: {emoji} = {role.name}")

        except discord.NotFound:
            await ctx.send("Message not found. Make sure you use this command in the same channel as the message.")
        except discord.HTTPException as e:
            await ctx.send(f"Failed to add reaction role; Exception: {e}")

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
        print("something happened")
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