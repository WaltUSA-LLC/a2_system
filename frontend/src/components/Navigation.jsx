import { Link } from "react-router-dom";
import "./Navigation.css";

function Navigation() {
    return (
        <div className="nav">
            <Link to="/machs-view">View Machs</Link>
            <Link to="/shift-view">View Shift</Link>
            <Link to="/sku-view">View SKU</Link>
            <Link to="/stops-view/mach">View Stops (by mach)</Link>
            <Link to="/stops-view/code">View Stops (by code)</Link>
        </div>
    );
}

export default Navigation;