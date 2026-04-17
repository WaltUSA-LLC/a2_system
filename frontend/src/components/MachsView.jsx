import BaseTableView from "./BaseTableView"
import { GridFilterInputValue } from "@mui/x-data-grid";
import { formatSeconds } from "./utils";

function MachsView() {
    const hourFilterOperators = [
        {
            label: "hours =",
            value: "hoursEquals",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 3600;
            return (value) => Number(value) === target;
            },
        },
        {
            label: "hours >",
            value: "hoursGreaterThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 3600;
            return (value) => Number(value) > target;
            },
        },
        {
            label: "hours <",
            value: "hoursLessThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 3600;
            return (value) => Number(value) < target;
            },
        },
    ];

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
            field: 'Shift_Start_Time',
            headerName: 'Shift Start Time',
            flex: 1,
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
            field: 'Weight',
            headerName: 'Weight (kg)',
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
            field: "ON_Time",
            headerName: "ON Time",
            type: 'number',
            flex: 1,
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: hourFilterOperators,
        },
        {
            field: "OFF_Time",
            headerName: "OFF Time",
            type: 'number',
            flex: 1,
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: hourFilterOperators,
        },
        {
            field: 'ON_Time_Occupation',
            headerName: 'ON Time (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            valueFormatter: (value) => `${value.toFixed(1)}%`,
        },
        {
            field: 'Mach_Efficiency',
            headerName: 'Mach Eff (%)',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueGetter: (value) => value * 100,
            valueFormatter: (value) => `${value.toFixed(1)}%`,
        },
        {
            field: 'Comment',
            headerName: 'Comment',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
    ];

    
    return (
        <BaseTableView url="http://localhost:8000/base/mach" col={columns}/>
    );
}

export default MachsView;

