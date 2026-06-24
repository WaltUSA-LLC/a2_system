import { useState } from 'react';
import Box from '@mui/material/Box';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import CircularProgress from '@mui/material/CircularProgress';
import { DataGrid } from '@mui/x-data-grid';
import ToolBar from './ToolBar';


function formatDate(date) {
    return new Intl.DateTimeFormat('en-CA', {
        timeZone: 'America/Denver',
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
    }).format(date);
}

function getDateDiffInDays(startDate, endDate) {
    const millisecondsPerDay = 24 * 60 * 60 * 1000;
    return (new Date(endDate) - new Date(startDate)) / millisecondsPerDay;
}

function TableView({col, rec, loadData, handleOpenChart, handleRowClick, markDownSelectedTime, hasChart=true}){
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const defaultDate = formatDate(yesterday);
    const [start, setStart] = useState(defaultDate);
    const [end, setEnd] = useState(defaultDate);
    const [shift, setShift] = useState(0);
    const [loading, setLoading] = useState(false);
    const [dateRangeErrorOpen, setDateRangeErrorOpen] = useState(false);
    const [dateRangeErrorMessage, setDateRangeErrorMessage] = useState('');
    const hasData = !loading && rec.length > 0;
    const isEndBeforeStart = end < start;

    async function handleShowData() {
        if (isEndBeforeStart) {
            setDateRangeErrorMessage('End time must be greater than or equal to start time.');
            setDateRangeErrorOpen(true);
            return;
        }

        if (getDateDiffInDays(start, end) > 31) {
            setDateRangeErrorMessage('The difference between start and end time must be within 31 days.');
            setDateRangeErrorOpen(true);
            return;
        }

        setLoading(true);
        if(markDownSelectedTime) {
            markDownSelectedTime({start, end, shift});
        }

        try{
            await loadData(start, end, shift);
        }catch(err){
            console.error(err);
        }finally{
            setLoading(false);
        }
        
    }

    function handleStartChange(event) {
        setStart(event.target.value);
    }

    function handleEndChange(event) {
        setEnd(event.target.value);
    }

    function handleShiftChange(event) {
        setShift(event.target.value);
    }

    function handleDateRangeErrorClose(event, reason) {
        if (reason === 'clickaway') {
            return;
        }

        setDateRangeErrorOpen(false);
    }

    return (
        <Box sx={{ width: '100%' }}>
            <Snackbar
                open={dateRangeErrorOpen}
                autoHideDuration={5000}
                onClose={handleDateRangeErrorClose}
                anchorOrigin={{ vertical: 'top', horizontal: 'center' }}
            >
                <Alert
                    severity="warning"
                    variant="filled"
                    onClose={handleDateRangeErrorClose}
                    sx={{ width: '100%' }}
                >
                    {dateRangeErrorMessage}
                </Alert>
            </Snackbar>
            <ToolBar
                start={start}
                end={end}
                shift={shift}
                hasData={hasData}
                hasChart={hasChart}
                handleStartChange={handleStartChange}
                handleEndChange={handleEndChange}
                handleShiftChange={handleShiftChange}
                handleShowData={handleShowData}
                handleOpenChart={handleOpenChart}
            />

            {loading ? (
                <Box sx={{ height: 700, width: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                    <CircularProgress enableTrackSlot />
                </Box>
            ) : (
                <Box sx={{ height: 700, width: '100%' }}>
                    <DataGrid
                        rows={rec}
                        columns={col}
                        initialState={{
                            pagination: {
                                paginationModel: {
                                    pageSize: 10,
                                },
                            },
                        }}
                        pageSizeOptions={[10, 20, 30]}
                        onRowClick={handleRowClick}
                        showToolbar
                        sx={{
                            '& .MuiDataGrid-columnHeaderTitle': {
                            fontWeight: 'bold',
                            },
                        }}
                    />
                </Box>
            )}
        </Box>
    );
}

export default TableView;
