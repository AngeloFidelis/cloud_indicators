CREATE OR REPLACE VIEW `lookerstudylab.views.all_projects` AS
WITH old_projects AS(
  SELECT 
    id_project,
    opt,
    customer,
    project_name,
    status,
    priority,
    workload,
    contract_type,
    start,
    `end`,
    CONCAT(UPPER(substring(region, 0,1)), LOWER(substring(region, 2))) AS region,
    cloud,
    roles_needed,
    working_days,
    hours,
    revenue,
    cost,
    margin,
    google_id,
    FORMAT_DATE("%Y", start) AS start_year,
    FORMAT_DATE("%Y", `end`) AS end_year,
    FORMAT_DATE("%b", start) AS start_month,
    CONCAT("Q", FORMAT_DATE('%Q', start)) AS start_quarter,
  FROM `lookerstudylab.cloud_indicators.actual_projects`
), actual_projects AS (
  SELECT 
    id_project,
    opt,
    customer,
    project_name,
    status, 
    CAST(NULL AS STRING) AS priority,  -- Adiciona uma coluna nula para "priority"
    workload,
    contract_type,
    start,
    `end`,
    CONCAT(UPPER(substring(region, 0,1)), LOWER(substring(region, 2))) AS region, 
    cloud,
    roles_needed,
    working_days,
    hours,
    revenue,
    cost,
    margin,
    google_id,
    FORMAT_DATE("%Y", start) AS start_year,
    FORMAT_DATE("%Y", `end`) AS end_year,
    FORMAT_DATE("%b", start) AS start_month,
    CONCAT("Q", FORMAT_DATE('%Q', start)) AS start_quarter,
  FROM `lookerstudylab.cloud_indicators.old_projects`
), concat_data AS (
  SELECT * FROM old_projects
  UNION ALL 
  SELECT * FROM actual_projects
)
SELECT
  * EXCEPT(priority),
  CASE 
    WHEN
      priority IS NULL OR priority = "N/A"
    THEN
      "No Priority"
    ELSE 
      priority 
  END AS priority,
  CASE 
    WHEN 
      ROW_NUMBER() OVER (PARTITION BY customer ORDER BY start) = 1 
    THEN 'New Customer' 
    ELSE 'Base Customer' 
  END AS customer_type
FROM concat_data 
WHERE 
  status <> 'Lost'
  AND status <> 'Cancelled'
  AND status <> 'Hold'
  AND start IS NOT null
  AND opt <> 'interno'
  AND project_name NOT LIKE '%TechHub%'