import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView"
import { ShiftChartModal } from '../modals/ChartModal';
import { MachDetailTableModal } from '../modals/TableModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function ShiftView() {
    const [contentRec, setContentRec] = useState([]);
    const [modalRec, setModalRec] = useState(null);
    const [chartOpen, setChartOpen] = useState(false); 
    const [tableOpen, setTableOpen] = useState(false);
    const [metaData, setMetaData] = useState({});

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

    function handleRowClick(params){
        //console.log("clicked row:", params.row);
        const [date, shift_time] = params.row.Shift_Start_Time.split(/\s+/);
        const shift = shift_time==="07:00:00"? 1 : 2;
        //console.log(date);
        //console.log(shift);
        axios.get(`${API_BASE_URL}/base/shift/detail?start=${date}&shift=${shift}`).then(
            resp => {
                const records = resp.data.content ?? [];
                setModalRec(records);
            }
        ).catch((err) => {
            console.error(err);
            setModalRec([]);
            setTableOpen(false);
            return;
        });
        setTableOpen(true);
        setMetaData({date_time: params.row.Shift_Start_Time})
    }

    function loadData(start, end, shift) {
        const promise = axios.get(`${API_BASE_URL}/base/shift`, {
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
            <TableView col={columns} rec={contentRec} loadData={loadData} handleOpenChart={handleOpenChart} handleRowClick={handleRowClick}/>
            {chartOpen ? (<ShiftChartModal open={chartOpen} onClose={handleCloseChart} rec={contentRec} />) : null}
            {(tableOpen && modalRec) ? <MachDetailTableModal open={tableOpen} 
                                        onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                        rec={modalRec} 
                                        metaData={metaData}/> : null}
        </>
    );
}

export default ShiftView;

