import { GridFilterInputValue } from "@mui/x-data-grid";
import TableView from "./TableView"
import { formatSeconds } from "./utils";

function StopsView() {
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
            field: 'Start_Shift_Time',
            headerName: 'Start Shift Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'Stop_time',
            headerName: 'Stop Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'MachID',
            headerName: 'Mach ID',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
        },
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
            field: 'Recover_time',
            headerName: 'Recover Time',
            flex: 1,
            type: 'string',
            align: 'center',
            headerAlign: 'center',
        },
        {
            field: 'dur_minute',
            headerName: 'Duration',
            flex: 1,
            type: 'number',
            align: 'center',
            headerAlign: 'center',
            valueFormatter: (value) => formatSeconds(value),
            filterOperators: minuteFilterOperators,
        },
        
    ];
    return (
        <TableView url="http://localhost:8000/base/stop" col={columns}/>
    );
}

export default StopsView;