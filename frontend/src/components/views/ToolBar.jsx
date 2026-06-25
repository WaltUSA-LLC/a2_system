import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import TextField from '@mui/material/TextField';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import { IconButton, Tooltip } from '@mui/material';
import AutoGraphOutlinedIcon from '@mui/icons-material/AutoGraphOutlined';

function ToolBar({
    start,
    end,
    shift,
    hasData,
    hasChart,
    hasShift,
    handleStartChange,
    handleEndChange,
    handleShiftChange,
    handleShowData,
    handleOpenChart,
}) {
    return (
        <Box
            sx={{
                display: 'flex',
                justifyContent: 'space-around',
                mt: '15px',
                mb: '15px',
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
            {hasShift && 
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
                </FormControl>}
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Button
                    variant="contained"
                    onClick={handleShowData}
                    sx={{
                        bgcolor: 'primary.light',
                        color: 'primary.contrastText',
                        '&:hover': {
                            bgcolor: 'primary.main',
                        },
                    }}
                >
                    Show Data
                </Button>

                <Tooltip title="Chart" placement="right-start">
                    <IconButton
                        sx={{
                            visibility: hasChart && hasData ? 'visible' : 'hidden',
                            color: 'primary.light',
                        }}
                        onClick={handleOpenChart}
                    >
                        <AutoGraphOutlinedIcon />
                    </IconButton>
                </Tooltip>
            </Box>
        </Box>
    );
}

export default ToolBar;
