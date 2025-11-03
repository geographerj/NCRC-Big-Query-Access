-- Subject Bank

-- Goal-Setting Analysis: Small Business Data Query
-- Subject Bank SB Respondent ID: 7745 (using 7745 for matching)
-- Assessment Area Counties: 194 counties
-- Years: 2020, 2021, 2022, 2023

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101']) as geoid5
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
        AND (l.sb_resid = '7745' OR l.sb_resid = '7745')
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
-- Subject Bank SB Respondent ID: 7745 (using 7745 for matching)
-- Assessment Area Counties: 194 counties
-- Years: 2020, 2021, 2022, 2023
-- Peer Rule: 50%-200% of subject bank's volume by year and CBSA

WITH assessment_area_counties AS (
    -- Filter to only assessment area counties using GEOID5
    SELECT DISTINCT geoid5
    FROM UNNEST(['17031', '17043', '17073', '17197', '17037', '17089', '17093', '17097', '55059', '21015', '21117', '39017', '39025', '39061', '39165', '39081', '54029', '39099', '39155', '42085', '08013', '08041', '08001', '08005', '08014', '08031', '08035', '08059', '12021', '18011', '18057', '18063', '18081', '18095', '18097', '18157', '26161', '26025', '26017', '26163', '26087', '26093', '26099', '26125', '26147', '26049', '26067', '26081', '26117', '26139', '26075', '26077', '26037', '26045', '26065', '26155', '26111', '26115', '26121', '26021', '26145', '26027', '26005', '26007', '26009', '26011', '26015', '26023', '26029', '26033', '26035', '26039', '26041', '26043', '26047', '26051', '26055', '26057', '26059', '26061', '26063', '26069', '26073', '26079', '26089', '26091', '26101', '26103', '26105', '26107', '26113', '26119', '26123', '26127', '26129', '26133', '26135', '26137', '26141', '26143', '26151', '26149', '26157', '26159', '26165', '27137', '27013', '27003', '27019', '27037', '27053', '27123', '27139', '27141', '27163', '27171', '27009', '27145', '27131', '39133', '39153', '39019', '39151', '39035', '39055', '39085', '39093', '39103', '39041', '39045', '39049', '39089', '39097', '39129', '39159', '39057', '39109', '39113', '39003', '39139', '39023', '39051', '39095', '39123', '39173', '39013', '39005', '39007', '39029', '39033', '39039', '39043', '39047', '39059', '39063', '39065', '39067', '39069', '39077', '39083', '39091', '39101', '39119', '39137', '39141', '39143', '39147', '39157', '39167', '39169', '39171', '39175', '42049', '42003', '42007', '42019', '42125', '42129', '42073', '46099', '54039', '54011', '54079', '51820', '54061', '54107', '51660', '54041', '54049', '54083', '54085', '55079', '55133', '55101']) as geoid5
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
    WHERE respondent_id = '7745' 
       OR respondent_id = '7745'
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
    WHERE al.respondent_id != '7745'  -- Exclude subject bank
      AND al.respondent_id != '7745'
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
