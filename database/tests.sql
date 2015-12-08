INSERT INTO team (team_id, start_date, end_date) VALUES 
(1, '2000-01-01', '2010-01-01');

-- A team name existing before the team
-- INSERT INTO team_name (team_id, team_name, team_code, start_date, end_date) VALUES
-- (1, 'Van99', 'VAN', '1999-01-01', null);

-- A team date overlapping another date
-- INSERT INTO team_name (team_id, team_name, team_code, start_date, end_date) VALUES
-- (1, 'Van2000', 'VAN', '2000-01-01', null),
-- (1, 'Van2001', 'VAN', '2001-01-01', null);
-- INSERT INTO team_name (team_id, team_name, team_code, start_date, end_date) VALUES
-- (1, 'VanOverlap','VAN','2000-06-01','2001-06-01');
