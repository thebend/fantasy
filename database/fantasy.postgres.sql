;-- ignore first command because of UTF byte order mark file prefix in file corrupting it

DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

CREATE TYPE gender_type AS ENUM ('male','female','other');

CREATE TABLE team (
	team_id serial PRIMARY KEY,
	start_date date NOT NULL,
	end_date date CHECK (end_date > start_date)
);

CREATE TABLE team_name (
	team_name_id serial PRIMARY KEY,
	team_id int NOT NULL REFERENCES team,
	start_date date NOT NULL,
	end_date date CHECK (end_date > start_date),
	team_name varchar(100) NOT NULL,
	
	-- team codes are always capitalized
	team_code char(3) NOT NULL CHECK (team_code = upper(team_code))
);


-- team codes not necessarily unique over time
-- but are unique for any specific point in time
-- 
-- think I could be making too many indexes
-- but this is a high-query database, so I don't know?
-- must read up on best practices
CREATE INDEX ON team_name USING hash (team_code);
CREATE INDEX ON team_name USING hash (team_name);

CREATE TABLE logo (
	logo_id serial PRIMARY KEY,
	team_id int NOT NULL REFERENCES team,
	logo_name varchar(100) UNIQUE NOT NULL,
	logo bytea UNIQUE NOT NULL
);
CREATE INDEX ON logo USING hash (logo);

CREATE TABLE uniform_type (
	uniform_type_id serial PRIMARY KEY,
	type_description varchar(100) UNIQUE
);
INSERT INTO uniform_type (uniform_type_id, type_description) VALUES
(1,'Home'),
(2,'Away'),
(3,'Legacy');

CREATE TABLE uniform (
	uniform_id serial PRIMARY KEY,
	team_id int NOT NULL REFERENCES team,
	start_date date NOT NULL,
	end_date date,
	
	-- rgb(255,255,255) format
	primary_red smallint,
	primary_green smallint,
	primary_blue smallint,
	secondary_red smallint,
	secondary_green smallint,
	secondary_blue smallint,
	
	uniform_type_id int NOT NULL REFERENCES uniform_type,
	uniform_description varchar(100),
	uniform_image bytea UNIQUE
);

CREATE TABLE logo_usage (
	logo_id int NOT NULL REFERENCES logo,
	start_date date NOT NULL,
	end_date date CHECK (end_date > start_date),
	PRIMARY KEY (logo_id, start_date)
);

CREATE TABLE city (
	city_id serial PRIMARY KEY,
	city_name varchar(100) NOT NULL,
	time_zone char(3) NOT NULL
);

CREATE TABLE city_population (
	city_id int NOT NULL REFERENCES city,
	population_date date NOT NULL,
	population int NOT NULL CHECK (population > 0),
	PRIMARY KEY (city_id, population_date)
);

CREATE TABLE team_city (
	team_id int NOT NULL REFERENCES team,
	city_id int NOT NULL REFERENCES city,
	start_date date NOT NULL,
	end_date date CHECK (end_date > start_date)
);

CREATE TABLE person (
	person_id serial PRIMARY KEY,
	dob date NOT NULL,
	home_city_id int NOT NULL REFERENCES city,
	first_name varchar(100) NOT NULL,
	last_name varchar(100) NOT NULL,
	height int NOT NULL CHECK (height > 0),
	gender gender_type NOT NULL DEFAULT 'male'
);

CREATE TABLE person_weight (
	person_id int NOT NULL REFERENCES person,
	weight_date date,
	weight int NOT NULL CHECK (weight > 0)
);

CREATE TABLE injury_category (
	injury_category_id serial PRIMARY KEY,
	injury_category_name varchar(100)
);
-- could categorize injuries by cut, bruise, strain, break
-- by fight, boards, puck...
INSERT INTO injury_category (injury_category_id, injury_category_name) VALUES
(1,'Other'),
(2,'Pulled Muscle'),
(3,'Broken Bone');

-- this can grow indefinitely, with hierarchies in multiple categories
-- must determine what data is available and design accordingly
CREATE TABLE injury_type (
	injury_type_id serial PRIMARY KEY,
	injury_name varchar(100),
	-- can be null.  Others can't.  Probably require not null reference for this
	injury_category_id int DEFAULT 1 REFERENCES injury_category
);

CREATE TABLE injury (
	injury_id serial PRIMARY KEY,
	person_id int NOT NULL REFERENCES person,
	injury_date date NOT NULL,
	injury_type_id int REFERENCES injury_type,
	severity int CHECK (severity > 0), 
	return_to_practice date,
	return_to_game date --could be inferred from actual game data
);

-- could track contract extensions?
CREATE TABLE contract (
	contract_id serial PRIMARY KEY,
	person_id int REFERENCES person,
	team_id int REFERENCES team,
	start_date date NOT NULL,
	end_date date CHECK (end_date > start_date),
	--ensure start date, end_date is not between other contract dates
	player_number int NOT NULL CHECK (player_number > 0)
);

CREATE TABLE position_category (
	position_category_id serial PRIMARY KEY,
	position_category_name varchar(100)
);
INSERT INTO position_category (position_category_id, position_category_name) VALUES
(1,'Offense'),
(2,'Defense'),
(3,'Goalie');

CREATE TABLE position_type (
	position_type_id serial PRIMARY KEY,
	position_name varchar(100) UNIQUE NOT NULL,
	position_abbr varchar(4) UNIQUE NOT NULL,
	position_category_id int NOT NULL REFERENCES position_category
);
INSERT INTO position_type (position_type_id, position_name, position_abbr, position_category_id) VALUES
(1,'Left Wing',    'LW',1),
(2,'Center',       'C', 1),
(3,'Right Wing',   'RW',1),
(4,'Defense Left', 'DL',2),
(5,'Defense Right','DR',2),
(6,'Goalie',       'G', 3);

CREATE TABLE position (
	position_id serial PRIMARY KEY,
	person_id int REFERENCES person,
	team_id int REFERENCES team,
	line_number int NOT NULL CHECK (line_number > 0),
	position_type_id int REFERENCES position,
	start_date date NOT NULL,
	end_date date CHECK (end_date > start_date),
	UNIQUE (team_id, line_number, position_id, start_date)
);

CREATE TABLE stadium (
	stadium_id serial PRIMARY KEY,
	city_id int NOT NULL REFERENCES city,
	stadium_name varchar(100) NOT NULL,
	capacity int CHECK (capacity > 0)
);

CREATE TABLE game (
	game_id serial PRIMARY KEY,
	home_team_id int NOT NULL REFERENCES team,
	away_team_id int NOT NULL REFERENCES team CHECK (home_team_id != away_team_id),
	home_uniform_id int REFERENCES uniform,
	away_uniform_id int REFERENCES uniform,
	stadium_id int REFERENCES stadium,
	start_time timestamp with time zone NOT NULL,
	end_time timestamp with time zone CHECK (end_time > start_time),
	attendance int CHECK (attendance >= 0),
	--could be inferred from game event data
	home_score int CHECK (home_score >= 0),
	away_score int CHECK (away_score >= 0),
	
	UNIQUE (home_team_id, start_time),
	UNIQUE (home_team_id, end_time),
	UNIQUE (away_team_id, start_time),
	UNIQUE (away_team_id, end_time)
);

CREATE TABLE event_type (
	event_type_id serial PRIMARY KEY,
	event_name varchar(100) UNIQUE NOT NULL
);
INSERT INTO event_type (event_type_id, event_name) VALUES
(1,'Hit'),
(2,'Giveaway'),
(3,'Takeaway'),
(4,'Faceoff');

CREATE TABLE game_event (
	event_id serial PRIMARY KEY,
	game_id int NOT NULL REFERENCES game,
	period int NOT NULL CHECK (period > 0),
	event_time time NOT NULL,
	event_type_id int NOT NULL REFERENCES event_type,
	-- player that "won" the exchange (hit someone, won faceoff, etc.)
	actor_id int NOT NULL REFERENCES person,
	-- the player that "lost" the exchange
	casualty_id int REFERENCES person
);
-- need solution for whole-team events.  I think.
-- could just add actor_team_id, casualty_team_id here?

CREATE TABLE shot_type (
	shot_type_id serial PRIMARY KEY,
	shot_name varchar(100) UNIQUE NOT NULL
);
INSERT INTO shot_type (shot_type_id, shot_name) VALUES
(1,'Slapshot'),
(2,'Wristshot'),
(3,'Backhand');

CREATE TABLE shot (
	shot_id serial PRIMARY KEY,
	game_id int NOT NULL REFERENCES game,
	period int NOT NULL CHECK (period > 0),
	shot_time time NOT NULL,
	shot_type_id int REFERENCES shot_type,
	shooter_id int NOT NULL REFERENCES person,
	assist1_id int REFERENCES person,
	assist2_id int REFERENCES person,
	--can be inferred elsewhere
	goalie_id int NOT NULL REFERENCES person,
	goal boolean NOT NULL DEFAULT FALSE
);

CREATE TABLE role_type (
	role_type_id serial PRIMARY KEY,
	role_type_name varchar(100) UNIQUE NOT NULL
);
INSERT INTO role_type (role_type_id, role_type_name) VALUES
(1,'Referee'),
(2,'Linesman');
-- are there others?  eg. commissioner

CREATE TABLE official_role (
	role_id serial PRIMARY KEY,
	role_name varchar(100) NOT NULL,
	role_type int NOT NULL REFERENCES role_type
);
INSERT INTO official_role (role_id, role_name, role_type) VALUES
(1,'Head Referee',     1),
(2,'Secondary Referee',1),
-- are these home/away, north/south?...
(3,'Left Linesman',    2),
(4,'Right Linesman',   2);

CREATE TABLE game_official (
	game_official_id serial PRIMARY KEY,
	game_id int NOT NULL REFERENCES game,
	role_id int NOT NULL REFERENCES official_role,
	person_id int NOT NULL REFERENCES person,
	UNIQUE (game_id, role_id),
	UNIQUE (game_id, person_id)
);

CREATE TABLE shift (
	shift_id serial PRIMARY KEY,
	game_id int REFERENCES game,
	person_id int REFERENCES person,
	period int NOT NULL CHECK (period > 0),
	start_time time NOT NULL,
	end_time time CHECK (end_time > start_time)
);

-- create compound period/time datatype? 
CREATE TABLE shootout (
	game_id int REFERENCES game,
	round_number int NOT NULL CHECK (round_number > 0),
	home_player_id int REFERENCES person,
	away_player_id int REFERENCES person,
	home_score boolean NOT NULL,
	away_score boolean NOT NULL,
	PRIMARY KEY (game_id, round_number)
);

CREATE TABLE penalty_category (
	penalty_category_id serial PRIMARY KEY,
	category_name varchar(100) NOT NULL UNIQUE	,
	penalty_minutes int NOT NULL CHECK (penalty_minutes > 0)
);
INSERT INTO penalty_category (penalty_category_id, category_name, penalty_minutes) VALUES
(1,'Minor',          2),
(2,'Double Minor',   4),
(3,'Major',          5),
(4,'Misconduct',     10),
(5,'Game Misconduct',10),
(6,'Match',          10);
CREATE TABLE penalty_type (
	penalty_type_id serial PRIMARY KEY,
	penalty_category_id int REFERENCES penalty_category,
	penalty_name varchar(100) NOT NULL UNIQUE
);
-- find a comprehensive list
-- ensure I have modelled it correctly
INSERT INTO penalty_type (penalty_type_id, penalty_category_id, penalty_name) VALUES
(1,1,'Roughing'),
(2,1,'High Sticking'),
(3,1,'Checking'),
(4,1,'Too Many Men'),
(5,2,'Fighting');
-- normal penalties can be modified if injury occurs.  Must capture this.

-- Suspensions?

CREATE TABLE penalty (
	penalty_id serial PRIMARY KEY,
	game_id int REFERENCES game,
	period int NOT NULL CHECK (period > 0),
	event_time time NOT NULL,
	penalty_type_id int REFERENCES penalty_type,
	source_person_id int REFERENCES person,
	target_person_id int REFERENCES person,
	source_team_id int REFERENCES team,
	target_team_id int REFERENCES team,
	game_official_id int REFERENCES game_official
);

-- must define useful views
-- eg. right now game_event links to player
-- must tie player to contract to team for a given date
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

CREATE FUNCTION is_date_overlap(start1 date, end1 date, start2 date, end2 date) RETURNS boolean AS $$
	BEGIN
		RETURN (
			start1 BETWEEN start2 AND end2 OR
			end1 BETWEEN start2 AND end2
		);
	END;
$$ LANGUAGE plpgsql;

-- automate testing process for these functions
CREATE FUNCTION has_date_overlap(
	tbl regclass,
	tbl_key text, search_key int,
	start_date date, end_date date
) RETURNS boolean AS $$
	DECLARE
		i RECORD; -- tbl%ROWTYPE
	BEGIN
		FOR i IN EXECUTE format(
			'SELECT start_date, end_date FROM %s WHERE %s = %s',
			tbl, tbl_key, search_key
		) LOOP
			IF is_date_overlap(i.start_date, i.end_date, start_date, end_date) THEN
				RETURN TRUE;
			END IF;
		END LOOP;
		RETURN FALSE;
	END;
$$ LANGUAGE plpgsql;

CREATE FUNCTION check_team_name_dates() RETURNS trigger AS $$
	BEGIN
		IF NOT is_team_during_date(NEW.team_id, NEW.start_date) THEN
			RAISE EXCEPTION 'Team name cannot be set outside team operating period';
		END IF;
		
		IF has_date_overlap(
			'team_name',
			'team_id', NEW.team_id,
			NEW.start_date, NEW.end_date
		) THEN
			RAISE EXCEPTION 'Team name cannot be set outside team operating period';
		END IF;
		RETURN NEW;
	END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER team_name_dates_check
BEFORE INSERT OR UPDATE ON team_name
FOR EACH ROW
EXECUTE PROCEDURE check_team_name_dates();

INSERT INTO team (team_id, start_date, end_date) VALUES 
(1, '2000-01-01', '2010-01-01');

-- A team name existing before the team
INSERT INTO team_name (team_id, team_name, team_code, start_date, end_date) VALUES
(1, 'Van99', 'VAN', '1999-01-01', null);

-- A team date overlapping another date
-- INSERT INTO team_name (team_id, team_name, team_code, start_date, end_date) VALUES
-- (1, 'Van2000', 'VAN', '2000-01-01', null),
-- (1, 'Van2001', 'VAN', '2001-01-01', null);
-- INSERT INTO team_name (team_id, team_name, team_code, start_date, end_date) VALUES
-- (1, 'VanOverlap','VAN','2000-06-01','2001-06-01');
