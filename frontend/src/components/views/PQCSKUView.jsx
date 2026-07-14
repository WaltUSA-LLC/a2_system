import { useState } from 'react';
import axios from "axios";

import TableView from "./TableView";
import { PQCSKUDetailTableModal } from '../modals/TableModal';
import { renderHeaderWithUnit } from "../utils";
import { DAY_SHIFT_START } from "../../constants";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;

function PQCSKUView() {
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
            field: 'Style_Code',
            headerName: 'Style Code',
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
            headerName: 'Stain',
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
        const shift = shift_time === DAY_SHIFT_START ? 1 : 2;
        const style = params.row.Style_Code;
        //console.log(date);
        //console.log(shift);
        axios.get(`${API_BASE_URL}/base/pqc/sku/detail?start=${date}&shift=${shift}&style=${style}`).then(
            resp => {
                const records = resp.data.content ?? [];
                setModalRec(records);
                setMetaData({date_time: params.row.Shift_Start_Time, 
                    style: style,});
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
        const promise = axios.get(`${API_BASE_URL}/base/pqc/sku`, {
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
            <TableView col={columns} rec={contentRec} loadData={loadData} handleRowClick={handleRowClick} hasChart={false}/>
            {(tableOpen && modalRec) ? <PQCSKUDetailTableModal open={tableOpen} 
                                                                onClose={()=>{setTableOpen(false); setModalRec(null)}} 
                                                                rec={modalRec} 
                                                                metaData={metaData}/> : null}
        </>
    );
}

export default PQCSKUView;

