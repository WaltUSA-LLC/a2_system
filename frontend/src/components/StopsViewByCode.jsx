import { GridFilterInputValue } from "@mui/x-data-grid";
import BaseTableView from "./BaseTableView"
import { formatSeconds } from "./utils";

function StopsViewByCode() {
    const minuteFilterOperators = [
        {
            label: "minutes =",
            value: "minutesEquals",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) === target;
            },
        },
        {
            label: "minutes >=",
            value: "minutesGreaterOrEqualThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) >= target;
            },
        },
        {
            label: "minutes <=",
            value: "minutesLessOrEqualThan",
            InputComponent: GridFilterInputValue,
            getApplyFilterFn: (filterItem) => {
            if (filterItem.value == null || filterItem.value === "") return null;
            const target = Number(filterItem.value) * 60;
            return (value) => Number(value) <= target;
            },
        },
    ];

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
            field: 'Mach_cnt',
            headerName: 'Mach Count',
            flex: 1,
            type: 'number',
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
    return (
        <BaseTableView url="http://localhost:8000/base/stop/code" col={columns}/>
    );
}

export default StopsViewByCode;