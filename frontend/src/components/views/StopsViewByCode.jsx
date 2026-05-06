import { useState } from 'react';
import axios from 'axios';

import TableView from "./TableView";
import { CodeStopTableModal } from "../modals/TableModal";
import { CodeStopChartModal } from '../modals/ChartModal';
import { formatSeconds, minuteFilterOperators } from "../utils";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function StopsViewByCode() {
    const [tableOpen, setTableOpen] = useState(false);
    const [chartOpen, setChartOpen] = useState(false); 
    const [modalRec, setModalRec] = useState(null);
    const [contentRec, setContentRec] = useState([]);
    const [chartFreqRec, setChartFreqRec] = useState(null);
    const [chartMachRec, setChartMachRec] = useState(null);
    const [chartDurSumRec, setChartDurSumRec] = useState(null);
    const [chartDurMedRec, setChartDurMedRec] = useState(null);
    const [time, setTime] = useState({})
    const [metaData, setMetaData] = useState({});

    const columns = [
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
            field: 'freq',
            headerName: 'Frequency',
            flex: 1,
            type: 'number',
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
            headerName: 'Duration (Medium)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
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
        axios.get(`${API_BASE_URL}/base/stop/code/detail?start=${time.start}&end=${time.end}&shift=${time.shift}&stop_code=${params.row.Stop_code}`).then(
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
        setMetaData({stop_code: params.row.Stop_code})
    }

    function loadData(start, end, shift) {
        const promise = axios.get(`${API_BASE_URL}/base/stop/code`, {
                            params: {
                                start,
                                end,
                                shift,
                            },
                        }).then((resp) => {
                            const content = resp.data.content ?? [];
                            const chart_freq = resp.data.chart_freq ?? [];
                            const chart_mach = resp.data.chart_mach ?? [];
                            const chart_dur_sum = resp.data.chart_dur_sum ?? [];
                            const chart_dur_med = resp.data.chart_dur_med ?? [];
                            setContentRec(content);
                            setChartFreqRec(chart_freq);
                            setChartMachRec(chart_mach);
                            setChartDurSumRec(chart_dur_sum);
                            setChartDurMedRec(chart_dur_med);
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
            {(tableOpen && modalRec) ? <CodeStopTableModal open={tableOpen} 
                                                          onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                                          rec={modalRec}
                                                          metaData={metaData}/> : null}
            {chartOpen ? (<CodeStopChartModal open={chartOpen} 
                                            onClose={handleCloseChart}  
                                            rec_freq={chartFreqRec}
                                            rec_mach={chartMachRec}
                                            rec_dur_sum={chartDurSumRec}
                                            rec_dur_med={chartDurMedRec}/>) : null}
        </>
    );
}

export default StopsViewByCode;