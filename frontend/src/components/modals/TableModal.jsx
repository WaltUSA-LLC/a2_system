import Button from '@mui/material/Button';
import Box from '@mui/material/Box';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import { DataGrid } from '@mui/x-data-grid';

import { formatSeconds, minuteFilterOperators, hourFilterOperators } from "../utils";
import { Typography } from '@mui/material';

export function MachStopTableModal({open, onClose, rec, metaData}){
    const columns = [
        {
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
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
            field: 'duration',
            headerName: 'Duration',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
        {
            field: 'KO',
            headerName: 'KO',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Tech',
            headerName: 'Tech',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
    ];


    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="xl"
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


export function CodeStopTableModal({open, onClose, rec, metaData}){
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


export function MachDetailTableModal({open, onClose, rec, metaData}){
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
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'MES_prs',
            headerName: 'MES (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'NAU_prs',
            headerName: 'NAU (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Discard_prs',
            headerName: 'Discard (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'defects',
            headerName: 'Defect (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'PQC defects',
        },
        {
            field: 'pqc_cnt',
            headerName: 'Checks',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'PQC checks',
        },
        {
            field: "ON_Time",
            headerName: "ON Time",
            type: 'number',
            flex: 1,
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: hourFilterOperators,
        },
        {
            field: "OFF_Time",
            headerName: "OFF Time",
            type: 'number',
            flex: 1,
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: hourFilterOperators,
        },
        {
            field: 'ON_Time_Occupation',
            headerName: 'ON Time (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value == null ? null : value * 100,
            valueFormatter: (value) => value == null ? '' : `${value.toFixed(1)}%`,
        },
        {
            field: 'Mach_Efficiency',
            headerName: 'Mach Eff (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value == null ? null : value * 100,
            valueFormatter: (value) => value == null ? '' : `${value.toFixed(1)}%`,
        },
        {
            field: 'Comment',
            headerName: 'Comment',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
    ];


    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="xl"
        >
            {metaData.style ? 
                <DialogTitle>
                    <Typography variant='h6' component='div'>
                        Style: {metaData.style}, Shift: {metaData.date_time}
                    </Typography>
                    <Typography variant='body1'>
                        KO: {metaData.ko}, Tech: {metaData.tech}, Creeler: {metaData.creeler}, Yarner: {metaData.yarner}
                    </Typography>
                </DialogTitle> :
                <DialogTitle>
                    <Typography variant='h6' component='div'>
                        Shift: {metaData.date_time}
                    </Typography>
                    <Typography variant='body1'>
                        KO: {metaData.ko}, Tech: {metaData.tech}, Creeler: {metaData.creeler}, Yarner: {metaData.yarner}
                    </Typography>
                </DialogTitle>
            }
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


export function PQCStaffDetailTableModal({open, onClose, rec, metaData}) {
    const columns = [
        {
            field: 'DateRec',
            headerName: 'Date Rec',
            flex: 2,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
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
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'toeHole',
            headerName: 'Hole',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'brokenNDL',
            headerName: 'N-Brok',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Broken',
        },
        {
            field: 'missNDL',
            headerName: 'N-Miss',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Missing',
        },
        {
            field: 'missYarn',
            headerName: 'Y-Brok',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Broken',
        },
        {
            field: 'fanYarn',
            headerName: 'Y-Rtn',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Return',
        },
        {
            field: 'feisha',
            headerName: 'Y-Fly',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Fly',
        },
        {
            field: 'logoIssue',
            headerName: 'Logo',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Logo Issue',
        },
        {
            field: 'dirty',
            headerName: 'Stain',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'other',
            headerName: 'Other',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
    ];


    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="xl"
        >
            <DialogTitle>
                <Typography variant='h6' component='div'>
                    {metaData.name}'s records at shift {metaData.date_time}
                </Typography>
            </DialogTitle>
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