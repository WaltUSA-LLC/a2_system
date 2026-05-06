import { useState } from 'react';
import axios from 'axios';

import TableView from "./TableView"
import { MachStopTableModal } from "../modals/TableModal";
import { MachStopChartModal } from '../modals/ChartModal';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function StopsViewByMach() {
    const [tableOpen, setTableOpen] = useState(false);
    const [chartOpen, setChartOpen] = useState(false); 
    const [chartRec, setChartRec] = useState(null);
    const [modalRec, setModalRec] = useState(null);
    const [contentRec, setContentRec] = useState([]);
    const [time, setTime] = useState({})
    const [metaData, setMetaData] = useState({});

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
            field: 'freq',
            headerName: 'Frequency',
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
        axios.get(`${API_BASE_URL}/base/stop/mach/detail?start=${time.start}&end=${time.end}&shift=${time.shift}&mach=${params.row.MachID}&style=${params.row.Style_Code}`).then(
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
        setMetaData({mach:params.row.MachID, style:params.row.Style_Code})
    }

    function loadData(start, end, shift) {
        const promise = axios.get(`${API_BASE_URL}/base/stop/mach`, {
                            params: {
                                start,
                                end,
                                shift,
                            },
                        }).then((resp) => {
                            const records = resp.data.content ?? [];
                            const charRecords = resp.data.chart ?? [];
                            setContentRec(records);
                            setChartRec(charRecords);
                        }).catch((err) => {
                            setContentRec([]);
                            console.error(err);
                            throw new Error("Failed to load mach data");
                        });
        return promise;
    }
    
    return (
        <>
            <TableView col={columns} rec={contentRec} loadData={loadData} handleOpenChart={handleOpenChart} handleRowClick={handleRowClick} markDownSelectedTime={setTime}/>
            {(tableOpen && modalRec) ? <MachStopTableModal open={tableOpen} onClose={()=>{setTableOpen(false); setModalRec(null)}} rec={modalRec} metaData={metaData}/> : null}
            {chartOpen ? (<MachStopChartModal open={chartOpen} onClose={handleCloseChart} rec={chartRec} />) : null}
        </>
    );
}

export default StopsViewByMach;