CREATE OR REPLACE VIEW `lookerstudylab.views.all_projects` AS
WITH consultants_current_projects AS (
  SELECT 
    * EXCEPT(dependence)
  FROM `lookerstudylab.cloud_indicators.current_projects_consultants`
), consultants_old_projects AS (
  SELECT 
    *
  FROM `lookerstudylab.cloud_indicators.old_projects_consultants`
), concat_data AS (
  SELECT * FROM consultants_current_projects
  UNION ALL 
  SELECT * FROM consultants_old_projects
)

SELECT 
  * EXCEPT(duplicate)
FROM (
  SELECT 
    *,
    ROW_NUMBER () OVER (PARTITION BY id_project, role, consultant, schedule_start) AS duplicate
  FROM concat_data
) AS all_data
WHERE
  duplicate = 1