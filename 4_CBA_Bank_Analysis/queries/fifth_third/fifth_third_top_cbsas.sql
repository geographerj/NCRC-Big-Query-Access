-- Find top 10 CBSAs by Fifth Third home purchase originations (2018-2024)
-- With standard filters applied

SELECT 
    cbsa_code,
    COUNTIF(action_taken = '1') as total_originations
FROM `hdma1-242116.hmda.hmda`
WHERE lei = 'QFROUN1UWUYU0DVIWD51'  -- Fifth Third Bank
  AND activity_year BETWEEN 2018 AND 2024
  AND loan_purpose = '1'  -- Home Purchase only
  AND action_taken = '1'  -- Originations only
  AND cbsa_code IS NOT NULL
  AND cbsa_code != ''
  -- Standard HMDA filters
  AND occupancy_type = '1'  -- Owner-occupied
  AND reverse_mortgage != '1'  -- Not reverse mortgage
  AND construction_method = '1'  -- Site-built only
  AND total_units IN ('1', '2', '3', '4')  -- 1-4 unit properties
GROUP BY cbsa_code
ORDER BY total_originations DESC
LIMIT 10;


