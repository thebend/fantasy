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
	weight int NOT NULL CHECK (weight > 0),
	PRIMARY KEY (person_id, weight_date)
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
	return_to_practice date CHECK (return_to_practice >= injury_date),
	return_to_game date CHECK (return_to_game >= return_to_practice) --could be inferred from actual game data
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
	end_date date CHECK (end_date > start_date)
);

CREATE TABLE stadium (
	stadium_id serial PRIMARY KEY,
	city_id int NOT NULL REFERENCES city,
	stadium_name varchar(100) NOT NULL,
	capacity int CHECK (capacity > 0),
	start_date date,
	end_date date CHECK (end_date > start_date)
);

CREATE TABLE season (
	season_id serial PRIMARY KEY,
	season_code varchar(10) NOT NULL UNIQUE,
	season_description varchar(100) NOT NULL UNIQUE
);
INSERT INTO season (season_id, season_code, season_description) VALUES
(1,'1','Pre-Season'),
(2,'2','Regular Season'),
(3,'3','Playoffs');

CREATE TABLE game (
	game_id serial PRIMARY KEY,
	game_number int CHECK (game_number > 0),
	season_id int NOT NULL REFERENCES season,
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

-- if just hockey, could fix columns for each official position
-- to the game table.  referee_1, referee_2, lineman_1, lineman_2?
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

-- should consider breaking up SQL by table and related data rather than by type
-- eg. penalty table with validation triggers, views
\i database/views.sql
\i database/validation.sql
\i database/tests.sql