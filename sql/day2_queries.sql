-- Read all events.
SELECT * FROM events;

-- Filter events by status.
SELECT *
FROM events
WHERE status = 'scheduled';

-- Practise a LEFT JOIN and aggregation.
SELECT u.display_name, COUNT(t.id) AS tip_count
FROM users AS u
LEFT JOIN tips AS t ON t.user_id = u.id
GROUP BY u.id, u.display_name
ORDER BY u.display_name;

-- Inspect the relationships behind each tip.
SELECT
    t.id AS tip_id,
    u.display_name,
    e.starts_at,
    predicted_team.name AS predicted_winner
FROM tips AS t
JOIN users AS u ON u.id = t.user_id
JOIN events AS e ON e.id = t.event_id
JOIN teams AS predicted_team ON predicted_team.id = t.predicted_winner_team_id
ORDER BY t.id;

-- Use a transaction while practising writes so they can be rolled back.
BEGIN;

UPDATE events
SET status = 'completed'
WHERE id = 1;

DELETE FROM tips
WHERE id = 10;

ROLLBACK;
