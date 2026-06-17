import { useState } from 'react';
import axios from 'axios';

import Alert from '@mui/material/Alert';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import CircularProgress from '@mui/material/CircularProgress';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import MenuItem from '@mui/material/MenuItem';
import Select from '@mui/material/Select';
import Stack from '@mui/material/Stack';
import TextField from '@mui/material/TextField';
import Typography from '@mui/material/Typography';
import CloudUploadOutlinedIcon from '@mui/icons-material/CloudUploadOutlined';
import UploadFileOutlinedIcon from '@mui/icons-material/UploadFileOutlined';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

const UPLOAD_TYPES = {
    staff: {
        label: 'Staff Schedule',
        endpoint: '/base/uploads/staff',
    },
    
};

const MONTHS = [
    { value: 1, label: 'January' },
    { value: 2, label: 'February' },
    { value: 3, label: 'March' },
    { value: 4, label: 'April' },
    { value: 5, label: 'May' },
    { value: 6, label: 'June' },
    { value: 7, label: 'July' },
    { value: 8, label: 'August' },
    { value: 9, label: 'September' },
    { value: 10, label: 'October' },
    { value: 11, label: 'November' },
    { value: 12, label: 'December' },
];

function UploadView() {
    const now = new Date();
    const [uploadType, setUploadType] = useState('staff');
    const [year, setYear] = useState(now.getFullYear());
    const [month, setMonth] = useState(now.getMonth() + 1);
    const [file, setFile] = useState(null);
    const [fileInputKey, setFileInputKey] = useState(0);
    const [loading, setLoading] = useState(false);
    const [alert, setAlert] = useState(null);
    const selectedUpload = UPLOAD_TYPES[uploadType];

    function handleUploadTypeChange(event) {
        setUploadType(event.target.value);
        setAlert(null);
    }

    function handleFileChange(event) {
        setFile(event.target.files?.[0] ?? null);
        setAlert(null);
    }

    async function handleUpload() {
        if (!file) {
            setAlert({ severity: 'warning', message: 'Select an Excel file before uploading.' });
            return;
        }

        if (!selectedUpload.endpoint) {
            setAlert({ severity: 'warning', message: 'Upload API is not available yet.' });
            return;
        }

        const parsedYear = Number(year);
        const parsedMonth = Number(month);

        if (!Number.isInteger(parsedYear) || parsedYear < 2000 || parsedYear > 2100) {
            setAlert({ severity: 'warning', message: 'Year must be between 2000 and 2100.' });
            return;
        }

        if (!Number.isInteger(parsedMonth) || parsedMonth < 1 || parsedMonth > 12) {
            setAlert({ severity: 'warning', message: 'Select a valid month.' });
            return;
        }

        const formData = new FormData();
        formData.append('file', file);
        formData.append('year', parsedYear);
        formData.append('month', parsedMonth);

        setLoading(true);
        setAlert(null);

        try {
            const response = await axios.post(`${API_BASE_URL}${selectedUpload.endpoint}`, formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });

            const result = response.data;
            const insertedCount = result.inserted_count ?? 0;
            setAlert({
                severity: 'success',
                message: `${result.message ?? 'Upload complete'} (${insertedCount} rows).`,
            });
            setFile(null);
            setFileInputKey((currentKey) => currentKey + 1);
        } catch (err) {
            const message = err.response?.data?.detail ?? 'Upload failed.';
            console.log("err: ", typeof err);
            setAlert({ severity: 'error', message });
        } finally {
            setLoading(false);
        }
    }

    return (
        <Box sx={{ width: '100%', px: 3, py: 3 }}>
            <Stack spacing={3} sx={{ maxWidth: 760, mx: 'auto' }}>
                <Typography
                    variant="h5"
                    component="h1"
                    sx={{
                        fontWeight: 700,
                        letterSpacing: 0,
                    }}
                >
                    Upload Files
                </Typography>

                {alert ? (
                    <Alert severity={alert.severity} onClose={() => setAlert(null)}>
                        {alert.message}
                    </Alert>
                ) : null}

                <Box
                    sx={{
                        display: 'grid',
                        gridTemplateColumns: {
                            xs: '1fr',
                            md: '1.2fr 1fr 1fr',
                        },
                        gap: 2,
                    }}
                >
                    <FormControl fullWidth>
                        <InputLabel id="upload-type-label">Upload Type</InputLabel>
                        <Select
                            labelId="upload-type-label"
                            value={uploadType}
                            label="Upload Type"
                            onChange={handleUploadTypeChange}
                        >
                            {Object.entries(UPLOAD_TYPES).map(([value, option]) => (
                                <MenuItem key={value} value={value}>
                                    {option.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>

                    <TextField
                        label="Year"
                        type="number"
                        value={year}
                        onChange={(event) => setYear(event.target.value)}
                        slotProps={{
                            input: {
                                inputProps: {
                                    min: 2000,
                                    max: 2100,
                                },
                            },
                        }}
                    />

                    <FormControl fullWidth disabled={uploadType !== 'staff'}>
                        <InputLabel id="month-label">Month</InputLabel>
                        <Select
                            labelId="month-label"
                            value={month}
                            label="Month"
                            onChange={(event) => setMonth(event.target.value)}
                        >
                            {MONTHS.map((option) => (
                                <MenuItem key={option.value} value={option.value}>
                                    {option.label}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                </Box>

                <Stack
                    direction={{ xs: 'column', sm: 'row' }}
                    spacing={2}
                    sx={{
                        alignItems: { xs: 'stretch', sm: 'center' },
                    }}
                >
                    <Button
                        component="label"
                        variant="outlined"
                        startIcon={<UploadFileOutlinedIcon />}
                        sx={{ minHeight: 48, textTransform: 'none' }}
                    >
                        Choose File
                        <input
                            key={fileInputKey}
                            hidden
                            type="file"
                            accept=".xlsx,.xls"
                            onChange={handleFileChange}
                        />
                    </Button>

                    <Typography
                        variant="body1"
                        sx={{
                            flexGrow: 1,
                            minWidth: 0,
                            overflow: 'hidden',
                            textOverflow: 'ellipsis',
                            whiteSpace: 'nowrap',
                        }}
                    >
                        {file?.name ?? 'No file selected'}
                    </Typography>

                    <Button
                        variant="contained"
                        startIcon={loading ? <CircularProgress color="inherit" size={18} /> : <CloudUploadOutlinedIcon />}
                        onClick={handleUpload}
                        disabled={loading}
                        sx={{
                            minHeight: 48,
                            bgcolor: 'primary.light',
                            color: 'primary.contrastText',
                            textTransform: 'none',
                            '&:hover': {
                                bgcolor: 'primary.main',
                            },
                        }}
                    >
                        {loading ? 'Uploading' : 'Upload'}
                    </Button>
                </Stack>
            </Stack>
        </Box>
    );
}

export default UploadView;
