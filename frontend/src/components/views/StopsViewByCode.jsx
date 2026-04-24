import { useState } from 'react';
import axios from 'axios';

import TableView from "./TableView";
import { CodeStopTableModal } from "../modals/TableModal";
import { formatSeconds, minuteFilterOperators } from "../utils";

function StopsViewByCode() {
    const [tableOpen, setTableOpen] = useState(false);
    const [modalRec, setModalRec] = useState(null);
    const [contentRec, setContentRec] = useState([]);
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
            field: 'dur_minute_sum',
            headerName: 'Duration (SUM)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
        {
            field: 'dur_minute_med',
            headerName: 'Duration (Medium)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
        
    ];

    function handleRowClick(params){
        //console.log("clicked row:", params.row);
        axios.get(`http://localhost:8000/base/stop/code/detail?start=${time.start}&end=${time.end}&shift=${time.shift}&stop_code=${params.row.Stop_code}`).then(
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
        const promise = axios.get("http://localhost:8000/base/stop/code", {
                            params: {
                                start,
                                end,
                                shift,
                            },
                        }).then((resp) => {
                            const records = resp.data.content ?? [];
                            setContentRec(records);
                        }).catch((err) => {
                            setContentRec([]);
                            console.error(err);
                            throw new Error("Failed to load mach data");
                        });
        return promise;
    }


    return (
        <>
            <TableView col={columns} rec={contentRec} loadData={loadData} handleRowClick={handleRowClick} markDownSelectedTime={setTime}/>
            {(tableOpen && modalRec) ? <CodeStopTableModal open={tableOpen} 
                                                          onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                                          rec={modalRec}
                                                          metaData={metaData}/> : null}
        </>
    );
}

export default StopsViewByCode;