import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import { DataGrid } from '@mui/x-data-grid';

import { formatSeconds, minuteFilterOperators } from "./utils";

export function MachStopTableModalView({open, onClose, rec, metaData}){
    const columns = [
        {
            field: 'Start_Shift_Time',
            headerName: 'Start Shift Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Stop_time',
            headerName: 'Stop Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Stop_code',
            headerName: 'Stop Code',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Description',
            headerName: 'Description',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Recover_time',
            headerName: 'Recover Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'dur_minute',
            headerName: 'Duration',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
        
    ];


    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="lg"
        >
            <DialogTitle>The Details of Mach# {metaData.mach} with StyleCode# {metaData.style}</DialogTitle>
            <DialogContent>
                <Box sx={{ height: 700, width: '100%' }}>
                    <DataGrid
                        rows={rec}
                        columns={columns}
                        initialState={{
                            pagination: {
                                paginationModel: {
                                    pageSize: 10,
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
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}


export function CodeStopTableModalView({open, onClose, rec, metaData}){
    const columns = [
        {
            field: 'MachID',
            headerName: 'Mach ID',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Style_Code',
            headerName: 'Style Code',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'freq',
            headerName: 'Frequency',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'dur_sum',
            headerName: 'Duration (SUM)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
        {
            field: 'dur_med',
            headerName: 'Duration (MED)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
    ];


    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="lg"
        >
            <DialogTitle>The Details of Stop Code# {metaData.stop_code}</DialogTitle>
            <DialogContent>
                <Box sx={{ height: 700, width: '100%' }}>
                    <DataGrid
                        rows={rec}
                        columns={columns}
                        initialState={{
                            pagination: {
                                paginationModel: {
                                    pageSize: 10,
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
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}