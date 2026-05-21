--index for STOP_MONITOR table
CREATE NONCLUSTERED INDEX IDX_STOPS_MONITOR_StopCode_DateRec
ON dbNautilus.dbo.STOPS_MONITOR (LastDateRec)
INCLUDE (StopCode, DateRec, MachCode, StyleCode, Shift, LastStopCode);