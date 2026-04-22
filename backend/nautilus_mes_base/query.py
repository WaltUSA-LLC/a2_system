MES_QUERY = """
DECLARE @Start DATETIME2(0) = :start_dt;
DECLARE @End   DATETIME2(0) = DATEADD(HOUR, 24, @Start);
DECLARE @Shift  INT = :shift;
DECLARE @Shift_prod_down_low_bound DATETIME2(0);
DECLARE @Shift_prod_down_upper_bound DATETIME2(0);

-- Assume shift 1 product down time range 14:00 to 23:00, shift 2 product down time range 5:00 to 10:00
IF @Shift = 1
    SET @Shift_prod_down_low_bound = DATEADD(HOUR, 7, @Start);
ELSE
    SET @Shift_prod_down_low_bound = DATEADD(HOUR, 22, @Start);

IF @Shift = 1
    SET @Shift_prod_down_upper_bound = DATEADD(HOUR, 16, @Start);
ELSE
    SET @Shift_prod_down_upper_bound = DATEADD(HOUR, 27, @Start);

WITH mach_info AS(
    SELECT
        pm.MachCode AS MachID,
        pm.Shift as shift_no,
        MIN(pm.DateStartShift) as Shift_Start_Time,
        pm.StyleCode as Style_Code,
        SUM(pm.Pieces) / 2 as NAU_prs,
        SUM(pm.Discards) / 2 as Discard_prs,
        CAST(AVG(CASE WHEN pm.Cycle <> 0 THEN pm.Cycle END) AS INT) AS Avg_Cycle,
        SUM(pm.TimeOn) AS ON_Time,
        SUM(pm.TimeOff) AS OFF_Time
    FROM dbNautilus.dbo.PRODUCTIONS_MONITOR AS pm
    WHERE pm.DateRec > @Start
      AND pm.DateRec <=  @End
      AND pm.Shift  = @Shift
      AND pm.Pieces >= 0
      AND pm.Pieces < 500  ---clean mach mes data
    GROUP BY pm.MachCode, pm.StyleCode, pm.Shift
),
internal_id AS(
    SELECT distinct FInterID
    FROM HUAER_SFP_USA.dbo.ODK_ProductDown
    WHERE FDate >= @Shift_prod_down_low_bound
      AND FDate <= @Shift_prod_down_upper_bound
),
product_down AS(
    SELECT pde.FMachineID, pde.FWeight
    FROM internal_id as internal, HUAER_SFP_USA.dbo.ODK_ProductDownEntry as pde
    WHERE internal.FInterID = pde.FInterID
),
product_down_mach AS(
    SELECT TRY_CAST(SUBSTRING(eq.FNumber, PATINDEX('%[0-9]%', eq.FNumber), 32) AS INT) AS mach, pd.FWeight
    FROM HUAER_SFP_USA.dbo.ODK_Equipment AS eq, product_down as pd
    WHERE eq.FItemID = pd.FMachineID
)
SELECT MachID,
       Shift_Start_Time,
       Style_Code,
       pdm.FWeight AS Weight,
       NAU_prs,
       Discard_prs,
       Avg_Cycle,
       ON_Time,
       OFF_Time
FROM mach_info as m  LEFT JOIN   product_down_mach as pdm ON pdm.mach=m.MachID
ORDER BY MachID ASC;
"""


NAU_STOP_QUERY = """
DECLARE @Start DATETIME2(0) = :start_dt;
DECLARE @End   DATETIME2(0) = :end_dt;

SELECT
    sm.Shift AS Shift,
    sm.MachCode AS MachID,
    sm.StyleCode AS Style_Code,
    sm.LastStopCode AS Stop_code,
    s.Description AS Description,
    sm.DateRec AS Recover_time,
    sm.LastDateRec AS Stop_time
FROM dbNautilus.dbo.STOPS_MONITOR AS sm, dbNautilus.dbo.STOPS AS s 
WHERE sm.LastDateRec > @Start
    AND sm.LastDateRec <=  @End
    AND sm.StopCode = 0
    AND sm.LastStopCode = s.StopCode 
"""