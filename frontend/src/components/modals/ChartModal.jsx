import { useEffect, useState } from 'react';
import Box from '@mui/material/Box';
import Button from '@mui/material/Button';
import Dialog from '@mui/material/Dialog';
import DialogTitle from '@mui/material/DialogTitle';
import DialogContent from '@mui/material/DialogContent';
import DialogActions from '@mui/material/DialogActions';
import FormControl from '@mui/material/FormControl';
import InputLabel from '@mui/material/InputLabel';
import Select from '@mui/material/Select';
import MenuItem from '@mui/material/MenuItem';
import Typography from '@mui/material/Typography';
import { BarChart as MuiBarChart } from '@mui/x-charts/BarChart';
import {
    ChartsContainer,
    BarPlot,
    LinePlot,
    MarkPlot,
    ChartsXAxis,
    ChartsYAxis,
    ChartsLegend,
    ChartsTooltip,
    ChartsGrid,
} from '@mui/x-charts';

function LineBarChart({ chartDataset }) {
    return (
        <>
            {chartDataset.length > 0 ? (
                <Box sx={{ mt: 3 }}>
                    <Box
                        sx={{
                            display: 'flex',
                            flexWrap: 'wrap',
                            gap: 2,
                            alignItems: 'center',
                            mb: 2,
                            ml: 40,
                        }}
                    >
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 14, height: 14, bgcolor: '#1f81eb', borderRadius: 0.5 }} />
                            <Typography variant="body2">Day Shift</Typography>
                        </Box>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                            <Box sx={{ width: 14, height: 14, bgcolor: '#f28e2b', borderRadius: 0.5 }} />
                            <Typography variant="body2">Night Shift</Typography>
                        </Box>
                    </Box>
                    <Box
                        sx={{
                            '& .MuiBarChart-element': {
                                filter: 'blur(1px)',
                                opacity: 0.8,
                            },
                        }}
                    >
                        <ChartsContainer
                            dataset={chartDataset}
                            height={320}
                            xAxis={[{ scaleType: 'band', dataKey: 'date', label: 'Date' }]}
                            series={[
                                { id: 'day-bar', type: 'bar', dataKey: 'Day', label: 'Day Shift Bar', color: '#1f81eb' },
                                { id: 'night-bar', type: 'bar', dataKey: 'Night', label: 'Night Shift Bar', color: '#f28e2b' },
                                { id: 'day-line', type: 'line', dataKey: 'Day', label: 'Day Shift Line', color: '#1f81eb', showMark: true },
                                { id: 'night-line', type: 'line', dataKey: 'Night', label: 'Night Shift Line', color: '#f28e2b', showMark: true },
                            ]}
                            margin={{ top: 50, right: 20, bottom: 40, left: 50 }}
                        >
                            <ChartsGrid horizontal />
                            <ChartsLegend
                                direction="row"
                                sx={{
                                    justifyContent: 'center',
                                    gap: 2,
                                }}
                            />
                            <BarPlot />
                            <LinePlot />
                            <MarkPlot />
                            <ChartsXAxis />
                            <ChartsYAxis />
                            <ChartsTooltip />
                        </ChartsContainer>
                    </Box>
                </Box>
            ) : null}
        </>
    );
}

export function BarChart({ chartDataset }) {
    return (
        <MuiBarChart
            dataset={chartDataset}
            xAxis={[{ label: 'Frequency' }]}
            yAxis={[{
                scaleType: 'band',
                dataKey: 'MachID',
                label: 'Machine ID', 
            }]}
            series={[{ dataKey: 'freq', 
                       label: 'Frequency',}]}
            layout="horizontal"
            grid={{ vertical: true }}
            height={400}
        />
    );
}

export function BarChart1({ chartDataset, property }) {
    return (
        chartDataset.length>0 &&<MuiBarChart
            dataset={chartDataset}
            xAxis={[{ label: property }]}
            yAxis={[{
                scaleType: 'band',
                dataKey: 'Stop_code',
                label: 'Stop Code',
                width: 90, 
            }]}
            series={[{ dataKey: property, 
                    label: property,}]}
            layout="horizontal"
            grid={{ vertical: true }}
            height={400}
        />
    );
}

export function MachChartModal({ open, onClose, rec }) {
    const [selectedMachId, setSelectedMachId] = useState('');
    const [selectedProperty, setSelectedProperty] = useState('');
    const [filteredRec, setFilteredRec] = useState(rec);
    const [chartDataset, setChartDataset] = useState([]);

    const machIds = [...new Set(rec.map((item) => item.MachID))]
        .filter((machId) => machId !== null && machId !== undefined)
        .sort((a, b) => Number(a) - Number(b));
        
    const propertyOptions = Object.keys(rec[0] ?? {}).filter(
        (property) => ['MES_prs', 'NAU_prs', 'ON_Time_Occupation', 'Mach_Efficiency'].includes(property)
    );

    useEffect(() => {
        setFilteredRec(
            rec.filter((item) => String(item.MachID) === String(selectedMachId))
        );
    }, [rec, selectedMachId]);

    function handleMachIdChange(event) {
        setSelectedMachId(event.target.value);
    }

    function handlePropertyChange(event) {
        setSelectedProperty(event.target.value);
    }

    function handleGenChart(event) {
        event.preventDefault();
        let dataset = {};
        filteredRec.forEach((record) => {
            const [date, time] = record.Shift_Start_Time.trim().split(/\s+/);
            if (!dataset[date]) {
                dataset[date] = {};
            }
            const shift = time === "07:00:00" ? "Day" : "Night";
            dataset[date].date = date;
            dataset[date][shift] = Number(record[selectedProperty] ?? 0);
        });
        dataset = Object.values(dataset).sort((a, b) => a.date.localeCompare(b.date));
        setChartDataset(dataset);
    }

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="md"
        >
            <DialogTitle>Data Vis</DialogTitle>
            <DialogContent>
                <Box component="form" onSubmit={handleGenChart} sx={{ display: 'flex', gap: 2, pt: 1 }}>
                    <FormControl fullWidth required>
                        <InputLabel id="chart-machid-label">MachID</InputLabel>
                        <Select
                            labelId="chart-machid-label"
                            value={selectedMachId}
                            label="MachID"
                            required
                            onChange={handleMachIdChange}
                        >
                            {machIds.map((machId) => (
                                <MenuItem key={machId} value={machId}>
                                    {machId}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl fullWidth required>
                        <InputLabel id="chart-property-label">Property</InputLabel>
                        <Select
                            labelId="chart-property-label"
                            value={selectedProperty}
                            label="Property"
                            onChange={handlePropertyChange}
                        >
                            {propertyOptions.map((property) => (
                                <MenuItem key={property} value={property}>
                                    {property}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Button type='submit' variant="contained">Gen</Button>
                </Box>
                <LineBarChart chartDataset={chartDataset} />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}

export function SKUChartModal({ open, onClose, rec }) {
    const [selectedStyle, setSelectedStyle] = useState('');
    const [selectedProperty, setSelectedProperty] = useState('');
    const [filteredRec, setFilteredRec] = useState(rec);
    const [chartDataset, setChartDataset] = useState([]);

    const styles = [...new Set(rec.map((item) => item.Style_Code))]
        .filter((sku) => sku !== null && sku !== undefined)
        .sort((a, b) =>
            String(a).localeCompare(String(b), undefined, { numeric: true, sensitivity: 'base' })
        );

        
    const propertyOptions = Object.keys(rec[0] ?? {}).filter(
        (property) => ['MES_prs', 'NAU_prs', 'ON_Time_Occupation', 'Efficiency'].includes(property)
    );

    useEffect(() => {
        setFilteredRec(
            rec.filter((item) => String(item.Style_Code) === String(selectedStyle))
        );
    }, [rec, selectedStyle]);

    function handleStyleChange(event) {
        setSelectedStyle(event.target.value);
    }

    function handlePropertyChange(event) {
        setSelectedProperty(event.target.value);
    }

    function handleGenChart(event) {
        event.preventDefault();
        let dataset = {};
        filteredRec.forEach((record) => {
            const [date, time] = record.Shift_Start_Time.trim().split(/\s+/);
            if (!dataset[date]) {
                dataset[date] = {};
            }
            const shift = time === "07:00:00" ? "Day" : "Night";
            dataset[date].date = date;
            dataset[date][shift] = Number(record[selectedProperty] ?? 0);
        });
        dataset = Object.values(dataset).sort((a, b) => a.date.localeCompare(b.date));
        setChartDataset(dataset);
    }

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="md"
        >
            <DialogTitle>Data Vis</DialogTitle>
            <DialogContent>
                <Box component="form" onSubmit={handleGenChart} sx={{ display: 'flex', gap: 2, pt: 1 }}>
                    <FormControl fullWidth required>
                        <InputLabel id="chart-sku-label">Style</InputLabel>
                        <Select
                            labelId="chart-sku-label"
                            value={selectedStyle}
                            label="Style"
                            required
                            onChange={handleStyleChange}
                        >
                            {styles.map((style) => (
                                <MenuItem key={style} value={style}>
                                    {style}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <FormControl fullWidth required>
                        <InputLabel id="chart-property-label">Property</InputLabel>
                        <Select
                            labelId="chart-property-label"
                            value={selectedProperty}
                            label="Property"
                            onChange={handlePropertyChange}
                        >
                            {propertyOptions.map((property) => (
                                <MenuItem key={property} value={property}>
                                    {property}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Button type='submit' variant="contained">Gen</Button>
                </Box>
                <LineBarChart chartDataset={chartDataset} />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}

export function MachStopChartModal({ open, onClose, rec }) {

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="md"
        >
            <DialogTitle>Data Vis</DialogTitle>
            <DialogContent>
                <BarChart chartDataset={rec} />
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}


export function CodeStopChartModal({ open, onClose, rec_freq,  rec_mach, rec_dur_sum, rec_dur_med}) {
    const [selectedProperty, setSelectedProperty] = useState('');
    const [chartDataset, setChartDataset] = useState(null);

    const propertyOptions = [['Frequency', 'freq'], ['Mach Count', 'Mach_cnt'], ['Duration Sum', 'dur_sum'], ['Duration Median', 'dur_med']];

    function handlePropertyChange(event) {
        setSelectedProperty(event.target.value);
        setChartDataset(null);
    }

    function handleGenChart(event) {
        event.preventDefault();
        if(selectedProperty==='freq'){
            setChartDataset(rec_freq);
        }else if(selectedProperty==='Mach_cnt'){
            setChartDataset(rec_mach);
        }else if(selectedProperty==='dur_sum'){
            setChartDataset(rec_dur_sum);
        }else{
            setChartDataset(rec_dur_med);
        }    
    }

    return (
        <Dialog
            open={open}
            onClose={onClose}
            fullWidth
            maxWidth="lg"
        >
            <DialogTitle>Data Vis</DialogTitle>
            <DialogContent>
                <Box component="form" onSubmit={handleGenChart} sx={{ display: 'flex', gap: 2, pt: 1 }}>
                    <FormControl fullWidth required>
                        <InputLabel id="chart-property-label">Property</InputLabel>
                        <Select
                            labelId="chart-property-label"
                            value={selectedProperty}
                            label="Property"
                            onChange={handlePropertyChange}
                        >
                            {propertyOptions.map((property) => (
                                <MenuItem key={property[0]} value={property[1]}>
                                    {property[0]}
                                </MenuItem>
                            ))}
                        </Select>
                    </FormControl>
                    <Button type='submit' variant="contained">Gen</Button>
                </Box>
                {chartDataset && <BarChart1 chartDataset={chartDataset} property={selectedProperty}/>}
            </DialogContent>
            <DialogActions>
                <Button onClick={onClose}>Close</Button>
            </DialogActions>
        </Dialog>
    );
}