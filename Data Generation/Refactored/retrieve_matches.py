#!/usr/bin/env python3

import cassiopeia
import csv
import os
import sys
import time


def get_team_stats(team: str, match: cassiopeia.Match) -> list:
    """Returns the requested team's statistics, team bans, and champions played in a match.

    Args:
        team: A string that requests either the 'red' team or the 'blue' team
        match: A Cassiopeia (Riot API wrapper) Match object to query statistics from
    """
    # This is used as a shorthand to type less
    if team == 'red':
        team = match.red_team
    elif team == 'blue':
        team = match.blue_team
    else:
        raise ValueError("Unknown team color given (must pick 'red' or 'blue').")

    team_info = [match.id, match.version, team.side.name, team.win]
    bans = [ban.name if ban is not None else "" for ban in team.bans]
    players = [participant.champion.name for participant in team.participants]
    team_stats = [team.tower_kills, team.inhibitor_kills, team.dragon_kills,
                  team.rift_herald_kills, team.baron_kills, team.first_tower,
                  team.first_inhibitor, team.first_dragon, team.first_rift_herald,
                  team.first_baron]

    team_info.extend(bans)
    team_info.extend(players)
    team_info.extend(team_stats)
    return team_info


def get_match_records(filename: str, start_id: int, max_records: int, sleep_time: int) -> None:
    """Retrieves the first n match records that are valid and is also a '5v5 ranked solo queue' game mode
    from the Riot API.

    Args:
        filename: Name of the file to save the League of Legends match records
        start_id: Match ID to begin looking from (will decrement from said ID number)
        max_records: Total number of successful records to be retrieved
        sleep_time: Number of seconds to wait between each API call

    Returns:
        Does not return anything. However, the data will be written to the filename as specified.
    """
    # Remember to remove the API key when pushing commits to GitHub
    cassiopeia.set_riot_api_key('RGAPI-KEY-GOES-HERE')
    cassiopeia.set_default_region('NA')

    # Iterate matches by ID number and only store matches that are of the "5v5 solo queue ranked" game mode
    read_records = 0
    current_id = start_id
    while read_records < max_records:
        # Cassiopeia API wrapper handles rate-limiting, but apparently its not suited for a personal API key
        time.sleep(sleep_time)

        match = cassiopeia.get_match(current_id)
        if not match.exists:
            print(f"Match ID {match.id} does not exist.")
        elif match.mode != cassiopeia.data.GameMode.classic or match.queue != cassiopeia.data.Queue.ranked_solo_fives:
            print(f"Match ID {match.id} does not match criteria of '5v5 ranked solo queue'.")
        else:
            print(f"Match ID {match.id} added. ({read_records + 1} matches out of {max_records} saved to disk) ")

            # a+ is similar to r+ to read and write to a file, but a+ also creates the file if it is missing and
            # appends additional text to the end of the file
            with open(filename, 'a+', newline='', encoding='utf-8') as file:
                csv_writer = csv.writer(file)
                # Write header once at the beginning of the file
                if read_records == 0:
                    csv_writer.writerow(["id", "version", "side", "win", "ban1", "ban2", "ban3", "ban4", "ban5",
                                         "champion1", "champion2", "champion3", "champion4", "champion5",
                                         "tower_kills", "inhibitor_kills", "dragon_kills", "rift_herald_kills",
                                         "baron_kills", "first_tower", "first_inhibitor", "first_dragon",
                                         "first_rift_herald", "first_baron"])

                # Write blue team information into csv
                bteam_info = get_team_stats('blue', match)
                csv_writer.writerow(bteam_info)

                # Write red team information into csv
                rteam_info = get_team_stats('red', match)
                csv_writer.writerow(rteam_info)
            read_records += 1  # This should be in the else statement
        current_id -= 1  # This should not be within the else statement


def main():
    """Main driver program to get match data from the Riot API. It retrieves match data by picking a set
    starting match ID, then decrementing the ID until n successful records have been found.

    The following command line arguments are required, in this order:
        filename: The name of the file to save the retrieved records
        start_id: The starting match ID to start searching from
        max_records: The number of successfully retrieved records to be saved into the file

    Note:
        The Riot API can only look up matches via a summoner name or match ID.
        The numerical structure of match IDs cannot be constructed from a pattern.
    """
    # Error checking for correct command line argument usage
    if len(sys.argv) != 4:
        raise ValueError('Number of arguments given in the command line mismatch the required amount.')

    # Global variables
    try:
        filename = str(sys.argv[1])
        start_id = int(sys.argv[2])
        max_records = int(sys.argv[3])
        sleep_time = 3
    except ValueError:
        raise ValueError('Invalid starting match ID or max number of records.')

    # Error checking for the filename
    if os.path.exists(filename):
        raise OSError(f'{filename} already exists. Terminating to prevent data from being overwritten.')
    else:
        print(f'Creating {filename} in the current directory.')
        get_match_records(filename, start_id, max_records, sleep_time)
        print(f'Successfully retrieved {max_records} records and saved to {filename}.')


if __name__ == '__main__':
    main()
