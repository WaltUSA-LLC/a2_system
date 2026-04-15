import { useState } from 'react';
import axios from "axios";
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import { DataGrid } from '@mui/x-data-grid';

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function BaseTableView({url, col}){
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const defaultDate = formatDate(yesterday);
    const [start, setStart] = useState(defaultDate);
    const [end, setEnd] = useState(defaultDate);
    const [rec, setRec] = useState([]);
    //const [col, setCol] = useState([]);
    const [loading, setLoading] = useState(false);

    function handleImportData() {
        setLoading(true);
        axios.get(url, {
            params: {
                start,
                end,
            },
        })
            .then((resp) => {
                //setCol((resp.data.columns ?? []).filter((column) => column.field !== 'id'));
                setRec(resp.data.content ?? []);
            })
            .catch((err) => {
                console.error(err);
                //setCol([]);
                setRec([]);
            })
            .finally(() => {
                setLoading(false);
            });
    }

    function handleStartChange(event) {
        setStart(event.target.value);
    }

    function handleEndChange(event) {
        setEnd(event.target.value);
    }

    return (
        <Box sx={{ width: '100%' }}>
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
                <Button
                    variant="contained"
                    onClick={handleImportData}
                >
                    Import Data
                </Button>
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
                                    pageSize: 20,
                                },
                            },
                        }}
                        pageSizeOptions={[10, 20, 30]}
                        disableRowSelectionOnClick
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

export default BaseTableView;
