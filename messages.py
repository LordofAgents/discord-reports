import discord
from discord.ui import View, Button
from helpers import get_translation, get_author_name, get_playerid_from_name
from modals import TempBanButton, MessagePlayerButton, MessageReportedPlayerButton, Show_logs_button, PermaBanButton, \
    PunishButton, KickButton
import random


async def unitreportembed(player_additional_data, user_lang, unit_name, roles, team, player):
    embed_title = get_translation(user_lang, "players_in_unit").format(unit_name, ', '.join(roles), team)
    embed = discord.Embed(title=embed_title, color=0xd85f0e)
    total_playtime_seconds = player_additional_data.get('total_playtime_seconds', 0)
    total_playtime_hours = total_playtime_seconds / 3600
    embed.add_field(name=get_translation(user_lang, "name"), value=player["name"], inline=True)
    embed.add_field(name=get_translation(user_lang, "level"), value=player["level"], inline=True)
    embed.add_field(name=get_translation(user_lang, "total_playtime"),
                    value=f"{total_playtime_hours:.2f} " + get_translation(user_lang, "hours"), inline=True)
    embed.add_field(name=get_translation(user_lang, "kills"), value=player["kills"], inline=True)
    embed.add_field(name=get_translation(user_lang, "deaths"), value=player["deaths"], inline=True)
    embed.add_field(name=get_translation(user_lang, "steam_id"), value=player["player_id"], inline=True)
    return embed


async def player_not_found_embed(player_id, player_name, user_lang):
    embed = discord.Embed(title=get_translation(user_lang, "no_matching_player_found"), color=discord.Colour.magenta())
    embed.add_field(name=get_translation(user_lang, "name"), value=player_name, inline=True)
    embed.add_field(name=get_translation(user_lang, "steam_id"), value=player_id, inline=True)
    return embed


async def playerreportembed(user_lang, best_match, player_stats, total_playtime_hours, best_player_data):
    embed_title = get_translation(user_lang, "report_for_player").format(best_match)
    embed = discord.Embed(title=embed_title, color=0xd85f0e)

    realname = None
    if player_stats.get('steaminfo') and player_stats['steaminfo'].get('profile'):
        realname = player_stats['steaminfo']['profile'].get('realname')

    if realname:
        embed.add_field(name=get_translation(user_lang, "realname"), value=realname, inline=True)
    embed.add_field(name=get_translation(user_lang, "information"),
                    value=get_translation(user_lang, "check_report_match"), inline=False)
    embed.add_field(name=get_translation(user_lang, "total_playtime"),
                    value=f"{total_playtime_hours:.2f} " + get_translation(user_lang, "hours"), inline=True)
    embed.add_field(name="Steam-ID", value=best_player_data['player_id'], inline=True)
    embed.add_field(name=get_translation(user_lang, "kills"), value=player_stats['kills'], inline=True)
    embed.add_field(name=get_translation(user_lang, "kill_streak"), value=player_stats['kills_streak'], inline=True)
    embed.add_field(name=get_translation(user_lang, "kill_death_ratio"), value=player_stats['kill_death_ratio'],
                    inline=True)
    embed.add_field(name=get_translation(user_lang, "kills_per_minute"), value=player_stats['kills_per_minute'],
                    inline=True)
    embed.add_field(name=get_translation(user_lang, "deaths"), value=player_stats['deaths'], inline=True)
    embed.add_field(name=get_translation(user_lang, "teamkills"), value=player_stats['teamkills'], inline=True)
    embed.add_field(name=get_translation(user_lang, "teamkill_streak"), value=player_stats['teamkills_streak'],
                    inline=True)
    return embed


class Reportview(discord.ui.View):
    def __init__(self, api_client):
        super().__init__(timeout=3600)
        self.api_client = api_client

    async def on_timeout(self) -> None:
        # Step 2
        for item in self.children:
            item.disabled = True

        # Step 3
        await self.message.edit(view=self)

    async def add_buttons(self, user_lang, reported_player_name, player_id, funct_unjustified_report_click,
                          funct_no_action_click, manual_process, self_report=False):
        if self_report == False:
            author_name = get_author_name()
            author_player_id = await get_playerid_from_name(author_name, self.api_client)
        else:
            author_name = False
            author_player_id = False
        # Message reported player
        message_reported_player_button_label = get_translation(user_lang, "message_reported_player").format(reported_player_name)
        message_reported_player_button = MessageReportedPlayerButton(label=message_reported_player_button_label,
                                                                     custom_id=f"message_reported_player_{player_id}",
                                                                     api_client=self.api_client,
                                                                     player_id=player_id,
                                                                     user_lang=user_lang, author_name=author_name,
                                                                     author_player_id=author_player_id, self_report=self_report)
        self.add_item(message_reported_player_button)

        # Punish
        punish_button_label = get_translation(user_lang, "punish_button_label").format(reported_player_name)
        punish_button = PunishButton(label=punish_button_label,
                                     custom_id=f"punish_{player_id}",
                                     api_client=self.api_client,
                                     player_id=player_id, user_lang=user_lang,
                                     author_player_id=author_player_id, self_report=self_report)
        self.add_item(punish_button)

        # Kick player
        kick_button_label = get_translation(user_lang, "kick_player")
        kick_button = KickButton(label=kick_button_label, custom_id=f"kick_{player_id}", api_client=self.api_client, player_id=player_id, user_lang=user_lang, author_player_id=author_player_id, author_name=author_name, self_report=self_report)
        self.add_item(kick_button)
        # Tempban
        temp_ban_button_label = get_translation(user_lang, "temp_ban_player").format(reported_player_name)
        temp_ban_button = TempBanButton(label=temp_ban_button_label,
                                        custom_id=f"temp_ban_{player_id}",
                                        api_client=self.api_client,
                                        player_id=player_id, user_lang=user_lang,
                                        author_player_id=author_player_id, self_report=self_report)
        self.add_item(temp_ban_button)
        # Perma-Ban
        perma_ban_button_label = get_translation(user_lang, "perma_ban_button_label").format(reported_player_name)
        perma_ban_button = PermaBanButton(label=perma_ban_button_label,
                                          custom_id=f"perma_ban_{player_id}",
                                          api_client=self.api_client, player_id=player_id,
                                          user_lang=user_lang, author_player_id=author_player_id, self_report=self_report)
        self.add_item(perma_ban_button)
        if self_report == False:
        # Message Reporter
            message_player_button_label = get_translation(user_lang, "message_player").format(reported_player_name)
            message_player_button = MessagePlayerButton(label=message_player_button_label,
                                                        custom_id=f"message_player_{player_id}",
                                                        api_client=self.api_client, player_id=player_id,
                                                        user_lang=user_lang, self_report=self_report)
            self.add_item(message_player_button)
        # Mimimi
        unjustified_report_button = Button(label=get_translation(user_lang, "unjustified_report"),
                                           style=discord.ButtonStyle.grey, custom_id="unjustified_report")
        unjustified_report_button.callback = funct_unjustified_report_click
        self.add_item(unjustified_report_button)
        # Müll
        no_action_button = Button(label=get_translation(user_lang, "wrong_player_reported"),
                                  style=discord.ButtonStyle.grey,
                                  custom_id="no_action")
        no_action_button.callback = funct_no_action_click
        self.add_item(no_action_button)
        show_logs_buttonobj = Show_logs_button(self, reported_player_name, custom_id="logs", user_lang=user_lang)
        self.add_item(show_logs_buttonobj)
        manual_process_button = Button(label=get_translation(user_lang, "button_manual_process"),
                                       style=discord.ButtonStyle.grey,
                                       custom_id="manual_process")
        manual_process_button.callback = manual_process
        self.add_item(manual_process_button)
