CREATE OR REPLACE VIEW `lookerstudylab.views.critical_analysis` AS
SELECT 
  DISTINCT
    ap.*,
    ARRAY_AGG(
      STRUCT(
        pc.consultant as consultants,
        pc.role as role,
        pc.allocation as allocation,
        pc.working_days as working_days,
        pc.schedule_start as schedule_start,
        pc.schedule_end as schedule_end
      )
    ) as consultants_data
FROM `lookerstudylab.views.all_projects` ap
LEFT JOIN `lookerstudylab.views.all_projects_consultants` pc
ON ap.id_project = pc.id_project
GROUP BY ALL