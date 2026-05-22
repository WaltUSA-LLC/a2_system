import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView";
import { SKUChartModal } from '../modals/ChartModal';
import { MachDetailTableModal } from '../modals/TableModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function SKUView() {
    const [contentRec, setContentRec] = useState([]);
    const [modalRec, setModalRec] = useState(null);
    const [chartOpen, setChartOpen] = useState(false); 
    const [tableOpen, setTableOpen] = useState(false);
    const [metaData, setMetaData] = useState({});

    const columns = [
        {
            field: 'Style_Code',
            headerName: 'Style Code',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
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
            field: 'Efficiency',
            headerName: 'Mach Eff (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value == null ? null : value * 100,
            valueFormatter: (value) => value == null ? '' : `${value.toFixed(1)}%`,
        },
        {
            field: 'Mach_cnt',
            headerName: 'Mach Count',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
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
        axios.get(`${API_BASE_URL}/base/sku/detail?start=${date}&end=${date}&shift=${shift}&style=${params.row.Style_Code}`).then(
            resp => {
                const records = resp.data.content ?? [];
                const staff = resp.data.staff ?? [];
                setModalRec(records);
                setMetaData({date_time: params.row.Shift_Start_Time, 
                    style:params.row.Style_Code,
                    ko: staff[0].KO ? staff[0].KO : "None", 
                    tech: staff[0].Tech ? staff[0].Tech : "None", 
                    creeler: staff[0].Creeler ? staff[0].Creeler : "None", 
                    yarner: staff[0].Yarner ? staff[0].Yarner : "None"
                })
            }
        ).catch((err) => {
            console.error(err);
            setModalRec([]);
            setTableOpen(false);
            return;
        });
        setTableOpen(true);
    }

    function loadData(start, end, shift) {
        const promise = axios.get(`${API_BASE_URL}/base/sku`, {
                            params: {
                                start,
                                end,
                                shift,
                            },
                        }).then((resp) => {
                            const records = resp.data.content ?? [];
                            setContentRec(records);
                        }).catch((err) => {
                            setChartOpen(false);
                            setContentRec([]);
                            console.error(err);
                            throw new Error("Failed to load mach data");
                        });
        return promise;
    }

    return (
        <>
            <TableView col={columns} rec={contentRec} loadData={loadData} handleOpenChart={handleOpenChart} handleRowClick={handleRowClick}/>
            { chartOpen ? (
                <SKUChartModal open={chartOpen} onClose={handleCloseChart} rec={contentRec} />) : 
                null}
            {(tableOpen && modalRec) ? <MachDetailTableModal open={tableOpen} 
                                        onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                        rec={modalRec} 
                                        metaData={metaData}/> : null}
        </>
    );
}

export default SKUView;