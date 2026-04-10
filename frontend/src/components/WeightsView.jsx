import { useState, useEffect } from 'react';
import axios from "axios";
import Box from '@mui/material/Box';
import TextField from '@mui/material/TextField';
import { DataGrid } from '@mui/x-data-grid';

function formatDate(date) {
    return date.toISOString().split('T')[0];
}

function WeightsView() {
    const yesterday = new Date();
    yesterday.setDate(yesterday.getDate() - 1);
    const defaultDate = formatDate(yesterday);
    const [start, setStart] = useState(defaultDate);
    const [end, setEnd] = useState(defaultDate);
    const [rec, setRec] = useState([]);
    const [col, setCol] = useState([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        axios.get("http://localhost:8000/base/mes", {
            params: {
                start,
                end:start,
            },
        })
            .then((resp) => {
                setCol((resp.data.columns ?? []).filter((column) => column.field !== 'id'));
                setRec(resp.data.content ?? []);
            })
            .catch((err) => {
                console.error(err);
                setCol([]);
                setRec([]);
            })
            .finally(() => {
                setLoading(false);
            });
    }, [start, end]);

    function handleStartChange(event) {
        setLoading(true);
        setStart(event.target.value);
    }

    function handleEndChange(event) {
        setLoading(true);
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
                    label="Time"
                    type="date"
                    value={start}
                    onChange={handleStartChange}
                    slotProps={{ inputLabel: { shrink: true } }}
                />
                {/* <TextField
                    label="End Time"
                    type="date"
                    value={end}
                    onChange={handleEndChange}
                    slotProps={{ inputLabel: { shrink: true } }}
                /> */}
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
                    />
                </Box>
            )}
        </Box>
    );
}

export default WeightsView;
