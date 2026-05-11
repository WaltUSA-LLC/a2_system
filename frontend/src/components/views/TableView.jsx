import { useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Alert from '@mui/material/Alert';
import Snackbar from '@mui/material/Snackbar';
import { DataGrid } from '@mui/x-data-grid';

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

function TableView({col, rec, loadData, handleOpenChart, handleRowClick, markDownSelectedTime}){
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

        if (getDateDiffInDays(start, end) > 14) {
            setDateRangeErrorMessage('The difference between start and end time must be within 14 days.');
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
            <Box
                sx={{
                    display: 'flex',
                    justifyContent: 'space-around',
                    mt:'15px',
                    mb:'15px'
                }}
            >
                <TextField
                    label="Start Time"
                    type="date"
                    value={start}
                    onChange={handleStartChange}
                    slotProps={{ inputLabel: { shrink: true } }}
                />
                <TextField
                    label="End Time"
                    type="date"
                    value={end}
                    onChange={handleEndChange}
                    slotProps={{ inputLabel: { shrink: true } }}
                />
                <FormControl>
                    <InputLabel id="shift-label">Shift</InputLabel>
                    <Select
                        labelId="shift-label"
                        value={shift}
                        label="Shift"
                        onChange={handleShiftChange}
                    >
                        <MenuItem value={0}>ALL</MenuItem>
                        <MenuItem value={1}>DAY</MenuItem>
                        <MenuItem value={2}>NIGHT</MenuItem>
                    </Select>
                </FormControl>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                    <Button
                        variant="contained"
                        onClick={handleShowData}
                    >
                        Show Data
                    </Button>
                    { hasData ? (
                        <Button variant="text" onClick={handleOpenChart}>
                            Chart
                        </Button>
                    ) : null }
                </Box>
            </Box>

            {loading ? (
                <div>Loading...</div>
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
