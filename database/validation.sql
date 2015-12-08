CREATE FUNCTION is_born(target_person_id int, target_date date) RETURNS boolean AS $$
	BEGIN
		RETURN EXISTS(
			SELECT 1
			FROM person
			WHERE
				person_id = target_person_id AND
				target_date >= dob
		);
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION validate_born(
	target_person_id int, target_date date, error_text text
) RETURNS void AS $$
	BEGIN
		IF NOT is_born(target_person_id, target_date) THEN
			RAISE EXCEPTION '%s', error_text;
		END IF;
		RETURN;
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION is_team_during_date(target_team_id int, target_start_date date) RETURNS boolean AS $$
	BEGIN
		RETURN EXISTS(
			SELECT 1
			FROM team
			WHERE
				team_id = target_team_id AND
				target_start_date BETWEEN start_date AND end_date
		);
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION validate_team_during_date(
	target_team_id int, target_start_date date, error_text text
) RETURNS void AS $$
	BEGIN
		IF NOT is_team_during_date(target_team_id, target_start_date) THEN
			RAISE EXCEPTION '%s', error_text;
		END IF;
		RETURN;
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION is_date_overlap(start1 date, end1 date, start2 date, end2 date) RETURNS boolean AS $$
	BEGIN
		RETURN (
			start1 BETWEEN start2 AND end2 OR
			end1 BETWEEN start2 AND end2
		);
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION is_time_overlap(start1 time, end1 time, start2 time, end2 time) RETURNS boolean AS $$
	BEGIN
		RETURN (
			start1 BETWEEN start2 AND end2 OR
			end1 BETWEEN start2 AND end2
		);
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION check_team_name_dates() RETURNS trigger AS $$
	DECLARE
		i RECORD;
	BEGIN
		SELECT validate_team_during_date(
			NEW.team_id, NEW.start_date,
			'Team name date range extends outside team operating period'
		);
		FOR i IN
			SELECT start_date, end_date FROM team_name WHERE team_id = NEW.team_id
		LOOP
			IF is_date_overlap(i.start_date, i.end_date, start_date, end_date) THEN
				RAISE EXCEPTION 'Team name periods overlap';
			END IF;
		END LOOP;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER team_name_dates_check
BEFORE INSERT OR UPDATE ON team_name
FOR EACH ROW EXECUTE PROCEDURE check_team_name_dates();

CREATE FUNCTION check_uniform_dates() RETURNS trigger AS $$
	BEGIN
		SELECT validate_team_during_date(
			NEW.team_id, NEW.start_date,
			'Uniform usage extends outside team operating period'
		);
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER uniform_dates_check
BEFORE INSERT OR UPDATE ON uniform
FOR EACH ROW EXECUTE PROCEDURE check_uniform_dates();

CREATE FUNCTION check_person_weight_dates() RETURNS trigger AS $$
	BEGIN
		SELECT validate_born(
			NEW.person_id, NEW.weight_date,
			'Weight recorded before person is born'
		);
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER person_weight_check
BEFORE INSERT OR UPDATE ON person_weight
FOR EACH ROW EXECUTE PROCEDURE check_person_weight_dates();

CREATE FUNCTION check_injury_dates() RETURNS trigger AS $$
	BEGIN
		SELECT validate_born(
			NEW.person_id, NEW.injury_date,
			'Injury occurs before person is born'
		);
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER injury_check
BEFORE INSERT OR UPDATE ON injury
FOR EACH ROW EXECUTE PROCEDURE check_injury_dates();

CREATE FUNCTION check_contract_dates() RETURNS trigger AS $$
	BEGIN
		SELECT validate_team_during_date(
			NEW.team_id, NEW.start_date,
			'Contract dates extend outside team operating period'
		);
		SELECT validate_born(
			NEW.person_id, NEW.start_date,
			'Contract starts before person is born'
		);
		IF has_date_overlap(
			'contract', 'person_id', NEW.person_id,
			NEW.start_date, NEW.end_date
		) THEN
			RAISE EXCEPTION 'Contract periods overlap';
		END IF;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER contract_check
BEFORE INSERT OR UPDATE ON contract
FOR EACH ROW EXECUTE PROCEDURE check_contract_dates();

-- validate CONTRACT during date.
-- use on game_event, penalty tables, maybe others?
-- instead of checking to see whether player was active on the ice
CREATE FUNCTION check_position_dates() RETURNS trigger AS $$
	DECLARE
		i RECORD;
	BEGIN
		SELECT validate_team_during_date(
			NEW.team_id, NEW.start_date,
			'Position date extends outside team operating period'
		);
		SELECT validate_born(
			NEW.person_id, NEW.start_date,
			'Position starts before person is born'
		);
		-- a person CAN have multiple positions at the same time
		
		-- ensure unique team-line-position in time
		FOR i IN
			SELECT start_date, end_date
			FROM position
			WHERE
				team_id = NEW.team_id AND
				line_number = NEW.line_number AND
				position_type_id = NEW.position_type_id
		LOOP
			IF is_date_overlap(i.start_date, i.end_date, NEW.start_date, new.end_date) THEN
				RAISE EXCEPTION 'The same team-line-position combination already exists during this time period.';
			END IF;
		END LOOP;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER position_check
BEFORE INSERT OR UPDATE ON position
FOR EACH ROW EXECUTE PROCEDURE check_position_dates();

-- I expect lots of null stadium and uniform information here
-- Must test to ensure nulls are allowed through trigger
CREATE FUNCTION check_game_dates() RETURNS trigger AS $$
	DECLARE
		i RECORD;
	BEGIN
		-- both teams exist during game
		SELECT validate_team_during_date(
			NEW.home_team_id, NEW.game_start_time, -- may have to cast datetime to date?
			'Home team does not exist at time of game'
		);
		SELECT validate_team_during_date(
			NEW.away_team_id, NEW.game_start_time,
			'Away team does not exist at time of game'
		);
		-- both uniforms are in use
		IF NOT EXISTS(
			SELECT 1
			FROM uniform
			WHERE
				team_id = NEW.home_team_id AND
				uniform_id = NEW.home_uniform_id AND
				NEW.game_start_time BETWEEN start_date AND end_date
		) THEN
			RAISE EXCEPTION 'Home uniform does not belong to home team and exist at game time';
		END IF;
		IF NOT EXISTS(
			SELECT 1
			FROM uniform
			WHERE
				team_id = NEW.away_team_id AND
				uniform_id = NEW.away_uniform_id AND
				NEW.game_start_time BETWEEN start_date AND end_date
		) THEN
			RAISE EXCEPTION 'Away uniform does not belong to home team and exist at game time';
		END IF;
		
		-- stadium is available
		IF NOT EXISTS(
			SELECT 1
			FROM stadium
			WHERE
				stadium_id = NEW.stadium_id AND
				NEW.game_start_time BETWEEN start_date AND end_date
		) THEN
			RAISE EXCEPTION 'Stadium does not exist at time of game';
		END IF;
		FOR i IN
			SELECT game_start_time, game_end_time
			FROM game
			WHERE stadium_id = NEW.stadium_id
		LOOP
			IF is_date_overlap(i.game_start_time, i.game_end_time, NEW.game_start_time, NEW.game_end_time) THEN
				RAISE EXCEPTION 'Stadium is already in use during this time.';
			END IF;
		END LOOP;
		
		-- neither team is playing a game already
		FOR i IN
			SELECT game_start_time, game_end_time
			FROM game
			WHERE (
					NEW.home_team_id = home_team_id OR
					NEW.home_team_id = away_team_id
				)
		LOOP
			IF is_date_overlap(i.game_start_time, i.game_end_time, NEW.game_start_time, NEW.game_end_time) THEN
				RAISE EXCEPTION 'The home team is playing another game during this time.';
			END IF;
		END LOOP;
		FOR i IN
			SELECT game_start_time, game_end_time
			FROM game
			WHERE (
					NEW.away_team_id = home_team_id OR
					NEW.away_team_id = away_team_id
				)
		LOOP
			IF is_date_overlap(i.game_start_time, i.game_end_time, NEW.game_start_time, NEW.game_end_time) THEN
				RAISE EXCEPTION 'The away team is playing another game during this time.';
			END IF;
		END LOOP;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER game_check
BEFORE INSERT OR UPDATE ON game
FOR EACH ROW EXECUTE PROCEDURE check_game_dates();

-- this will cause problems if contracts aren't documented
-- must allow for nulls!
-- probably just omit some of these checks to resolve
CREATE FUNCTION check_shift_times() RETURNS trigger AS $$
	DECLARE
		i RECORD;
	BEGIN
		-- ensure player is on team during game
		IF NOT EXISTS(
			SELECT 1
			FROM game
			INNER JOIN contract ON (
				contract.team_id IN (game.home_team_id, game.away_team_id) AND
				contract.person_id = NEW.person_id
			)
			WHERE game.game_id = NEW.game_id
		) THEN
			RAISE EXCEPTION 'Player not contracted to a team playing in this game';
		END IF;
		
		-- ensure player did not already have shift
		FOR i IN
			SELECT start_time, end_time
			FROM shift
			WHERE
				game_id = NEW.game_id AND
				person_id = NEW.person_id AND
				period = NEW.period
		LOOP
			IF is_time_overlap(i.start_time, i.end_time, NEW.start_time, NEW.end_time) THEN
				RAISE EXCEPTION 'This shift overlaps with an existing shift for the same person';
			END IF;
		END LOOP;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER shift_check
BEFORE INSERT OR UPDATE ON shift
FOR EACH ROW EXECUTE PROCEDURE check_shift_times();

CREATE FUNCTION is_on_shift(
	target_player_id int, target_game_id int, target_period int, target_shot_time time)
RETURNS boolean AS $$
	BEGIN
		RETURN EXISTS(
			SELECT 1
			FROM shift
			WHERE
				player_id = target_player_id AND
				game_id = target_game_id AND
				period = target_period AND
				target_shot_time BETWEEN start_time AND end_time 
		);
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION validate_on_shift(
	target_player_id int, target_game_id int, target_period int, target_shot_time time, error_text text)
RETURNS void AS $$
	BEGIN
		IF NOT is_on_shift(
			target_player_id, target_game_id, target_period, target_shot_time
		) THEN
			RAISE EXCEPTION '%s', error_text;
		END IF;
		RETURN;
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION check_shot_times() RETURNS trigger AS $$
	BEGIN
		-- was player, assist1, assist2, goalie on shift at the time?
		SELECT validate_on_shift(
			NEW.shooter_id, NEW.game_id, NEW.period, NEW.shot_time,
			'Shooter is not on shift during shot'
		);
		SELECT validate_on_shift(
			NEW.assist1_id, NEW.game_id, NEW.period, NEW.shot_time,
			'First assist player is not on shift during shot'
		);
		SELECT validate_on_shift(
			NEW.assist2_id, NEW.game_id, NEW.period, NEW.shot_time,
			'Second assist player is not on shift during shot'
		);
		SELECT validate_on_shift(
			NEW.goalie_id, NEW.game_id, NEW.period, NEW.shot_time,
			'Goalie is not on shift during shot'
		);
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER shot_check
BEFORE INSERT OR UPDATE ON shot
FOR EACH ROW EXECUTE PROCEDURE check_shot_times();

-- a player not on shift could still be source or target of penalty
-- should check if in game instead
CREATE FUNCTION check_penalty_times() RETURNS trigger AS $$
	BEGIN
		SELECT validate_on_shift(
			NEW.source_person_id, NEW.game_id, NEW.period, NEW.penalty_time,
			'Player that was source of penalizing act not on shift at the time.'
		);
		SELECT validate_on_shift(
			NEW.target_person_id, NEW.game_id, NEW.period, NEW.penalty_time,
			'Player that was target of penalizing act not on shift at the time.'
		);
		IF NOT EXISTS(
			SELECT 1
			FROM game_official
			WHERE
				game_id = NEW.game_id AND
				person_id = NEW.game_official_id
		) THEN
			RAISE EXCEPTION 'Official making penalty was not officiating this game.';
		END IF;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

-- a player not on shift could still be actor or casualty of event
-- should check if in game instead
CREATE FUNCTION check_game_event_times() RETURNS trigger AS $$
	BEGIN
		SELECT validate_on_shift(
			NEW.actor_id, NEW.game_id, NEW.period, NEW.event_time,
			'Player that was primary actor of event not on shift at the time.'
		);
		SELECT validate_on_shift(
			NEW.casualty_id, NEW.game_id, NEW.period, NEW.event_time,
			'Player that was casualty of event not on shift at the time.'
		);
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER game_event_check
BEFORE INSERT OR UPDATE ON game_event
FOR EACH ROW EXECUTE PROCEDURE check_game_event_times();

CREATE TRIGGER penalty_check
BEFORE INSERT OR UPDATE ON penalty
FOR EACH ROW EXECUTE PROCEDURE check_penalty_times();

CREATE FUNCTION check_shootout() RETURNS trigger AS $$
	DECLARE
		shootout_required boolean;
	BEGIN
		-- ensure player is on team during game
		IF NOT EXISTS(
			SELECT 1
			FROM game
			INNER JOIN contract ON (
				contract.team_id = game.home_team_id AND
				contract.player_id = NEW.home_player_id
			)
		) THEN
			RAISE EXCEPTION 'Home player not contracted to the home team in this shootout round';
		END IF;
		IF NOT EXISTS(
			SELECT 1
			FROM game
			INNER JOIN contract ON (
				contract.team_id = game.away_team_id AND
				contract.player_id = NEW.away_player_id
			)
		) THEN
			RAISE EXCEPTION 'Away player not contracted to the away team in this shootout round';
		END IF;
		
		-- ensure game was tied (at point of shootout) or a win by 1 (end of game)
		SELECT (abs(home_score - away_score) <= 1) INTO shootout_required
		FROM game
		WHERE
			game.game_id = NEW.game_id AND
			game.season_id IN (1,2); -- no shootouts in the playoffs
		IF NOT shootout_required THEN
			RAISE EXCEPTION 'Shootout for a game that was not tied';
		END IF;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER shootout_check
BEFORE INSERT OR UPDATE ON shot
FOR EACH ROW EXECUTE PROCEDURE check_shootout();
