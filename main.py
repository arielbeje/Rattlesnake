import os
import yaml

import logging
from logging.handlers import TimedRotatingFileHandler

import discord
from discord.ext import commands

workDir = os.getcwd()
logDir = os.path.join(workDir, "logs")
if not os.path.exists(logDir):
    os.makedirs(logDir)

fh = TimedRotatingFileHandler("logs/log", "midnight", encoding="utf-8", backupCount=7)
fh.setLevel(logging.DEBUG)
fh.setFormatter(logging.Formatter(fmt="[%(asctime)s] [%(name)-19s] %(levelname)-8s: %(message)s",
                                  datefmt="%Y-%m-%dT%H:%M:%S%z"))
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(logging.Formatter(fmt="[%(asctime)s] %(levelname)-8s: %(message)s",
                                  datefmt="%Y-%m-%dT%H:%M:%S%z"))
logging.basicConfig(handlers=[fh, ch],
                    level=logging.DEBUG)
logger = logging.getLogger('root')

with open("config.yaml", "r") as f:
    config = yaml.load(f)

bot = commands.Bot(command_prefix="+")


@bot.event
async def on_command_error(ctx, error):
    origerror = getattr(error, "original", error)
    if isinstance(origerror, customchecks.NoPermsError):
        em = discord.Embed(title="Error",
                           description=f"You do not have sufficient permissions to use the command `{ctx.command}`",
                           colour=discord.Colour.red())
        return await ctx.send(embed=em)
    elif isinstance(origerror, commands.MissingPermissions):
        missingPerms = [perm.replace('_', ' ').replace('guild', 'server').title() for perm in origerror.args[0]]
        description = (f"You do not have sufficient permissions to use the command `{ctx.command}`:\n" +
                       f"Missing permissions: {', '.join(missingPerms)}")
        em = discord.Embed(title="Error",
                           description=description,
                           colour=discord.Colour.red())
        return await ctx.send(embed=em)
    elif isinstance(origerror, discord.ext.commands.errors.CommandNotFound):
        pass
    elif isinstance(origerror, discord.errors.Forbidden):
        em = discord.Embed(title="Error",
                           description="I don't have sufficient permissions to do that.",
                           colour=discord.Colour.red())
        return await ctx.send(embed=em)
    else:
        raise error


@bot.event
async def on_ready():
    logger.info(f"Logged in as: {bot.user.name} - {bot.user.id}")
    logger.info(f"Serving {len(bot.users)} users in {len(bot.guilds)} server{('s' if len(bot.guilds) > 1 else '')}")


if __name__ == "__main__":
    hadError = False
    coglist = []
    for root, directories, files in os.walk("cogs"):
        for filename in files:
            filepath = os.path.join(root, filename)
            if filepath.endswith(".py"):
                coglist.append(filepath.split(".py")[0].replace(os.sep, "."))

    logger.debug("Loading cogs")
    for cog in coglist:
        logger.debug(f"Loading {cog}")
        try:
            bot.load_extension(cog)
            logger.debug(f"Loaded {cog} successfully")
        except Exception:
            logger.exception(f"Failed to load cog: {cog}")
            hadError = True
    if hadError:
        logger.warning("Error during cog loading")
    else:
        logger.info("Successfully loaded all cogs")
    bot.run(os.environ["UBOT"], bot=True, reconnect=True)
