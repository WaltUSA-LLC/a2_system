import { useState } from 'react'
import { Link as RouterLink } from "react-router-dom";
import { AppBar, Toolbar, Typography, Stack, Button, Menu, MenuItem } from '@mui/material'
import KeyboardArrowDownIcon from '@mui/icons-material/KeyboardArrowDown'
import photo from "../assets/sock.png";

function TopBar() {
    const [anchorEl, setAnchorEl] = useState();

    function handleClick(event){
        setAnchorEl(event.currentTarget);
    }

    function handleClose(){
        setAnchorEl(null);
    }

    return (
        <AppBar position='static' sx={{backgroundColor: "primary.light"}}>
            <Toolbar>
                <img
                    src={photo}
                    alt="SockSight"
                    style={{
                        width: 38,
                        height: 38,
                        objectFit: "cover",
                        marginRight: 8,
                    }}
                />
                <Typography 
                    variant='h4' 
                    component='div' 
                    sx={{ flexGrow: 1, 
                        fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
                        fontSize: '1.8rem',
                        fontWeight: 700,
                        letterSpacing: 0,
                        lineHeight: 1.2,}}
                >
                    SockSight
                </Typography>
                <Stack 
                    direction='row' 
                    spacing={2}
                    sx={{
                        '& .MuiButton-root': {
                            fontSize: '1rem',
                            fontWeight: 600,
                            textTransform: 'none',
                            letterSpacing: 0,
                        },
                    }}
                >
                    <Button color='inherit' component={RouterLink} to="/shift-view">
                        Shift
                    </Button>
                    <Button color='inherit' component={RouterLink} to="/sku-view">
                        SKU
                    </Button>
                    <Button
                        color='inherit'
                        endIcon={<KeyboardArrowDownIcon />}
                        onClick={handleClick}
                    >
                        Stop
                    </Button>
                </Stack>
                <Menu
                    anchorEl={anchorEl}
                    open={Boolean(anchorEl)}
                    onClose={handleClose}
                    anchorOrigin={{
                        vertical: 'bottom',
                        horizontal: 'right'
                    }}
                    transformOrigin={{
                        vertical: 'top',
                        horizontal: 'right'
                    }}
                    sx={{
                        '& .MuiMenuItem-root': {
                            fontSize: '1rem',
                            fontWeight: 600,
                            letterSpacing: 0,
                        },
                    }}
                >
                    <MenuItem component={RouterLink} to="/stops-view/mach" onClick={handleClose}>By Mach</MenuItem>
                    <MenuItem component={RouterLink} to="/stops-view/code" onClick={handleClose}>By Code</MenuItem>
                </Menu>
            </Toolbar>
        </AppBar>
    );
}

export default TopBar;