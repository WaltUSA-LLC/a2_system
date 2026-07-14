from cores.constants import DAY_SHIFT_START_STR, NIGHT_SHIFT_START_STR


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
        SUM(CASE 
                WHEN pm.Discards >= 0 THEN pm.Discards 
                ELSE 0 
            END) / 2 as Discard_prs,
        CAST(MIN(CASE WHEN pm.Cycle <> 0 THEN pm.Cycle END) AS INT) AS Avg_Cycle,
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


STOP_QUERY = """
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
FROM dbNautilus.dbo.STOPS_MONITOR AS sm LEFT JOIN dbNautilus.dbo.STOPS AS s ON sm.LastStopCode = s.StopCode 
WHERE sm.LastDateRec > @Start
    AND sm.LastDateRec <=  @End
    AND (sm.StopCode = 0 OR sm.LastStopCode <> 0) 
"""


STAFF_QUERY = """
DECLARE @Start DATETIME2(0) = :start_dt;
DECLARE @End   DATETIME2(0) = :end_dt;

WITH specific_schedule AS(
    SELECT *
    FROM dbA2.dbo.ShiftOperator
    WHERE ShiftStartTime >= @Start
        AND ShiftStartTime < @End  -- note here is the shiftStartTime, not LastDateRec
)
SELECT ShiftStartTime, ID, FirstName, LastName, RoleName
FROM specific_schedule AS ss JOIN dbA2.dbo.Operator AS op ON ss.OperatorID = op.ID
"""


PQC_QUERY = f"""
DECLARE @Start DATETIME2(0) = :start_dt;
DECLARE @End   DATETIME2(0) = :end_dt;
DECLARE @Shift  INT = :shift;

SELECT kcp.knitted AS Date, kcp.Shift AS Shift, MachineId AS MachID, 
    ItemStyle AS Style_Code, Name AS Role_Name, OperatorID, toeHole, brokenNDL, missNDL, missYarn, fanYarn, logoIssue,
    dirty, feisha, other, DateRec
FROM operator_log.dbo.knitCHN_pqc kcp 
WHERE kcp.Knitted >= CAST(@Start AS date) 
    AND kcp.Knitted <= CAST(@End AS date) 
    AND (@Shift = 0 or (CAST(kcp.Shift AS time) =
        CASE 
            WHEN @Shift = 1 THEN CAST('{DAY_SHIFT_START_STR}' AS time)
            WHEN @Shift = 2 THEN CAST('{NIGHT_SHIFT_START_STR}' AS time)
        END
    ))
"""
