SELECT 
  id_project,
  opt,
  customer,
  project_name,
  status,
  workload,
  contract_type,
  start,
  `end`,
  working_days,
  hours,
  revenue,
  cost,
  margin,
  region,
  cloud,
  google_id
FROM `lookerstudylab.cloud_indicators.actual_data_project`
UNION ALL
SELECT 
  id_project,
  opt,
  customer,
  project_name,
  status,
  workload,
  contract_type,
  start,
  `end`,
  working_days,
  hours,
  revenue,
  cost,
  margin,
  region,
  cloud,
  google_id
FROM `lookerstudylab.cloud_indicators.historical_data_project`
LIMIT 10;