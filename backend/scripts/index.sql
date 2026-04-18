--index for STOP_MONITOR table
CREATE NONCLUSTERED INDEX IDX_STOPS_MONITOR_StopCode_DateRec
ON dbo.STOPS_MONITOR (StopCode, DateRec)
INCLUDE (MachCode, Shift, LastStopCode, LastDateRec);

CREATE NONCLUSTERED INDEX IDX_STOPS_MONITOR_LastStopCode_DateRec
ON dbo.STOPS_MONITOR (StopCode, LastDateRec)
INCLUDE (MachCode, Shift, LastStopCode, DateRec);