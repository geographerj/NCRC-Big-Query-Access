-- Subject Bank

-- Goal-Setting Analysis: Small Business Data Query
-- Subject Bank SB Respondent ID: 11813 (using 11813 for matching)
-- Assessment Area Counties: 142 counties
-- Years: 2020, 2021, 2022, 2023

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491']) as geoid5
),

filtered_sb_data AS (
    -- Filter SB data early: years, respondent ID, assessment area counties
    SELECT 
        CAST(d.year AS STRING) as year,
        d.msamd as cbsa_code,
        d.geoid5,
        -- SB Loans count (sum of all three size categories)
        (d.num_under_100k + d.num_100k_250k + d.num_250k_1m) as sb_loans_count,
        -- SB Loans amount (sum of all three size categories)
        (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m) as sb_loans_amount,
        -- LMICT flag: income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN 1 ELSE 0
        END as is_lmict,
        -- LMICT loans count (if is_lmict = 1, use sb_loans_count)
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.num_under_100k + d.num_100k_250k + d.num_250k_1m)
            ELSE 0
        END as lmict_loans_count,
        -- LMICT loans amount (if is_lmict = 1, use sb_loans_amount)
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m)
            ELSE 0
        END as lmict_loans_amount,
        -- Loans Rev Under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        -- Amount Rev Under $1m
        d.amtsbrev_under_1m as amount_rev_under_1m
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    INNER JOIN assessment_area_counties aac
        ON CAST(d.geoid5 AS STRING) = aac.geoid5
    WHERE CAST(d.year AS STRING) IN ('2020', '2021', '2022', '2023')
        -- Match respondent ID (strip prefix if present)
        AND (l.sb_resid = '11813' OR l.sb_resid = '11813')
        AND d.msamd IS NOT NULL
        AND d.msamd != ''
),

aggregated_sb_metrics AS (
    -- Aggregate SB metrics by year and CBSA
    SELECT 
        year,
        cbsa_code,
        -- Metric 1: SB Loans (count)
        SUM(sb_loans_count) as sb_loans_total,
        -- Metric 2: #LMICT (count of loans in LMICT tracts)
        SUM(lmict_loans_count) as lmict_count,
        -- Metric 3: Avg SB LMICT Loan Amount ($#,###)
        CASE 
            WHEN SUM(lmict_loans_count) > 0
            THEN SUM(lmict_loans_amount) / SUM(lmict_loans_count)
            ELSE NULL
        END as avg_sb_lmict_loan_amount,
        -- Metric 4: Loans Rev Under $1m (count)
        SUM(loans_rev_under_1m) as loans_rev_under_1m_count,
        -- Metric 5: Avg Loan Amt for RUM SB ($#,###)
        CASE 
            WHEN SUM(loans_rev_under_1m) > 0
            THEN SUM(amount_rev_under_1m) / SUM(loans_rev_under_1m)
            ELSE NULL
        END as avg_loan_amt_rum_sb
    FROM filtered_sb_data
    GROUP BY year, cbsa_code
)

-- Final output: aggregated SB metrics by year and CBSA
SELECT * FROM aggregated_sb_metrics
ORDER BY year, cbsa_code


-- Peer Banks

-- Goal-Setting Analysis: Peer Small Business Data Query
-- Subject Bank SB Respondent ID: 11813 (using 11813 for matching)
-- Assessment Area Counties: 142 counties
-- Years: 2020, 2021, 2022, 2023
-- Peer Rule: 50%-200% of subject bank's volume by year and CBSA

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['01081', '01009', '01073', '01115', '01117', '01003', '01103', '01055', '01083', '01089', '01097', '01085', '01101', '01125', '01013', '01025', '01039', '01049', '01071', '01095', '01121', '01129', '05007', '05143', '05033', '05131', '05051', '05031', '05045', '05085', '05119', '05091', '05001', '05027', '05055', '05057', '05065', '05073', '05093', '05095', '05103', '05117', '05121', '05133', '05139', '12091', '12131', '12017', '12081', '12115', '12083', '12005', '12033', '12113', '12103', '12053', '12057', '12101', '13059', '13089', '13121', '13135', '13073', '13189', '13245', '13047', '13295', '13139', '13021', '13169', '13067', '13051', '13153', '13093', '13267', '22079', '22005', '22033', '22063', '22055', '22019', '22067', '22073', '22083', '22015', '22017', '22061', '28047', '28059', '28035', '28073', '28049', '28089', '28121', '28123', '28127', '28033', '28137', '28003', '28013', '28017', '28025', '28043', '28057', '28061', '28067', '28071', '28081', '28087', '28095', '28099', '28105', '28107', '28115', '28117', '28141', '28145', '28149', '28153', '28159', '28161', '29189', '29189', '29077', '47065', '47033', '47053', '47113', '47047', '47157', '47167', '47037', '47187', '47055', '47095', '47103', '47109', '47183', '48021', '48209', '48453', '48491']) as geoid5
),

filtered_sb_data AS (
    -- Filter SB data early: years, assessment area counties
    SELECT 
        CAST(d.year AS STRING) as year,
        d.msamd as cbsa_code,
        l.sb_resid as respondent_id,
        -- SB Loans count and amount for volume matching
        (d.num_under_100k + d.num_100k_250k + d.num_250k_1m) as sb_loans_count,
        (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m) as sb_loans_amount,
        -- LMICT flag and counts/amounts
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN 1 ELSE 0
        END as is_lmict,
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.num_under_100k + d.num_100k_250k + d.num_250k_1m)
            ELSE 0
        END as lmict_loans_count,
        CASE 
            WHEN d.income_group_total IN ('101', '102', '1', '2', '3', '4', '5', '6', '7', '8')
            THEN (d.amt_under_100k + d.amt_100k_250k + d.amt_250k_1m)
            ELSE 0
        END as lmict_loans_amount,
        -- Revenue under $1m
        d.numsbrev_under_1m as loans_rev_under_1m,
        d.amtsbrev_under_1m as amount_rev_under_1m
    FROM `hdma1-242116.sb.disclosure` d
    INNER JOIN `hdma1-242116.sb.lenders` l
        ON d.respondent_id = l.sb_resid
    INNER JOIN assessment_area_counties aac
        ON CAST(d.geoid5 AS STRING) = aac.geoid5
    WHERE CAST(d.year AS STRING) IN ('2020', '2021', '2022', '2023')
        AND d.msamd IS NOT NULL
        AND d.msamd != ''
),

subject_volume AS (
    -- Calculate subject bank's volume by year and CBSA for peer matching
    SELECT 
        year,
        cbsa_code,
        SUM(sb_loans_count) as subject_sb_vol
    FROM filtered_sb_data
    WHERE respondent_id = '11813' 
       OR respondent_id = '11813'
    GROUP BY year, cbsa_code
),

all_lenders_volume AS (
    -- Calculate all lenders' volumes by year, CBSA, and respondent_id
    SELECT 
        year,
        cbsa_code,
        respondent_id,
        SUM(sb_loans_count) as lender_sb_vol
    FROM filtered_sb_data
    GROUP BY year, cbsa_code, respondent_id
),

peers AS (
    -- Identify peer lenders (50%-200% of subject's volume) by year and CBSA
    SELECT DISTINCT
        al.year,
        al.cbsa_code,
        al.respondent_id
    FROM all_lenders_volume al
    INNER JOIN subject_volume sv
        ON al.year = sv.year
        AND al.cbsa_code = sv.cbsa_code
    WHERE al.respondent_id != '11813'  -- Exclude subject bank
      AND al.respondent_id != '11813'
      AND al.lender_sb_vol >= sv.subject_sb_vol * 0.5  -- At least 50% of subject volume
      AND al.lender_sb_vol <= sv.subject_sb_vol * 2.0  -- At most 200% of subject volume
),

peer_sb_data AS (
    -- Filter to only peer lenders' loans
    SELECT f.*
    FROM filtered_sb_data f
    INNER JOIN peers p
        ON f.year = p.year
        AND f.cbsa_code = p.cbsa_code
        AND f.respondent_id = p.respondent_id
),

aggregated_peer_sb_metrics AS (
    -- Aggregate peer SB metrics by year and CBSA (same structure as subject query)
    SELECT 
        year,
        cbsa_code,
        -- Metric 1: SB Loans (count)
        SUM(sb_loans_count) as sb_loans_total,
        -- Metric 2: #LMICT (count of loans in LMICT tracts)
        SUM(lmict_loans_count) as lmict_count,
        -- Metric 3: Avg SB LMICT Loan Amount ($#,###)
        CASE 
            WHEN SUM(lmict_loans_count) > 0
            THEN SUM(lmict_loans_amount) / SUM(lmict_loans_count)
            ELSE NULL
        END as avg_sb_lmict_loan_amount,
        -- Metric 4: Loans Rev Under $1m (count)
        SUM(loans_rev_under_1m) as loans_rev_under_1m_count,
        -- Metric 5: Avg Loan Amt for RUM SB ($#,###)
        CASE 
            WHEN SUM(loans_rev_under_1m) > 0
            THEN SUM(amount_rev_under_1m) / SUM(loans_rev_under_1m)
            ELSE NULL
        END as avg_loan_amt_rum_sb
    FROM peer_sb_data
    GROUP BY year, cbsa_code
)

-- Final output: aggregated peer SB metrics by year and CBSA
SELECT * FROM aggregated_peer_sb_metrics
ORDER BY year, cbsa_code
