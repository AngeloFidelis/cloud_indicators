CREATE OR REPLACE VIEW `lookerstudylab.views.all_projects` AS
WITH old_projects AS (
  SELECT 
    *,
    FORMAT_DATE("%Y", start) AS start_year,
    FORMAT_DATE("%Y", `end`) AS end_year,
    FORMAT_DATE("%b", start) AS start_month,
    format_date("%m", `end`) as end_month,
    CONCAT("Q", FORMAT_DATE('%Q', start)) AS start_quarter,
    CONCAT("Q", FORMAT_DATE('%Q', `end`)) AS end_quarter
  FROM `lookerstudylab.cloud_indicators.old_projects`
), current_projects AS (
  SELECT 
    * EXCEPT(google_calendar_event),
    FORMAT_DATE("%Y", start) AS start_year,
    FORMAT_DATE("%Y", `end`) AS end_year,
    FORMAT_DATE("%b", start) AS start_month,
    format_date("%m", `end`) as end_month,
    CONCAT("Q", FORMAT_DATE('%Q', start)) AS start_quarter,
    CONCAT("Q", FORMAT_DATE('%Q', `end`)) AS end_quarter
  FROM `lookerstudylab.cloud_indicators.current_projects`
), concat_data AS (
  SELECT * FROM old_projects
  UNION ALL
  SELECT * FROM current_projects
)

SELECT 
  * EXCEPT(duplicate, priority),
  -- Melhora a visualização da coluna 'priority'
  CASE 
    WHEN
      priority IS NULL OR priority = "N/A"
    THEN
      "No Priority"
    ELSE 
      priority 
  END AS priority,
  -- Cria uma coluna que diz se o cliente é novo ou de base
  CASE 
    WHEN 
      ROW_NUMBER() OVER (PARTITION BY customer ORDER BY start) = 1 
    THEN 'New Customer' 
    ELSE 'Base Customer' 
  END AS customer_type
FROM (
  SELECT 
    *,
    -- Cria uma coluna que checa se há dados duplicados, e se houver, o valor da coluna vai ser maior que 1
    ROW_NUMBER() OVER (PARTITION BY opt, customer, project_name ORDER BY start DESC) AS duplicate
  FROM concat_data
) AS all_data
WHERE 
  duplicate = 1
  AND status <> 'Lost'
  AND status <> 'Cancelled'
  AND status <> 'Hold'
  AND start IS NOT null
  AND opt <> 'interno'
  AND project_name NOT LIKE '%TechHub%'
