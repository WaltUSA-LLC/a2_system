import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import { GridFilterInputValue } from "@mui/x-data-grid";
import { DataGrid } from '@mui/x-data-grid';

import { formatSeconds } from "./utils";

export function MachStopTableModalView({open, onClose, rec, metaData}){
    const minuteFilterOperators = [
        {
            label: "minutes =",
            value: "minutesEquals",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) === target;
            },
        },
        {
            label: "minutes >=",
            value: "minutesGreaterOrEqualThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) >= target;
            },
        },
        {
            label: "minutes <=",
            value: "minutesLessOrEqualThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) <= target;
            },
        },
    ];

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