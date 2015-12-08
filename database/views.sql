-- must define useful views
-- eg. right now game_event links to player
-- must tie player to contract to team for a given date
-- currently inner joining contract, but that might not be available?
CREATE VIEW game_event_extended AS
SELECT
	game_event.event_id,
	game_event.game_id,
	actor.person_id AS actor_id,
	actor_contract.player_number AS actor_player_number,
	actor.first_name AS actor_first_name,
	actor.last_name AS actor_last_name,
	casualty.person_id AS casualty_id,
	casualty_contract.player_number AS casualty_player_number,
	casualty.first_name AS casualty_first_name,
	casualty.last_name AS casualty_last_name
FROM game_event
INNER JOIN game ON
	game_event.game_id = game.game_id
INNER JOIN person AS actor ON
	game_event.actor_id = actor.person_id
INNER JOIN contract as actor_contract ON
	actor.person_id = actor_contract.person_id AND
	game.start_time BETWEEN actor_contract.start_date AND actor_contract.end_date
LEFT JOIN person as casualty ON
	game_event.casualty_id = casualty.person_id
LEFT JOIN contract as casualty_contract ON
	casualty.person_id = casualty_contract.person_id AND
	game.start_time BETWEEN casualty_contract.start_date AND casualty_contract.end_date;

-- should create game summary table with total goals, penalties, etc.
CREATE VIEW game_summary AS
SELECT
	game.game_id,
	game.start_time,
	home_team_name.team_code AS home_team_code,
	away_team_name.team_code AS away_team_code,
	COUNT(*) as goals
FROM game
INNER JOIN team AS home_team ON
	game.home_team_id = home_team.team_id
INNER JOIN team_name AS home_team_name ON
	home_team_name.team_id = home_team.team_id AND
	game.start_time BETWEEN home_team_name.start_date AND home_team_name.end_date
INNER JOIN team AS away_team ON
	game.away_team_id = away_team.team_id
INNER JOIN team_name AS away_team_name ON
	away_team_name.team_id = away_team.team_id AND
	game.start_time BETWEEN away_team_name.start_date AND away_team_name.end_date
LEFT JOIN shot ON
	game.game_id = shot.game_id AND
	shot.goal
GROUP BY
	game.game_id,
	game.start_time,
	home_team_name.team_code,
	away_team_name.team_code
ORDER BY game.start_time DESC;
