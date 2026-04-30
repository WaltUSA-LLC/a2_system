import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView"
import { ShiftChartModal } from '../modals/ChartModal';

function ShiftView() {
    const [contentRec, setContentRec] = useState([]);
    const [chartOpen, setChartOpen] = useState(false); 

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
            field: 'Mach_cnt',
            headerName: 'Mach Count',
            flex: 1,
            type: 'number',
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
            field: 'ST_prs',
            headerName: 'ST (prs)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'eff',
            headerName: 'Mach Eff (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            valueFormatter: (value) => `${value.toFixed(1)}%`,
        },
        {
            field: 'Time_Occupation',
            headerName: 'ON Time (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            valueFormatter: (value) => `${value.toFixed(1)}%`,
        },
        
        
    ];

    function handleOpenChart() {
        setChartOpen(true);
    }

    function handleCloseChart() {
        setChartOpen(false);
    }

    function loadData(start, end, shift) {
        const promise = axios.get("http://localhost:8000/base/shift", {
                            params: {
                                start,
                                end,
                                shift,
                            },
                        }).then((resp) => {
                            const records = resp.data.content ?? [];
                            setContentRec(records);
                        }).catch((err) => {
                            //setChartOpen(false);
                            setContentRec([]);
                            console.error(err);
                            throw new Error("Failed to load mach data");
                        });
        return promise;
    }

    return (
        <>
            <TableView col={columns} rec={contentRec} loadData={loadData} handleOpenChart={handleOpenChart}/>
            {chartOpen ? (<ShiftChartModal open={chartOpen} onClose={handleCloseChart} rec={contentRec} />) : null}
        </>
    );
}

export default ShiftView;

