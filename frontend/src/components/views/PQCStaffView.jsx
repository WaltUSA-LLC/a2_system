import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView";
import { PQCStaffDetailTableModal } from '../modals/TableModal';
import { formatSeconds, minuteFilterOperators, renderHeaderWithUnit } from "../utils";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function PQCStaffView() {
    const [contentRec, setContentRec] = useState([]);
    const [modalRec, setModalRec] = useState(null);
    const [tableOpen, setTableOpen] = useState(false);
    const [metaData, setMetaData] = useState({});

    const columns = [
        {
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
            flex: 2,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Name',
            headerName: 'Name',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Role',
            headerName: 'Role',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'pqc_cnt',
            headerName: 'Checks',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Check Counting',
        },
        {
            field: 'start_check',
            headerName: 'Start',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
            description: '1st Check Time'
        },
        {
            field: 'end_check',
            headerName: 'End',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
            description: 'Last Check Time'
        },
        {
            field: 'avg_adj_diff',
            headerName: 'Freq',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => {
                if (value == "NaT") return '';
                return formatSeconds(value);
            },
            filterOperators: minuteFilterOperators,
        },
        {
            field: 'defects',
            renderHeader: (params) => renderHeaderWithUnit('Defect', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Total Defects',
        },
        {
            field: 'toeHole',
            renderHeader: () => renderHeaderWithUnit('Hole', 'PCS'),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'brokenNDL',
            renderHeader: (params) => renderHeaderWithUnit('N-Brok', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Broken',
        },
        {
            field: 'missNDL',
            renderHeader: (params) => renderHeaderWithUnit('N-Miss', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Needle Missing',
        },
        {
            field: 'missYarn',
            renderHeader: (params) => renderHeaderWithUnit('Y-Miss', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Miss',
        },
        {
            field: 'fanYarn',
            renderHeader: (params) => renderHeaderWithUnit('Y-Rtn', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Misplace',
        },
        {
            field: 'feisha',
            renderHeader: (params) => renderHeaderWithUnit('Y-Fly', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Yarn Fly',
        },
        {
            field: 'logoIssue',
            renderHeader: (params) => renderHeaderWithUnit('Logo', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            description: 'Logo Issue',
        },
        {
            field: 'dirty',
            headerName: 'Stain (PCS)',
            renderHeader: (params) => renderHeaderWithUnit('Stain', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'other',
            renderHeader: (params) => renderHeaderWithUnit('Other', 'PCS', params.colDef.description),
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
        
    ];

    function handleRowClick(params){
        //console.log("clicked row:", params.row);
        const [date, shift_time] = params.row.Shift_Start_Time.split(/\s+/);
        const shift = shift_time==="07:00:00"? 1 : 2;
        const name = params.row.Name;
        //console.log(date);
        //console.log(shift);
        axios.get(`${API_BASE_URL}/base/pqc/staff/detail?start=${date}&shift=${shift}&name=${name}`).then(
            resp => {
                const records = resp.data.content ?? [];
                setModalRec(records);
                setMetaData({date_time: params.row.Shift_Start_Time, 
                    name: name,
                    role: params.row.Role,})
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
        const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
        const promise = axios.get(`${API_BASE_URL}/base/pqc/staff`, {
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
            <TableView col={columns} rec={contentRec} loadData={loadData} handleRowClick={handleRowClick}/>
            {(tableOpen && modalRec) ? <PQCStaffDetailTableModal open={tableOpen} 
                                                    onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                                    rec={modalRec} 
                                                    metaData={metaData}/> : null}
        </>
    );
}

export default PQCStaffView;

