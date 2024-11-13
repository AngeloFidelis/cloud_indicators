CREATE OR REPLACE VIEW `lookerstudylab.views.all_projects` AS
SELECT 
  id_project,
  role,
  consultant,
  schedule_start,
  schedule_end,
  billable,
  allocation,
  working_days,
  hours,
  cost_per_hour,
  cost
FROM `lookerstudylab.cloud_indicators.actual_projects_consultants`
UNION ALL
SELECT 
  id_project,
  role,
  consultant,
  schedule_start,
  schedule_end,
  billable,
  allocation,
  working_days,
  hours,
  cost_per_hour,
  cost
FROM `lookerstudylab.cloud_indicators.old_projects_consultants`