CREATE PROCEDURE q2chub.sp_get_root_opportunities (IN in_run_timestamp TIMESTAMP )
LANGUAGE SQL
DYNAMIC RESULT SETS 1
BEGIN
    DECLARE root_opp CURSOR WITH RETURN FOR
    SELECT DISTINCT root_oppty_num, level_num
    FROM q2chub.BUYING_EVENT_BOM
    WHERE
        ( create_ts > in_run_timestamp
        OR update_ts > in_run_timestamp );

    OPEN root_opp;

END