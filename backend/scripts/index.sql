--index for STOP_MONITOR table
CREATE NONCLUSTERED INDEX IDX_STOPS_MONITOR_LastStopCode_DateRec
ON dbo.STOPS_MONITOR (StopCode, DateRec)
INCLUDE (MachCode, Shift, LastStopCode, LastDateRec);